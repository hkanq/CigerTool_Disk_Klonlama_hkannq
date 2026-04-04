using System.Diagnostics;
using System.IO.Compression;
using CigerTool.Application.Models;

namespace CigerTool.Infrastructure.Common;

internal sealed class SmartCloneFileSystemExecutor
{
    private const int BufferSize = 1024 * 1024;

    public async Task<SmartCloneExecutionResult> MirrorAsync(
        string sourceRoot,
        string targetRoot,
        IProgress<OperationProgressSnapshot>? progress,
        CancellationToken cancellationToken)
    {
        var warnings = new List<string>();
        var scan = ScanSource(sourceRoot, warnings, cancellationToken);
        var stopwatch = Stopwatch.StartNew();

        progress?.Report(OperationProgressFactory.Create(
            "Hazırlık",
            "Hedef sürücü temizleniyor.",
            0,
            Math.Max(1, scan.TotalBytes),
            stopwatch,
            targetRoot,
            isIndeterminate: true));

        ClearTargetRoot(targetRoot, warnings, cancellationToken);

        foreach (var directory in scan.Directories)
        {
            cancellationToken.ThrowIfCancellationRequested();
            Directory.CreateDirectory(Path.Combine(targetRoot, directory));
        }

        long processedBytes = 0;
        var copiedItems = 0;

        foreach (var file in scan.Files)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var sourcePath = Path.Combine(sourceRoot, file.RelativePath);
            var targetPath = Path.Combine(targetRoot, file.RelativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(targetPath)!);

            try
            {
                await using var sourceStream = new FileStream(sourcePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, BufferSize, useAsync: true);
                await using var targetStream = new FileStream(targetPath, FileMode.Create, FileAccess.Write, FileShare.None, BufferSize, useAsync: true);

                processedBytes += await CopyFileWithProgressAsync(
                    sourceStream,
                    targetStream,
                    file.Length,
                    scan.TotalBytes,
                    processedBytes,
                    progress,
                    stopwatch,
                    file.RelativePath,
                    cancellationToken);

                copiedItems++;
                ApplyMetadata(sourcePath, targetPath, warnings);
            }
            catch (Exception ex)
            {
                warnings.Add($"{file.RelativePath}: {ex.Message}");
            }
        }

        progress?.Report(OperationProgressFactory.Create(
            "Tamamlandı",
            warnings.Count == 0 ? "Akıllı kopya tamamlandı." : "Akıllı kopya uyarılarla tamamlandı.",
            processedBytes,
            scan.TotalBytes,
            stopwatch));

        return new SmartCloneExecutionResult(processedBytes, scan.TotalBytes, copiedItems, warnings);
    }

    public static IReadOnlyList<FilePackageEntry> ScanFilesForPackaging(string sourceRoot, List<string> warnings, CancellationToken cancellationToken)
    {
        return ScanSource(sourceRoot, warnings, cancellationToken).Files;
    }

    public async Task<long> WriteFileSetToZipAsync(
        string sourceRoot,
        ZipArchive archive,
        IReadOnlyList<FilePackageEntry> files,
        long totalBytes,
        IProgress<OperationProgressSnapshot>? progress,
        CancellationToken cancellationToken)
    {
        var stopwatch = Stopwatch.StartNew();
        long processedBytes = 0;

        foreach (var file in files)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var sourcePath = Path.Combine(sourceRoot, file.RelativePath);
            var entryPath = $"files/{file.RelativePath.Replace('\\', '/')}";
            var entry = archive.CreateEntry(entryPath, CompressionLevel.SmallestSize);

            await using var sourceStream = new FileStream(sourcePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, BufferSize, useAsync: true);
            await using var entryStream = entry.Open();

            processedBytes += await CopyFileWithProgressAsync(
                sourceStream,
                entryStream,
                file.Length,
                totalBytes,
                processedBytes,
                progress,
                stopwatch,
                file.RelativePath,
                cancellationToken);
        }

        return processedBytes;
    }

    public async Task<SmartCloneExecutionResult> RestoreFileSetFromZipAsync(
        ZipArchive archive,
        string targetRoot,
        IProgress<OperationProgressSnapshot>? progress,
        CancellationToken cancellationToken)
    {
        var warnings = new List<string>();
        var fileEntries = archive.Entries
            .Where(entry => entry.FullName.StartsWith("files/", StringComparison.OrdinalIgnoreCase) && !string.IsNullOrEmpty(entry.Name))
            .Select(entry => new FilePackageEntry(entry.FullName["files/".Length..].Replace('/', Path.DirectorySeparatorChar), entry.Length))
            .ToArray();
        var totalBytes = fileEntries.Sum(entry => entry.Length);
        var stopwatch = Stopwatch.StartNew();
        long processedBytes = 0;
        var copiedItems = 0;

        ClearTargetRoot(targetRoot, warnings, cancellationToken);

        foreach (var file in fileEntries)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var sourceEntry = archive.GetEntry($"files/{file.RelativePath.Replace('\\', '/')}")!;
            var targetPath = Path.Combine(targetRoot, file.RelativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(targetPath)!);

            try
            {
                await using var sourceStream = sourceEntry.Open();
                await using var targetStream = new FileStream(targetPath, FileMode.Create, FileAccess.Write, FileShare.None, BufferSize, useAsync: true);

                processedBytes += await CopyFileWithProgressAsync(
                    sourceStream,
                    targetStream,
                    sourceEntry.Length,
                    totalBytes,
                    processedBytes,
                    progress,
                    stopwatch,
                    file.RelativePath,
                    cancellationToken);
                copiedItems++;
            }
            catch (Exception ex)
            {
                warnings.Add($"{file.RelativePath}: {ex.Message}");
            }
        }

        return new SmartCloneExecutionResult(processedBytes, totalBytes, copiedItems, warnings);
    }

    private static SourceScanResult ScanSource(string sourceRoot, List<string> warnings, CancellationToken cancellationToken)
    {
        var directories = new List<string>();
        var files = new List<FilePackageEntry>();
        long totalBytes = 0;

        void Walk(string absoluteDirectory)
        {
            cancellationToken.ThrowIfCancellationRequested();

            IEnumerable<string> subDirectories;
            try
            {
                subDirectories = Directory.EnumerateDirectories(absoluteDirectory);
            }
            catch (Exception ex)
            {
                warnings.Add($"{absoluteDirectory}: {ex.Message}");
                return;
            }

            foreach (var subDirectory in subDirectories)
            {
                cancellationToken.ThrowIfCancellationRequested();
                try
                {
                    var attributes = File.GetAttributes(subDirectory);
                    if (attributes.HasFlag(FileAttributes.ReparsePoint))
                    {
                        warnings.Add($"{Path.GetRelativePath(sourceRoot, subDirectory)}: yeniden yönlendirme noktası atlandı.");
                        continue;
                    }

                    var relativeDirectory = Path.GetRelativePath(sourceRoot, subDirectory);
                    directories.Add(relativeDirectory);
                    Walk(subDirectory);
                }
                catch (Exception ex)
                {
                    warnings.Add($"{Path.GetRelativePath(sourceRoot, subDirectory)}: {ex.Message}");
                }
            }

            IEnumerable<string> discoveredFiles;
            try
            {
                discoveredFiles = Directory.EnumerateFiles(absoluteDirectory);
            }
            catch (Exception ex)
            {
                warnings.Add($"{absoluteDirectory}: {ex.Message}");
                return;
            }

            foreach (var file in discoveredFiles)
            {
                cancellationToken.ThrowIfCancellationRequested();
                try
                {
                    var info = new FileInfo(file);
                    if ((info.Attributes & FileAttributes.ReparsePoint) == FileAttributes.ReparsePoint)
                    {
                        warnings.Add($"{Path.GetRelativePath(sourceRoot, file)}: yeniden yönlendirme noktası atlandı.");
                        continue;
                    }

                    files.Add(new FilePackageEntry(Path.GetRelativePath(sourceRoot, file), info.Length));
                    totalBytes += info.Length;
                }
                catch (Exception ex)
                {
                    warnings.Add($"{Path.GetRelativePath(sourceRoot, file)}: {ex.Message}");
                }
            }
        }

        Walk(sourceRoot);
        return new SourceScanResult(directories, files, totalBytes);
    }

    private static void ClearTargetRoot(string targetRoot, List<string> warnings, CancellationToken cancellationToken)
    {
        foreach (var entry in Directory.EnumerateFileSystemEntries(targetRoot))
        {
            cancellationToken.ThrowIfCancellationRequested();

            try
            {
                DeleteEntry(entry);
            }
            catch (Exception ex)
            {
                warnings.Add($"{entry}: {ex.Message}");
            }
        }
    }

    private static void DeleteEntry(string path)
    {
        var attributes = File.GetAttributes(path);
        if (attributes.HasFlag(FileAttributes.ReadOnly))
        {
            File.SetAttributes(path, attributes & ~FileAttributes.ReadOnly);
        }

        if (attributes.HasFlag(FileAttributes.Directory) && !attributes.HasFlag(FileAttributes.ReparsePoint))
        {
            Directory.Delete(path, recursive: true);
            return;
        }

        if (attributes.HasFlag(FileAttributes.Directory))
        {
            Directory.Delete(path);
            return;
        }

        File.Delete(path);
    }

    private static void ApplyMetadata(string sourcePath, string targetPath, List<string> warnings)
    {
        try
        {
            var sourceInfo = new FileInfo(sourcePath);
            File.SetCreationTimeUtc(targetPath, sourceInfo.CreationTimeUtc);
            File.SetLastWriteTimeUtc(targetPath, sourceInfo.LastWriteTimeUtc);
            File.SetAttributes(targetPath, sourceInfo.Attributes);
        }
        catch (Exception ex)
        {
            warnings.Add($"{Path.GetFileName(targetPath)}: öznitelikler taşınamadı ({ex.Message}).");
        }
    }

    private static async Task<long> CopyFileWithProgressAsync(
        Stream source,
        Stream target,
        long fileLength,
        long grandTotal,
        long alreadyProcessed,
        IProgress<OperationProgressSnapshot>? progress,
        Stopwatch stopwatch,
        string currentItem,
        CancellationToken cancellationToken)
    {
        var buffer = new byte[BufferSize];
        long copied = 0;

        while (copied < fileLength)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var requested = (int)Math.Min(buffer.Length, fileLength - copied);
            var read = await source.ReadAsync(buffer.AsMemory(0, requested), cancellationToken);
            if (read == 0)
            {
                break;
            }

            await target.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
            copied += read;

            progress?.Report(OperationProgressFactory.Create(
                "Akıllı kopya",
                "Dosyalar hedef sürücüye taşınıyor.",
                alreadyProcessed + copied,
                grandTotal,
                stopwatch,
                currentItem));
        }

        await target.FlushAsync(cancellationToken);
        return copied;
    }

    private sealed record SourceScanResult(
        IReadOnlyList<string> Directories,
        IReadOnlyList<FilePackageEntry> Files,
        long TotalBytes);
}

internal sealed record FilePackageEntry(string RelativePath, long Length);

internal sealed record SmartCloneExecutionResult(
    long ProcessedBytes,
    long TotalBytes,
    int CopiedItems,
    IReadOnlyList<string> Warnings);

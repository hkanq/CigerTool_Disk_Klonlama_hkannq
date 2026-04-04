using System.Diagnostics;
using CigerTool.Application.Models;

namespace CigerTool.Infrastructure.Common;

internal static class StreamCopyExecutor
{
    private const int BufferSize = 1024 * 1024;

    public static async Task<long> CopyAsync(
        Stream source,
        Stream target,
        long totalBytes,
        string phaseLabel,
        string summary,
        IProgress<OperationProgressSnapshot>? progress,
        CancellationToken cancellationToken,
        string? currentItem = null)
    {
        var buffer = new byte[BufferSize];
        long processedBytes = 0;
        var stopwatch = Stopwatch.StartNew();
        var lastReportAt = TimeSpan.Zero;

        progress?.Report(OperationProgressFactory.Create(phaseLabel, summary, 0, totalBytes, stopwatch, currentItem));

        while (processedBytes < totalBytes)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var requested = (int)Math.Min(buffer.Length, totalBytes - processedBytes);
            var read = await source.ReadAsync(buffer.AsMemory(0, requested), cancellationToken);
            if (read == 0)
            {
                throw new IOException("Kaynak akış beklenenden önce sona erdi.");
            }

            await target.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
            processedBytes += read;

            if (stopwatch.Elapsed - lastReportAt >= TimeSpan.FromMilliseconds(180) || processedBytes == totalBytes)
            {
                lastReportAt = stopwatch.Elapsed;
                progress?.Report(OperationProgressFactory.Create(phaseLabel, summary, processedBytes, totalBytes, stopwatch, currentItem));
            }
        }

        await target.FlushAsync(cancellationToken);
        progress?.Report(OperationProgressFactory.Create(phaseLabel, summary, processedBytes, totalBytes, stopwatch, currentItem));
        return processedBytes;
    }
}

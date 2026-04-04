using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Models;
using CigerTool.Infrastructure.Common;

namespace CigerTool.Infrastructure.Storage;

public sealed class RuntimeAppPathService(IEnvironmentProfileService environmentProfileService) : IAppPathService
{
    private ApplicationPaths? _cached;

    public ApplicationPaths GetPaths()
    {
        return _cached ??= ResolvePaths(environmentProfileService.GetCurrentProfile());
    }

    public static string GetCrashLogDirectory()
    {
        var profile = DetectFallbackProfile();
        return ResolvePaths(profile).LogDirectory;
    }

    private static ApplicationPaths ResolvePaths(AppEnvironmentProfile profile)
    {
        var baseDirectory = AppContext.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var localAppDataRoot = Path.Combine(
            System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData),
            "CigerTool");
        var commonAppDataRoot = Path.Combine(
            System.Environment.GetFolderPath(System.Environment.SpecialFolder.CommonApplicationData),
            "CigerTool");
        var tempRoot = Path.Combine(Path.GetTempPath(), "CigerTool");
        var systemTempRoot = ResolveSystemTempRoot();

        var preferServiceStorage = profile.IsWinPe || BuildFlavorDetector.IsWinPeFlavor();
        var preferredRoots = preferServiceStorage
            ? new[] { tempRoot, systemTempRoot, localAppDataRoot, commonAppDataRoot }
            : new[] { localAppDataRoot, commonAppDataRoot, tempRoot, systemTempRoot };

        var dataRoot = preferredRoots.First(TryEnsureWritableDirectory);
        var configDirectory = EnsureChildDirectory(dataRoot, "Config");
        var logDirectory = EnsureChildDirectory(dataRoot, "Logs");
        var cacheDirectory = EnsureChildDirectory(dataRoot, "Cache");
        var downloadsDirectory = EnsureChildDirectory(dataRoot, "Downloads");
        var toolsDirectory = ResolveToolsDirectory(baseDirectory);

        return new ApplicationPaths(
            BaseDirectory: baseDirectory,
            DataRoot: dataRoot,
            ConfigDirectory: configDirectory,
            LogDirectory: logDirectory,
            CacheDirectory: cacheDirectory,
            DownloadsDirectory: downloadsDirectory,
            ToolsDirectory: toolsDirectory,
            IsPortableMode: false,
            StorageModeLabel: DescribeStorageRoot(dataRoot, localAppDataRoot, commonAppDataRoot));
    }

    private static AppEnvironmentProfile DetectFallbackProfile()
    {
        var isWinPe = BuildFlavorDetector.IsWinPeFlavor() ||
                      System.Environment.SystemDirectory.StartsWith(@"X:\", StringComparison.OrdinalIgnoreCase);

        return new AppEnvironmentProfile(
            ProfileName: isWinPe ? "Servis ortamı" : "Masaüstü",
            IsWinPe: isWinPe,
            SupportsUsbCreation: true,
            SupportsLiveCloning: !isWinPe,
            Summary: isWinPe
                ? "Geçici sistem alanında çalışan servis profili."
                : "Windows kullanıcı verileri altında çalışan masaüstü profili.");
    }

    private static string ResolveSystemTempRoot()
    {
        var systemRoot = System.Environment.GetEnvironmentVariable("SystemRoot");
        return string.IsNullOrWhiteSpace(systemRoot)
            ? Path.Combine(Path.GetTempPath(), "CigerTool")
            : Path.Combine(systemRoot, "Temp", "CigerTool");
    }

    private static string DescribeStorageRoot(string dataRoot, string localAppDataRoot, string commonAppDataRoot)
    {
        if (string.Equals(dataRoot, localAppDataRoot, StringComparison.OrdinalIgnoreCase))
        {
            return "Windows kullanıcı verileri";
        }

        if (string.Equals(dataRoot, commonAppDataRoot, StringComparison.OrdinalIgnoreCase))
        {
            return "Windows ortak uygulama verileri";
        }

        return "Geçici sistem alanı";
    }

    private static bool TryEnsureWritableDirectory(string directory)
    {
        try
        {
            Directory.CreateDirectory(directory);
            var probeFile = Path.Combine(directory, ".cigertool-write-test");
            File.WriteAllText(probeFile, "ok");
            File.Delete(probeFile);
            return true;
        }
        catch
        {
            return false;
        }
    }

    private static string EnsureChildDirectory(string root, string childName)
    {
        var path = Path.Combine(root, childName);
        Directory.CreateDirectory(path);
        return path;
    }

    private static string ResolveToolsDirectory(string baseDirectory)
    {
        var candidates = new[]
        {
            Path.Combine(baseDirectory, "Tools"),
            Path.Combine(baseDirectory, "tools")
        };

        foreach (var candidate in candidates)
        {
            if (Directory.Exists(candidate))
            {
                return candidate;
            }
        }

        return candidates[0];
    }
}

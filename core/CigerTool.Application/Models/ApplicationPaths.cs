namespace CigerTool.Application.Models;

public sealed record ApplicationPaths(
    string BaseDirectory,
    string DataRoot,
    string ConfigDirectory,
    string LogDirectory,
    string CacheDirectory,
    string DownloadsDirectory,
    string ToolsDirectory,
    bool IsPortableMode,
    string StorageModeLabel);

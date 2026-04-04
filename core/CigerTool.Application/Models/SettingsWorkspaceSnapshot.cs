namespace CigerTool.Application.Models;

public sealed record SettingsWorkspaceSnapshot(
    string Heading,
    string Summary,
    string Language,
    string UpdateChannel,
    string? ManifestUrl,
    bool UseTurkishDefaults,
    bool PreferSingleFilePublishing,
    string StorageMode,
    string DataRoot,
    string LogRoot,
    string DownloadsRoot,
    string ToolsRoot);

namespace CigerTool.Usb.Models;

public sealed record ReleaseManifestSummary(
    string Channel,
    string Version,
    string ImageName,
    string? ImageUrl,
    string? Sha256,
    string Notes,
    long? SizeBytes,
    string SourceDescription,
    string Status,
    string ModeLabel,
    string? LocalImagePath,
    bool IsCachedFallback);

namespace CigerTool.Domain.Models;

public sealed record ReleaseSourceConfiguration(
    string DefaultChannel,
    string? DefaultManifestUrl,
    bool AllowManualImageSelection,
    bool AllowLocalOverride);

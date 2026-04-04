namespace CigerTool.Application.Models;

public sealed record ApplicationSettings(
    string ProductName,
    string Language,
    string DefaultChannel,
    string? DefaultManifestUrl,
    bool UseTurkishDefaults,
    bool PreferSingleFilePublishing);

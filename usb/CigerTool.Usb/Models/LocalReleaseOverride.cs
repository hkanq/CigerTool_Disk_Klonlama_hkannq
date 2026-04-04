using System.Text.Json.Serialization;

namespace CigerTool.Usb.Models;

internal sealed class LocalReleaseOverride
{
    [JsonPropertyName("enabled")]
    public bool Enabled { get; init; } = true;

    [JsonPropertyName("channel")]
    public string? Channel { get; init; }

    [JsonPropertyName("manifest_url")]
    public string? ManifestUrl { get; init; }

    [JsonPropertyName("image_file")]
    public string? ImageFile { get; init; }

    [JsonPropertyName("version")]
    public string? Version { get; init; }

    [JsonPropertyName("image_name")]
    public string? ImageName { get; init; }

    [JsonPropertyName("sha256")]
    public string? Sha256 { get; init; }

    [JsonPropertyName("notes")]
    public string? Notes { get; init; }
}

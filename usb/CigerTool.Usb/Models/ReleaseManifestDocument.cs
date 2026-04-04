using System.Text.Json.Serialization;

namespace CigerTool.Usb.Models;

internal sealed class ReleaseManifestDocument
{
    [JsonPropertyName("channel")]
    public string? Channel { get; init; }

    [JsonPropertyName("version")]
    public string? Version { get; init; }

    [JsonPropertyName("image_name")]
    public string? ImageName { get; init; }

    [JsonPropertyName("image_url")]
    public string? ImageUrl { get; init; }

    [JsonPropertyName("sha256")]
    public string? Sha256 { get; init; }

    [JsonPropertyName("notes")]
    public string? Notes { get; init; }

    [JsonPropertyName("size_bytes")]
    public long? SizeBytes { get; init; }
}

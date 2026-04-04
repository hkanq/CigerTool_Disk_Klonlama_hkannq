namespace CigerTool.Domain.Models;

public sealed record ToolDefinition(
    string Id,
    string Name,
    string Category,
    string Description,
    string ExecutablePath,
    string? Arguments,
    bool AvailableInWinPe,
    bool IsBundled,
    string ResolvedExecutablePath,
    bool Exists,
    bool CanLaunch,
    string AvailabilityStatus);

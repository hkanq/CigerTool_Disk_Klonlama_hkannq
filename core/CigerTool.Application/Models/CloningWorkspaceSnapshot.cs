using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record CloningWorkspaceSnapshot(
    string Heading,
    string Summary,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<DiskSummary> Candidates,
    IReadOnlyList<string> Recommendations,
    bool RawCloneEnabled,
    bool SmartCloneEnabled);

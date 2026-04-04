using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record DiskWorkspaceSnapshot(
    string Heading,
    string Summary,
    SystemSummary System,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<DiskSummary> Disks,
    IReadOnlyList<string> Notes);

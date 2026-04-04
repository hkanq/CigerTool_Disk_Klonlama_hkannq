using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record BackupWorkspaceSnapshot(
    string Heading,
    string Summary,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<BackupOperationOption> Operations,
    IReadOnlyList<BackupCapabilityItem> Capabilities,
    IReadOnlyList<DiskSummary> CandidateDisks,
    IReadOnlyList<string> SupportedScenarios);

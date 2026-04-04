using CigerTool.Domain.Enums;

namespace CigerTool.Domain.Models;

public sealed record CloneAnalysisResult(
    CloneMode Mode,
    CloneSuitabilityStatus Status,
    bool CanProceed,
    string Summary,
    string SourceName,
    string TargetName,
    string RequiredCapacityLabel,
    string ComparisonLabel,
    IReadOnlyList<CloneAnalysisCheck> Checks);

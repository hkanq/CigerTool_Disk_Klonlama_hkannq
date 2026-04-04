namespace CigerTool.Application.Models;

public sealed record OperationProgressSnapshot(
    string PhaseLabel,
    string Summary,
    double Percent,
    bool IsIndeterminate,
    long ProcessedBytes,
    long TotalBytes,
    string ProcessedLabel,
    string TotalLabel,
    string SpeedLabel,
    string RemainingLabel,
    string? CurrentItem);

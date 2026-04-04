using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record CloneExecutionResult(
    ExecutionState State,
    string StatusLabel,
    string Summary,
    string ModeLabel,
    string SourceName,
    string TargetName,
    long ProcessedBytes,
    long TotalBytes,
    int CopiedItems,
    IReadOnlyList<string> Warnings,
    IReadOnlyList<string> Notes);

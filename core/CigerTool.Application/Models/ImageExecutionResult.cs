using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record ImageExecutionResult(
    BackupWorkflowKind Operation,
    ExecutionState State,
    string StatusLabel,
    string Summary,
    string FormatLabel,
    string SourceLabel,
    string DestinationLabel,
    long ProcessedBytes,
    long TotalBytes,
    IReadOnlyList<string> Warnings,
    IReadOnlyList<string> Notes);

using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record LogsWorkspaceSnapshot(
    string Heading,
    string Summary,
    IReadOnlyList<CardMetric> Metrics,
    string TextLogPath,
    string StructuredLogPath,
    IReadOnlyList<LogEntry> Entries);

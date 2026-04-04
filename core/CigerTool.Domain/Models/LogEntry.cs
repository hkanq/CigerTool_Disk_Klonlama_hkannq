using CigerTool.Domain.Enums;

namespace CigerTool.Domain.Models;

public sealed record LogEntry(
    DateTimeOffset Timestamp,
    OperationSeverity Severity,
    string Area,
    string EventId,
    string Message,
    string Details);

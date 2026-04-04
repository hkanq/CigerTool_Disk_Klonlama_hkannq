using CigerTool.Domain.Enums;

namespace CigerTool.Domain.Models;

public sealed record CloneAnalysisCheck(
    string Title,
    string Message,
    OperationSeverity Severity);

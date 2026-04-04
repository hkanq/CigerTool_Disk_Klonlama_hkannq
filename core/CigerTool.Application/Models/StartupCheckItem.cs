using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record StartupCheckItem(
    string Title,
    string Status,
    string Detail,
    OperationSeverity Severity);

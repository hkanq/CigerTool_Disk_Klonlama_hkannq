using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record AttentionItem(
    string Title,
    string Description,
    OperationSeverity Severity);

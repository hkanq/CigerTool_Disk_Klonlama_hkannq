using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record BackupOperationOption(
    BackupWorkflowKind Value,
    string Title,
    string Description,
    string AvailabilityLabel,
    bool IsExecutionAvailable);

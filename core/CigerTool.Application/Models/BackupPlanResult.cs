using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record BackupPlanResult(
    BackupWorkflowKind Operation,
    string StatusLabel,
    string Summary,
    string NextAction,
    string ScopeNote,
    bool CanStartNow,
    bool CanExportPlan,
    IReadOnlyList<string> Warnings,
    IReadOnlyList<WorkflowStepItem> Steps);

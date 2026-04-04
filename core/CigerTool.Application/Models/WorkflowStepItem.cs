namespace CigerTool.Application.Models;

public sealed record WorkflowStepItem(
    string Title,
    string Description,
    bool IsCurrent,
    bool IsCompleted);

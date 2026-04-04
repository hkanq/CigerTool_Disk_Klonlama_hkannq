namespace CigerTool.Domain.Enums;

public enum ExecutionState
{
    NotStarted = 0,
    Running = 1,
    Succeeded = 2,
    CompletedWithWarnings = 3,
    Canceled = 4,
    Failed = 5
}

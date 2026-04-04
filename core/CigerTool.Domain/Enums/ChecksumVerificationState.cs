namespace CigerTool.Domain.Enums;

public enum ChecksumVerificationState
{
    NotStarted = 0,
    Verified = 1,
    CalculatedOnly = 2,
    Mismatch = 3,
    Failed = 4
}

namespace CigerTool.Domain.Models;

public sealed record AppEnvironmentProfile(
    string ProfileName,
    bool IsWinPe,
    bool SupportsUsbCreation,
    bool SupportsLiveCloning,
    string Summary);

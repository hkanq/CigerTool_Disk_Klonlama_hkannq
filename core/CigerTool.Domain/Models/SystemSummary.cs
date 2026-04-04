namespace CigerTool.Domain.Models;

public sealed record SystemSummary(
    string MachineName,
    string OperatingSystem,
    string Architecture,
    string Framework,
    string CurrentUser,
    string SystemDrive,
    string UptimeLabel);

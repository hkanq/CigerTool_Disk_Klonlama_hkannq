namespace CigerTool.Application.Models;

public sealed record UsbDeviceEntry(
    string Id,
    string DisplayName,
    string Model,
    string PhysicalPath,
    string SizeLabel,
    long SizeBytes,
    string MountedVolumesLabel,
    bool IsSystemDisk,
    bool CanWrite,
    string SafetyStatus);

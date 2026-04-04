namespace CigerTool.Usb.Models;

internal sealed record UsbPhysicalDeviceInfo(
    string Id,
    string PhysicalPath,
    string Model,
    long SizeBytes,
    IReadOnlyList<string> MountedVolumes,
    bool IsSystemDisk);

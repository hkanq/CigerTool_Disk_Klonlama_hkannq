using System.Management;
using CigerTool.Application.Contracts;
using CigerTool.Domain.Enums;
using CigerTool.Usb.Models;

namespace CigerTool.Usb.Services;

internal sealed class UsbDeviceDiscoveryService(IOperationLogService operationLogService)
{
    public IReadOnlyList<UsbPhysicalDeviceInfo> GetUsbDevices()
    {
        var systemDrive = (Environment.GetEnvironmentVariable("SystemDrive") ?? "C:").TrimEnd('\\');
        var devices = new List<UsbPhysicalDeviceInfo>();

        try
        {
            using var searcher = new ManagementObjectSearcher(
                "SELECT DeviceID, Model, Size, InterfaceType, MediaType, PNPDeviceID, Index FROM Win32_DiskDrive");

            foreach (ManagementObject disk in searcher.Get())
            {
                using (disk)
                {
                    var deviceId = disk["DeviceID"]?.ToString();
                    if (string.IsNullOrWhiteSpace(deviceId))
                    {
                        continue;
                    }

                    var interfaceType = disk["InterfaceType"]?.ToString() ?? string.Empty;
                    var mediaType = disk["MediaType"]?.ToString() ?? string.Empty;
                    var pnpDeviceId = disk["PNPDeviceID"]?.ToString() ?? string.Empty;

                    if (!IsUsbCandidate(interfaceType, mediaType, pnpDeviceId))
                    {
                        continue;
                    }

                    var index = Convert.ToInt32(disk["Index"] ?? -1);
                    if (index < 0)
                    {
                        continue;
                    }

                    var physicalPath = $@"\\.\PhysicalDrive{index}";
                    var volumes = GetMountedVolumes(deviceId);
                    var isSystemDisk = volumes.Any(volume => string.Equals(volume, systemDrive, StringComparison.OrdinalIgnoreCase));
                    var sizeBytes = TryGetLong(disk["Size"]);
                    var model = string.IsNullOrWhiteSpace(disk["Model"]?.ToString())
                        ? $"USB Disk {index}"
                        : disk["Model"]!.ToString()!;

                    devices.Add(new UsbPhysicalDeviceInfo(
                        Id: physicalPath,
                        PhysicalPath: physicalPath,
                        Model: model,
                        SizeBytes: sizeBytes,
                        MountedVolumes: volumes,
                        IsSystemDisk: isSystemDisk));
                }
            }
        }
        catch (Exception ex)
        {
                operationLogService.Record(
                    OperationSeverity.Warning,
                    "USB Oluşturma",
                    "USB aygıtları algılanamadı.",
                    "usb.devices.enumeration.failure",
                    new Dictionary<string, string>
                    {
                    ["error"] = ex.Message
                });
        }

        return devices
            .OrderByDescending(device => device.IsSystemDisk)
            .ThenBy(device => device.Model)
            .ToArray();
    }

    private static bool IsUsbCandidate(string interfaceType, string mediaType, string pnpDeviceId)
    {
        return interfaceType.Equals("USB", StringComparison.OrdinalIgnoreCase) ||
               mediaType.Contains("Removable", StringComparison.OrdinalIgnoreCase) ||
               pnpDeviceId.StartsWith("USB", StringComparison.OrdinalIgnoreCase);
    }

    private static IReadOnlyList<string> GetMountedVolumes(string deviceId)
    {
        var volumes = new List<string>();
        var escapedDeviceId = EscapeWmiString(deviceId);
        using var partitionSearcher = new ManagementObjectSearcher(
            $"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{escapedDeviceId}'}} WHERE AssocClass = Win32_DiskDriveToDiskPartition");

        foreach (ManagementObject partition in partitionSearcher.Get())
        {
            using (partition)
            {
                var partitionId = partition["DeviceID"]?.ToString();
                if (string.IsNullOrWhiteSpace(partitionId))
                {
                    continue;
                }

                var escapedPartitionId = EscapeWmiString(partitionId);
                using var logicalDiskSearcher = new ManagementObjectSearcher(
                    $"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{escapedPartitionId}'}} WHERE AssocClass = Win32_LogicalDiskToPartition");

                foreach (ManagementObject logicalDisk in logicalDiskSearcher.Get())
                {
                    using (logicalDisk)
                    {
                        var name = logicalDisk["Name"]?.ToString();
                        if (!string.IsNullOrWhiteSpace(name))
                        {
                            volumes.Add(name.Trim());
                        }
                    }
                }
            }
        }

        return volumes
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(volume => volume)
            .ToArray();
    }

    private static long TryGetLong(object? value)
    {
        try
        {
            return Convert.ToInt64(value ?? 0L);
        }
        catch
        {
            return 0L;
        }
    }

    private static string EscapeWmiString(string value)
    {
        return value
            .Replace("\\", "\\\\", StringComparison.Ordinal)
            .Replace("'", "\\'", StringComparison.Ordinal);
    }
}

using System.Management;
using System.Runtime.InteropServices;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;
using CigerTool.Domain.Models;
using CigerTool.Infrastructure.Common;

namespace CigerTool.Infrastructure.Disks;

public sealed class RuntimeDiskInventoryService(IOperationLogService operationLogService) : IDiskInventoryService
{
    public DiskWorkspaceSnapshot GetSnapshot()
    {
        var disks = GetCurrentDisks();
        var systemDrive = System.Environment.GetEnvironmentVariable("SystemDrive") ?? "C:";
        var systemDisk = disks.FirstOrDefault(disk => disk.IsSystemVolume);
        var fixedCount = disks.Count(disk => !disk.IsRemovable);
        var removableCount = disks.Count(disk => disk.IsRemovable);
        var warningCount = disks.Count(disk => !string.Equals(disk.WarningSummary, "Hazır", StringComparison.OrdinalIgnoreCase));

        return new DiskWorkspaceSnapshot(
            Heading: "Diskler ve Sağlık",
            Summary: "Bağlı sürücüleri, kapasite durumunu, bağlantı tipini ve seçim öncesi dikkat gerektiren uyarıları burada görebilirsiniz.",
            System: new SystemSummary(
                MachineName: System.Environment.MachineName,
                OperatingSystem: RuntimeInformation.OSDescription,
                Architecture: RuntimeInformation.OSArchitecture.ToString(),
                Framework: RuntimeInformation.FrameworkDescription,
                CurrentUser: System.Environment.UserName,
                SystemDrive: systemDrive,
                UptimeLabel: ByteSizeFormatter.FormatUptime(TimeSpan.FromMilliseconds(System.Environment.TickCount64))),
            Metrics:
            [
                new CardMetric("Toplam sürücü", disks.Count.ToString(), "İşlem ekranlarında seçilebilir sürücüler."),
                new CardMetric("Dahili / sabit", fixedCount.ToString(), "Genellikle sistem veya veri amaçlı kullanılan sürücüler."),
                new CardMetric("Çıkarılabilir", removableCount.ToString(), "USB bellek veya taşınabilir diskler."),
                new CardMetric("Dikkat gerektiren", warningCount.ToString(), "Düşük boş alan veya sınırlı erişim gibi notlar içeren sürücüler."),
                new CardMetric(
                    "Sistem sürücüsü",
                    systemDisk?.DriveLetter ?? systemDrive,
                    systemDisk is null ? "Sistem sürücüsü ayrıntısı okunamadı." : $"{systemDisk.FreeLabel} boş alan")
            ],
            Disks: disks,
            Notes:
            [
                "Sağlık özeti; boş alan, Windows durum bilgisi ve erişim koşullarına göre oluşturulur.",
                "Derin SMART ve üreticiye özel telemetri bu sürümde tam kapsamlı değildir.",
                "Ham kopya ve ham imaj alma için yönetici yetkisi gerekir."
            ]);
    }

    public IReadOnlyList<DiskSummary> GetCurrentDisks()
    {
        var systemDrive = (System.Environment.GetEnvironmentVariable("SystemDrive") ?? "C:").TrimEnd('\\');
        var mappings = TryBuildDriveMappings();
        var disks = new List<DiskSummary>();

        foreach (var drive in DriveInfo.GetDrives())
        {
            if (!drive.IsReady)
            {
                continue;
            }

            if (drive.DriveType is not (DriveType.Fixed or DriveType.Removable))
            {
                continue;
            }

            try
            {
                var driveLetter = drive.Name.TrimEnd('\\');
                var totalBytes = drive.TotalSize;
                var freeBytes = drive.AvailableFreeSpace;
                var usedBytes = Math.Max(0, totalBytes - freeBytes);
                var usagePercent = totalBytes == 0 ? 0 : (int)Math.Round((double)usedBytes / totalBytes * 100d, MidpointRounding.AwayFromZero);
                var mapping = mappings.FirstOrDefault(item => string.Equals(item.DriveLetter, driveLetter, StringComparison.OrdinalIgnoreCase));
                var isSystemVolume = string.Equals(driveLetter, systemDrive, StringComparison.OrdinalIgnoreCase);
                var connectionType = MapConnectionType(drive.DriveType, mapping?.InterfaceType);
                var warningSummary = BuildWarningSummary(freeBytes, totalBytes, isSystemVolume, mapping);
                var healthLabel = BuildHealthLabel(warningSummary, mapping?.Status);
                var displayName = string.IsNullOrWhiteSpace(drive.VolumeLabel) ? driveLetter : $"{driveLetter} - {drive.VolumeLabel}";

                disks.Add(new DiskSummary(
                    Id: driveLetter,
                    Name: displayName,
                    DriveLetter: driveLetter,
                    FileSystem: SafeRead(() => drive.DriveFormat, "Bilinmiyor"),
                    ConnectionType: connectionType,
                    CapacityLabel: ByteSizeFormatter.Format(totalBytes),
                    UsedLabel: ByteSizeFormatter.Format(usedBytes),
                    FreeLabel: ByteSizeFormatter.Format(freeBytes),
                    LayoutLabel: isSystemVolume ? "Sistem sürücüsü" : "Veri sürücüsü",
                    HealthLabel: healthLabel,
                    TotalBytes: totalBytes,
                    UsedBytes: usedBytes,
                    FreeBytes: freeBytes,
                    IsSystemVolume: isSystemVolume,
                    IsReady: true,
                    DeviceModel: mapping?.Model ?? "Bilinmeyen aygıt",
                    BusType: mapping?.InterfaceType ?? (drive.DriveType == DriveType.Removable ? "USB" : "Dahili"),
                    MediaType: mapping?.MediaType ?? (drive.DriveType == DriveType.Removable ? "Çıkarılabilir" : "Sabit"),
                    IdentityLabel: BuildIdentityLabel(mapping, connectionType),
                    WarningSummary: warningSummary,
                    UsagePercent: usagePercent,
                    IsRemovable: drive.DriveType == DriveType.Removable,
                    SupportsRawAccess: RawVolumeAccessScope.IsAdministrator()));
            }
            catch (Exception ex)
            {
                operationLogService.Record(
                    OperationSeverity.Warning,
                    "Diskler",
                    $"Sürücü bilgisi okunamadı: {drive.Name}",
                    "disks.read.failure",
                    new Dictionary<string, string>
                    {
                        ["drive"] = drive.Name,
                        ["error"] = ex.Message
                    });
            }
        }

        return disks
            .OrderByDescending(disk => disk.IsSystemVolume)
            .ThenBy(disk => disk.IsRemovable)
            .ThenBy(disk => disk.DriveLetter)
            .ToArray();
    }

    public DiskSummary? FindById(string id)
    {
        return GetCurrentDisks().FirstOrDefault(disk => string.Equals(disk.Id, id, StringComparison.OrdinalIgnoreCase));
    }

    private static IReadOnlyList<DriveMapping> TryBuildDriveMappings()
    {
        try
        {
            using var searcher = new ManagementObjectSearcher("SELECT DeviceID, Model, InterfaceType, MediaType, Index, Status FROM Win32_DiskDrive");
            using var results = searcher.Get();
            var mappings = new List<DriveMapping>();

            foreach (ManagementObject disk in results)
            {
                var diskDeviceId = disk["DeviceID"]?.ToString();
                if (string.IsNullOrWhiteSpace(diskDeviceId))
                {
                    continue;
                }

                var query = $"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{EscapeWmiPath(diskDeviceId)}'}} WHERE AssocClass = Win32_DiskDriveToDiskPartition";
                using var partitions = new ManagementObjectSearcher(query).Get();
                foreach (ManagementObject partition in partitions)
                {
                    var partitionId = partition["DeviceID"]?.ToString();
                    if (string.IsNullOrWhiteSpace(partitionId))
                    {
                        continue;
                    }

                    var logicalQuery = $"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{EscapeWmiPath(partitionId)}'}} WHERE AssocClass = Win32_LogicalDiskToPartition";
                    using var logicalDisks = new ManagementObjectSearcher(logicalQuery).Get();
                    foreach (ManagementObject logicalDisk in logicalDisks)
                    {
                        var driveLetter = logicalDisk["DeviceID"]?.ToString();
                        if (string.IsNullOrWhiteSpace(driveLetter))
                        {
                            continue;
                        }

                        mappings.Add(new DriveMapping(
                            DriveLetter: driveLetter,
                            Model: disk["Model"]?.ToString() ?? "Bilinmeyen aygıt",
                            InterfaceType: disk["InterfaceType"]?.ToString() ?? "Bilinmiyor",
                            MediaType: disk["MediaType"]?.ToString() ?? "Bilinmiyor",
                            Status: disk["Status"]?.ToString() ?? "Bilinmiyor",
                            Index: disk["Index"]?.ToString() ?? string.Empty));
                    }
                }
            }

            return mappings;
        }
        catch
        {
            return [];
        }
    }

    private static string EscapeWmiPath(string value)
    {
        return value.Replace("\\", "\\\\").Replace("'", "\\'");
    }

    private static string BuildIdentityLabel(DriveMapping? mapping, string connectionType)
    {
        if (mapping is null)
        {
            return connectionType;
        }

        var parts = new List<string>();
        if (!string.IsNullOrWhiteSpace(mapping.Index))
        {
            parts.Add($"Disk {mapping.Index}");
        }

        if (!string.IsNullOrWhiteSpace(mapping.Model))
        {
            parts.Add(mapping.Model);
        }

        if (!string.IsNullOrWhiteSpace(mapping.InterfaceType))
        {
            parts.Add(mapping.InterfaceType);
        }

        return string.Join(" · ", parts.Where(part => !string.IsNullOrWhiteSpace(part)));
    }

    private static string BuildHealthLabel(string warningSummary, string? status)
    {
        if (!string.IsNullOrWhiteSpace(status) && !string.Equals(status, "OK", StringComparison.OrdinalIgnoreCase))
        {
            return "Dikkat gerekiyor";
        }

        return string.Equals(warningSummary, "Hazır", StringComparison.OrdinalIgnoreCase)
            ? "Hazır"
            : "İnceleme önerilir";
    }

    private static string BuildWarningSummary(long freeBytes, long totalBytes, bool isSystemVolume, DriveMapping? mapping)
    {
        if (!string.IsNullOrWhiteSpace(mapping?.Status) && !string.Equals(mapping.Status, "OK", StringComparison.OrdinalIgnoreCase))
        {
            return "Windows durum bilgisi sürücüde dikkat gerektirdiğini bildiriyor.";
        }

        if (totalBytes > 0 && freeBytes * 100L / totalBytes < 10)
        {
            return "Boş alan çok düşük.";
        }

        if (isSystemVolume)
        {
            return "Çalışan sistem sürücüsü.";
        }

        return "Hazır";
    }

    private static string MapConnectionType(DriveType driveType, string? interfaceType) => driveType switch
    {
        DriveType.Fixed when string.Equals(interfaceType, "USB", StringComparison.OrdinalIgnoreCase) => "USB üzerinden bağlı",
        DriveType.Fixed => "Dahili / sabit",
        DriveType.Removable => "Çıkarılabilir",
        DriveType.Network => "Ağ",
        _ => interfaceType ?? driveType.ToString()
    };

    private static string SafeRead(Func<string> action, string fallback)
    {
        try
        {
            return action();
        }
        catch
        {
            return fallback;
        }
    }

    private sealed record DriveMapping(
        string DriveLetter,
        string Model,
        string InterfaceType,
        string MediaType,
        string Status,
        string Index);
}

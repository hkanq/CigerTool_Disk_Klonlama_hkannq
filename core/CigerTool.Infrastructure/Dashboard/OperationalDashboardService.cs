using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;

namespace CigerTool.Infrastructure.Dashboard;

public sealed class OperationalDashboardService(
    IEnvironmentProfileService environmentProfileService,
    IStartupDiagnosticsService startupDiagnosticsService,
    IDiskInventoryService diskInventoryService,
    ICloneWorkflowService cloneWorkflowService,
    IBackupWorkflowService backupWorkflowService,
    IUsbCreationService usbCreationService,
    IOperationLogService operationLogService) : IDashboardService
{
    public DashboardSnapshot GetSnapshot()
    {
        var environment = environmentProfileService.GetCurrentProfile();
        var diagnostics = startupDiagnosticsService.Run();
        var disks = diskInventoryService.GetSnapshot();
        var clone = cloneWorkflowService.GetSnapshot();
        var backup = backupWorkflowService.GetSnapshot();
        var usb = usbCreationService.GetSnapshot();
        var logs = operationLogService.GetSnapshot();
        var warningCount = logs.Entries.Count(entry => entry.Severity == OperationSeverity.Warning);
        var errorCount = logs.Entries.Count(entry => entry.Severity == OperationSeverity.Error);
        var systemDisk = disks.Disks.FirstOrDefault(disk => disk.IsSystemVolume);
        var hasPreparedImage = !string.IsNullOrWhiteSpace(usb.Release.PreparedImagePath);

        return new DashboardSnapshot(
            Heading: "CigerTool",
            Summary: "Klonlama, imaj alma, geri yükleme ve USB ortamı oluşturma adımlarını tek ekrandan yönetebilirsiniz.",
            Metrics:
            [
                new CardMetric("Bağlı sürücü", disks.Disks.Count.ToString(), "İşlem için görünen sürücüler."),
                new CardMetric(
                    "Klonlama",
                    clone.Candidates.Count >= 2 ? "Yürütme açık" : "Ek sürücü gerekli",
                    clone.Candidates.Count >= 2
                        ? "Kaynak ve hedef seçilip doğrulama sonrası gerçek kopyalama başlatılabilir."
                        : "Klonlama için en az iki uygun sürücü gerekir."),
                new CardMetric(
                    "Yedekleme ve imaj",
                    "İmaj alma açık",
                    "İmaj oluşturma, geri yükleme ve dönüştürme bu sürümde çalışır."),
                new CardMetric(
                    "USB ortamı",
                    hasPreparedImage ? "İmaj hazır" : "Hazırlık gerekiyor",
                    usb.Release.Status),
                new CardMetric(
                    "Son olaylar",
                    $"{warningCount} uyarı / {errorCount} hata",
                    "İşlem kayıtları Günlükler bölümünde ayrıntılı görülebilir."),
                new CardMetric(
                    "Sistem sürücüsü",
                    systemDisk?.DriveLetter ?? disks.System.SystemDrive,
                    systemDisk is null ? "Sistem sürücüsü ayrıntısı okunamadı." : $"{systemDisk.FreeLabel} boş alan")
            ],
            Highlights:
            [
                new AttentionItem(
                    "Klonlama",
                    clone.Candidates.Count >= 2
                        ? "Klonlama bölümünden kaynak ve hedefi seçip denetim sonrası işlemi başlatabilirsiniz."
                        : "Klonlama için ikinci uygun sürücüyü bağlayın.",
                    clone.Candidates.Count >= 2 ? OperationSeverity.Info : OperationSeverity.Warning),
                new AttentionItem(
                    "İmaj işlemleri",
                    "Yedekleme ve İmaj bölümünde sürücüden imaj alabilir, imajı geri yükleyebilir veya .img ile .ctimg arasında dönüşüm yapabilirsiniz.",
                    OperationSeverity.Info),
                new AttentionItem(
                    "USB ortamı",
                    usb.CanWriteFromCurrentState
                        ? "İmaj ve aygıt hazır görünüyor. İsterseniz USB yazma adımına geçebilirsiniz."
                        : "USB yazma öncesi imaj, bütünlük veya aygıt hazırlığını tamamlayın.",
                    usb.CanWriteFromCurrentState ? OperationSeverity.Info : OperationSeverity.Warning),
                new AttentionItem(
                    "Çalışma ortamı",
                    environment.IsWinPe
                        ? "Servis ortamında çevrim dışı disk işlemleri için en güvenli koşullar sağlanır."
                        : "Masaüstünde aktif sistem sürücüsüne yönelik canlı işlem sınırları uygulanır.",
                    OperationSeverity.Info),
                new AttentionItem(
                    "Başlangıç denetimi",
                    diagnostics.Summary,
                    diagnostics.Severity)
            ],
            RecentEntries: logs.Entries.Take(5).ToArray(),
            Diagnostics: diagnostics);
    }
}

using System.Text.Json;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;
using CigerTool.Domain.Models;

namespace CigerTool.Infrastructure.Logging;

public sealed class FileOperationLogService : IOperationLogService
{
    private readonly List<LogEntry> _entries = [];
    private readonly object _sync = new();
    private readonly string _textLogPath;
    private readonly string _structuredLogPath;

    public FileOperationLogService(IAppPathService appPathService)
    {
        var logDirectory = appPathService.GetPaths().LogDirectory;

        Directory.CreateDirectory(logDirectory);
        _textLogPath = Path.Combine(logDirectory, "cigertool.log");
        _structuredLogPath = Path.Combine(logDirectory, "cigertool.jsonl");

        Record(OperationSeverity.Info, "Başlangıç", "Uygulama başlatıldı.", "app.start");
        Record(OperationSeverity.Info, "Günlükleme", "Metin ve yapılandırılmış günlük dosyaları hazır.", "logging.ready");
        Record(OperationSeverity.Info, "Yollar", $"Günlük klasörü hazır: {logDirectory}", "paths.logs.ready");
    }

    public LogsWorkspaceSnapshot GetSnapshot()
    {
        LogEntry[] entries;

        lock (_sync)
        {
            entries = _entries
                .OrderByDescending(entry => entry.Timestamp)
                .ToArray();
        }

        var warningCount = entries.Count(entry => entry.Severity == OperationSeverity.Warning);
        var errorCount = entries.Count(entry => entry.Severity == OperationSeverity.Error);

        return new LogsWorkspaceSnapshot(
            Heading: "Günlükler",
            Summary: "Önemli olayları, hataları ve işlem sonuçlarını burada izleyebilirsiniz.",
            Metrics:
            [
                new CardMetric("Toplam olay", entries.Length.ToString(), "Bellekte tutulan son olaylar."),
                new CardMetric("Uyarı", warningCount.ToString(), "Dikkat gerektiren olaylar."),
                new CardMetric("Hata", errorCount.ToString(), "Kullanıcı dostu hata mesajları ile kaydedilen sorunlar."),
                new CardMetric("Makine okunur kayıt", "JSONL", "Gelişmiş inceleme için yapılandırılmış kayıt akışı aktif.")
            ],
            TextLogPath: _textLogPath,
            StructuredLogPath: _structuredLogPath,
            Entries: entries);
    }

    public void Record(
        OperationSeverity severity,
        string area,
        string message,
        string? eventId = null,
        IReadOnlyDictionary<string, string>? details = null)
    {
        var detailText = details is null || details.Count == 0
            ? string.Empty
            : string.Join(", ", details.Select(pair => $"{pair.Key}={pair.Value}"));
        var entry = new LogEntry(DateTimeOffset.Now, severity, area, eventId ?? $"{area.ToLowerInvariant()}.event", message, detailText);

        lock (_sync)
        {
            _entries.Add(entry);

            if (_entries.Count > 500)
            {
                _entries.RemoveRange(0, _entries.Count - 500);
            }
        }

        try
        {
            var line = $"{entry.Timestamp:yyyy-MM-dd HH:mm:ss} [{entry.Severity}] {entry.Area}/{entry.EventId}: {entry.Message}";
            var finalLine = string.IsNullOrWhiteSpace(entry.Details) ? line : $"{line} | {entry.Details}";
            File.AppendAllText(_textLogPath, finalLine + System.Environment.NewLine);

            var structured = JsonSerializer.Serialize(new
            {
                timestamp = entry.Timestamp,
                severity = entry.Severity.ToString(),
                area = entry.Area,
                eventId = entry.EventId,
                message = entry.Message,
                details
            });

            File.AppendAllText(_structuredLogPath, structured + System.Environment.NewLine);
        }
        catch
        {
        }
    }
}

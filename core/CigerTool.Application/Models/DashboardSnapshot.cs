using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record DashboardSnapshot(
    string Heading,
    string Summary,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<AttentionItem> Highlights,
    IReadOnlyList<LogEntry> RecentEntries,
    StartupDiagnosticsSnapshot Diagnostics);

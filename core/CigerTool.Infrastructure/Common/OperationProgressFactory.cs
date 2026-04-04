using System.Diagnostics;
using CigerTool.Application.Models;

namespace CigerTool.Infrastructure.Common;

internal static class OperationProgressFactory
{
    public static OperationProgressSnapshot Create(
        string phaseLabel,
        string summary,
        long processedBytes,
        long totalBytes,
        Stopwatch stopwatch,
        string? currentItem = null,
        bool isIndeterminate = false)
    {
        var boundedProcessed = Math.Max(0, processedBytes);
        var boundedTotal = Math.Max(0, totalBytes);
        var percent = boundedTotal == 0
            ? 0
            : Math.Min(100d, Math.Round((double)boundedProcessed / boundedTotal * 100d, 1));
        var elapsedSeconds = Math.Max(0.1d, stopwatch.Elapsed.TotalSeconds);
        var speedBytesPerSecond = boundedProcessed / elapsedSeconds;
        var remainingBytes = Math.Max(0, boundedTotal - boundedProcessed);
        var remaining = speedBytesPerSecond > 0
            ? TimeSpan.FromSeconds(remainingBytes / speedBytesPerSecond)
            : (TimeSpan?)null;

        return new OperationProgressSnapshot(
            PhaseLabel: phaseLabel,
            Summary: summary,
            Percent: percent,
            IsIndeterminate: isIndeterminate,
            ProcessedBytes: boundedProcessed,
            TotalBytes: boundedTotal,
            ProcessedLabel: ByteSizeFormatter.Format(boundedProcessed),
            TotalLabel: ByteSizeFormatter.Format(boundedTotal),
            SpeedLabel: speedBytesPerSecond <= 0 ? "Hesaplanıyor" : $"{ByteSizeFormatter.Format((long)speedBytesPerSecond)}/sn",
            RemainingLabel: remaining is null ? "Hesaplanıyor" : ByteSizeFormatter.FormatDuration(remaining.Value),
            CurrentItem: currentItem);
    }
}

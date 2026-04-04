using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record UsbCreatorWorkspaceSnapshot(
    string Heading,
    string Summary,
    ReleaseSourceConfiguration ReleaseSourceConfiguration,
    string ReleaseSourceStatus,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<string> Requirements,
    UsbReleaseInfo Release,
    IReadOnlyList<UsbDeviceEntry> Devices,
    bool IsAdministrator,
    bool CanWriteFromCurrentState);

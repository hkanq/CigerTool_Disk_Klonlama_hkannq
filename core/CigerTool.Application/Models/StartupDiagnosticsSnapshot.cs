using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record StartupDiagnosticsSnapshot(
    string Heading,
    string Summary,
    string ReadinessLabel,
    OperationSeverity Severity,
    ApplicationPaths Paths,
    IReadOnlyList<StartupCheckItem> Checks);

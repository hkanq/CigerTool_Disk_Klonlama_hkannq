using CigerTool.Domain.Models;

namespace CigerTool.Application.Models;

public sealed record ToolsWorkspaceSnapshot(
    string Heading,
    string Summary,
    IReadOnlyList<CardMetric> Metrics,
    IReadOnlyList<ToolDefinition> Tools,
    string LaunchPolicyNote,
    string CatalogSource);

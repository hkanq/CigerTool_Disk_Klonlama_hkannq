using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record CloneWorkflowRequest(
    CloneMode Mode,
    string? SourceId,
    string? TargetId);

using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record BackupWorkflowRequest(
    BackupWorkflowKind Operation,
    string? SourceDiskId,
    string? TargetDiskId,
    string? SourceImagePath,
    string? DestinationPath,
    ImageContainerFormat Format,
    ImageCaptureMode CaptureMode);

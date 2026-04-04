using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record ImageCaptureModeOption(
    ImageCaptureMode Value,
    string Title,
    string Description,
    string AvailabilityLabel,
    bool IsExecutionAvailable);

using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record UsbReleaseInfo(
    string ModeLabel,
    string Status,
    string SourceDescription,
    string Channel,
    string Version,
    string ImageName,
    string ImageSizeLabel,
    string Notes,
    string? ImageUrl,
    string? PreparedImagePath,
    string? ExpectedSha256,
    string? CalculatedSha256,
    ChecksumVerificationState ChecksumState,
    string ChecksumStatus);

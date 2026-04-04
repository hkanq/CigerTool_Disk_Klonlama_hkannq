using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record CloneModeOption(
    CloneMode Value,
    string Title,
    string Description);

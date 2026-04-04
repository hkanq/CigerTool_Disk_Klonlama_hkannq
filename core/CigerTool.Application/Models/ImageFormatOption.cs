using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record ImageFormatOption(
    ImageContainerFormat Value,
    string Title,
    string Description,
    string DefaultExtension);

using CigerTool.Domain.Enums;

namespace CigerTool.Application.Models;

public sealed record UsbCreatorOperationResult(
    bool Succeeded,
    OperationSeverity Severity,
    string Message);

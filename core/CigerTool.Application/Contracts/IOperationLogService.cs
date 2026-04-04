using System.Collections.Generic;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;

namespace CigerTool.Application.Contracts;

public interface IOperationLogService
{
    LogsWorkspaceSnapshot GetSnapshot();

    void Record(
        OperationSeverity severity,
        string area,
        string message,
        string? eventId = null,
        IReadOnlyDictionary<string, string>? details = null);
}

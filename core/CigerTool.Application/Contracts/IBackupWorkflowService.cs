using CigerTool.Application.Models;
using CigerTool.Domain.Enums;

namespace CigerTool.Application.Contracts;

public interface IBackupWorkflowService
{
    BackupWorkspaceSnapshot GetSnapshot();

    BackupPlanResult Analyze(BackupWorkflowRequest request);

    Task<ImageExecutionResult> ExecuteAsync(
        BackupWorkflowRequest request,
        IProgress<OperationProgressSnapshot>? progress = null,
        CancellationToken cancellationToken = default);
}

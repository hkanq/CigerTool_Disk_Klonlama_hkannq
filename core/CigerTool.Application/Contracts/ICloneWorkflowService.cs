using CigerTool.Domain.Enums;
using CigerTool.Domain.Models;
using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface ICloneWorkflowService
{
    CloningWorkspaceSnapshot GetSnapshot();

    CloneAnalysisResult Analyze(CloneWorkflowRequest request);

    Task<CloneExecutionResult> ExecuteAsync(
        CloneWorkflowRequest request,
        IProgress<OperationProgressSnapshot>? progress = null,
        CancellationToken cancellationToken = default);
}

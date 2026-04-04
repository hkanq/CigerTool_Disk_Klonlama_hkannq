using CigerTool.Domain.Models;
using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface IToolCatalogService
{
    ToolsWorkspaceSnapshot GetSnapshot();

    IReadOnlyList<ToolDefinition> GetTools();
}

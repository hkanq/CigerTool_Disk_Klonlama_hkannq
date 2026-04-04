using CigerTool.Domain.Models;
using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface IDiskInventoryService
{
    DiskWorkspaceSnapshot GetSnapshot();

    IReadOnlyList<DiskSummary> GetCurrentDisks();

    DiskSummary? FindById(string id);
}

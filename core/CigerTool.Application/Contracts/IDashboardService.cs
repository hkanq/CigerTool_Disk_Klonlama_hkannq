using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface IDashboardService
{
    DashboardSnapshot GetSnapshot();
}

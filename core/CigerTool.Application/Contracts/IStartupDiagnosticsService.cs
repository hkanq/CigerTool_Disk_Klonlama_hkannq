using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface IStartupDiagnosticsService
{
    StartupDiagnosticsSnapshot Run();
}

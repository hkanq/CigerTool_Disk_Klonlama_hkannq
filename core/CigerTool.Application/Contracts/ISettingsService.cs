using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface ISettingsService
{
    ApplicationSettings GetSettings();

    SettingsWorkspaceSnapshot GetSnapshot();
}

using CigerTool.Application.Contracts;
using CigerTool.Application.Models;

namespace CigerTool.App.ViewModels.Pages;

public sealed class SettingsPageViewModel : ViewModelBase
{
    public SettingsPageViewModel(ISettingsService settingsService)
    {
        Snapshot = settingsService.GetSnapshot();
    }

    public SettingsWorkspaceSnapshot Snapshot { get; }
}

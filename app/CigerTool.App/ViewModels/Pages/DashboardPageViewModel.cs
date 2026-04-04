using System.Windows.Input;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;

namespace CigerTool.App.ViewModels.Pages;

public sealed class DashboardPageViewModel : ViewModelBase
{
    private readonly IDashboardService _dashboardService;
    private DashboardSnapshot _snapshot;
    private string _statusMessage;

    public DashboardPageViewModel(IDashboardService dashboardService)
    {
        _dashboardService = dashboardService;
        _snapshot = dashboardService.GetSnapshot();
        _statusMessage = "Ana sayfa güncel.";
        RefreshCommand = new RelayCommand(_ => Refresh());
    }

    public ICommand RefreshCommand { get; }

    public DashboardSnapshot Snapshot
    {
        get => _snapshot;
        private set => SetProperty(ref _snapshot, value);
    }

    public string StatusMessage
    {
        get => _statusMessage;
        private set => SetProperty(ref _statusMessage, value);
    }

    private void Refresh()
    {
        try
        {
            Snapshot = _dashboardService.GetSnapshot();
            StatusMessage = "Ana sayfa yenilendi.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Ana sayfa yüklenemedi: {ex.Message}";
        }
    }
}

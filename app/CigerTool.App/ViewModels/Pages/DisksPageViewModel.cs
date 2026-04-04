using System.Windows.Input;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;

namespace CigerTool.App.ViewModels.Pages;

public sealed class DisksPageViewModel : ViewModelBase
{
    private readonly IDiskInventoryService _diskInventoryService;
    private DiskWorkspaceSnapshot _snapshot;
    private string _statusMessage;

    public DisksPageViewModel(IDiskInventoryService diskInventoryService)
    {
        _diskInventoryService = diskInventoryService;
        _snapshot = diskInventoryService.GetSnapshot();
        _statusMessage = "Sürücü listesi hazır.";
        RefreshCommand = new RelayCommand(_ => Refresh());
    }

    public ICommand RefreshCommand { get; }

    public DiskWorkspaceSnapshot Snapshot
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
            Snapshot = _diskInventoryService.GetSnapshot();
            StatusMessage = "Sürücü listesi yenilendi.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Sürücü bilgisi alınamadı: {ex.Message}";
        }
    }
}

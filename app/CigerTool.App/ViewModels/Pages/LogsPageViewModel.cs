using System.Diagnostics;
using System.IO;
using System.Windows.Input;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;

namespace CigerTool.App.ViewModels.Pages;

public sealed class LogsPageViewModel : ViewModelBase
{
    private readonly IOperationLogService _operationLogService;
    private LogsWorkspaceSnapshot _snapshot;
    private string _statusMessage;

    public LogsPageViewModel(IOperationLogService operationLogService)
    {
        _operationLogService = operationLogService;
        _snapshot = operationLogService.GetSnapshot();
        _statusMessage = "Günlükler hazır.";
        RefreshCommand = new RelayCommand(_ => Refresh());
        OpenLogFolderCommand = new RelayCommand(_ => OpenLogFolder());
    }

    public ICommand RefreshCommand { get; }

    public ICommand OpenLogFolderCommand { get; }

    public LogsWorkspaceSnapshot Snapshot
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
            Snapshot = _operationLogService.GetSnapshot();
            StatusMessage = "Günlükler yenilendi.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Günlükler yüklenemedi: {ex.Message}";
        }
    }

    private void OpenLogFolder()
    {
        try
        {
            var directory = Path.GetDirectoryName(Snapshot.TextLogPath);
            if (string.IsNullOrWhiteSpace(directory) || !Directory.Exists(directory))
            {
                StatusMessage = "Günlük klasörü bulunamadı.";
                return;
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = $"\"{directory}\"",
                UseShellExecute = true
            });

            StatusMessage = "Günlük klasörü açıldı.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Günlük klasörü açılamadı: {ex.Message}";
        }
    }
}

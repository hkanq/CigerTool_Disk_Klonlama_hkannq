using System.IO;
using System.Text;
using System.Windows.Input;
using Microsoft.Win32;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;
using CigerTool.Domain.Models;
using CigerTool.Infrastructure.Common;

namespace CigerTool.App.ViewModels.Pages;

public sealed class CloningPageViewModel : ViewModelBase
{
    private readonly ICloneWorkflowService _cloneWorkflowService;
    private readonly IEnvironmentProfileService _environmentProfileService;
    private readonly IOperationLogService _operationLogService;
    private readonly RelayCommand _analyzeCommand;
    private readonly RelayCommand _savePlanCommand;
    private readonly AsyncRelayCommand _startOperationCommand;
    private readonly RelayCommand _cancelOperationCommand;
    private readonly RelayCommand _saveExecutionReportCommand;
    private CancellationTokenSource? _executionCancellationTokenSource;
    private CloningWorkspaceSnapshot _snapshot;
    private CloneModeOption _selectedMode;
    private DiskSummary? _selectedSource;
    private DiskSummary? _selectedTarget;
    private CloneAnalysisResult? _analysis;
    private CloneExecutionResult? _lastExecution;
    private OperationProgressSnapshot? _currentProgress;
    private bool _confirmDestructiveAction;
    private bool _isOperationRunning;
    private string _analysisStatus;

    public CloningPageViewModel(
        ICloneWorkflowService cloneWorkflowService,
        IEnvironmentProfileService environmentProfileService,
        IOperationLogService operationLogService)
    {
        _cloneWorkflowService = cloneWorkflowService;
        _environmentProfileService = environmentProfileService;
        _operationLogService = operationLogService;
        _snapshot = cloneWorkflowService.GetSnapshot();
        Modes =
        [
            new CloneModeOption(CloneMode.Raw, "Ham kopya", "Kaynağın tüm bayt içeriğini hedefe yazar. Aktif sistem kaynağı yalnızca servis ortamında desteklenir."),
            new CloneModeOption(CloneMode.Smart, "Akıllı kopya", "Hedef kökünü temizler ve erişilebilen dosyaları eşler. Canlı sistem kaynağında bazı dosyalar atlanabilir.")
        ];
        _selectedMode = Modes[0];
        _selectedSource = _snapshot.Candidates.FirstOrDefault(candidate => candidate.IsSystemVolume) ?? _snapshot.Candidates.FirstOrDefault();
        _selectedTarget = _snapshot.Candidates.FirstOrDefault(candidate => !candidate.IsSystemVolume && candidate.Id != _selectedSource?.Id);
        _analysisStatus = "Kaynak, hedef ve kopyalama türünü seçip denetimi çalıştırın.";

        _analyzeCommand = new RelayCommand(_ => Analyze(), _ => !IsOperationRunning);
        _savePlanCommand = new RelayCommand(_ => SavePlan(), _ => CanSavePlan);
        _startOperationCommand = new AsyncRelayCommand(_ => StartOperationAsync(), _ => CanStartOperation);
        _cancelOperationCommand = new RelayCommand(_ => CancelOperation(), _ => CanCancelOperation);
        _saveExecutionReportCommand = new RelayCommand(_ => SaveExecutionReport(), _ => CanSaveExecutionReport);
        RefreshCommand = new RelayCommand(_ => Refresh(), _ => !IsOperationRunning);
    }

    public ICommand AnalyzeCommand => _analyzeCommand;

    public ICommand RefreshCommand { get; }

    public ICommand SavePlanCommand => _savePlanCommand;

    public ICommand StartOperationCommand => _startOperationCommand;

    public ICommand CancelOperationCommand => _cancelOperationCommand;

    public ICommand SaveExecutionReportCommand => _saveExecutionReportCommand;

    public IReadOnlyList<CloneModeOption> Modes { get; }

    public CloningWorkspaceSnapshot Snapshot
    {
        get => _snapshot;
        private set => SetProperty(ref _snapshot, value);
    }

    public CloneModeOption SelectedMode
    {
        get => _selectedMode;
        set
        {
            SetProperty(ref _selectedMode, value);
            InvalidateAnalysis();
        }
    }

    public DiskSummary? SelectedSource
    {
        get => _selectedSource;
        set
        {
            SetProperty(ref _selectedSource, value);
            InvalidateAnalysis();
        }
    }

    public DiskSummary? SelectedTarget
    {
        get => _selectedTarget;
        set
        {
            SetProperty(ref _selectedTarget, value);
            InvalidateAnalysis();
        }
    }

    public CloneAnalysisResult? Analysis
    {
        get => _analysis;
        private set
        {
            SetProperty(ref _analysis, value);
            RaisePropertyChanged(nameof(AnalysisChecks));
            RaiseDerivedStateChanged();
        }
    }

    public CloneExecutionResult? LastExecution
    {
        get => _lastExecution;
        private set
        {
            SetProperty(ref _lastExecution, value);
            RaisePropertyChanged(nameof(ExecutionWarnings));
            RaiseDerivedStateChanged();
        }
    }

    public OperationProgressSnapshot? CurrentProgress
    {
        get => _currentProgress;
        private set
        {
            SetProperty(ref _currentProgress, value);
            RaisePropertyChanged(nameof(ProgressPercent));
            RaisePropertyChanged(nameof(ProgressSummary));
            RaisePropertyChanged(nameof(ProgressDetail));
            RaiseDerivedStateChanged();
        }
    }

    public bool ConfirmDestructiveAction
    {
        get => _confirmDestructiveAction;
        set
        {
            SetProperty(ref _confirmDestructiveAction, value);
            RaiseDerivedStateChanged();
        }
    }

    public bool IsOperationRunning
    {
        get => _isOperationRunning;
        private set
        {
            SetProperty(ref _isOperationRunning, value);
            RaiseDerivedStateChanged();
        }
    }

    public IReadOnlyList<CloneAnalysisCheck> AnalysisChecks => Analysis?.Checks ?? Array.Empty<CloneAnalysisCheck>();

    public IReadOnlyList<string> ExecutionWarnings => LastExecution?.Warnings ?? Array.Empty<string>();

    public IReadOnlyList<WorkflowStepItem> WorkflowSteps => BuildWorkflowSteps();

    public bool CanSavePlan => Analysis is not null;

    public bool CanStartOperation => !IsOperationRunning && Analysis?.CanProceed == true && ConfirmDestructiveAction;

    public bool CanCancelOperation => IsOperationRunning;

    public bool CanSaveExecutionReport => LastExecution is not null;

    public double ProgressPercent => CurrentProgress?.Percent ?? 0;

    public string ProgressSummary => CurrentProgress?.Summary ?? "İşlem başlatıldığında ilerleme durumu burada görünür.";

    public string ProgressDetail
    {
        get
        {
            if (CurrentProgress is null)
            {
                return "Henüz çalışan işlem yok.";
            }

            return $"{CurrentProgress.ProcessedLabel} / {CurrentProgress.TotalLabel} · {CurrentProgress.SpeedLabel} · Kalan {CurrentProgress.RemainingLabel}";
        }
    }

    public string NextActionText
    {
        get
        {
            if (IsOperationRunning)
            {
                return "İlerlemeyi izleyin. Gerekirse işlemi iptal edin ve hedef sürücünün kısmi kalabileceğini unutmayın.";
            }

            if (LastExecution is not null)
            {
                return LastExecution.State switch
                {
                    ExecutionState.Succeeded => "İşlem tamamlandı. İsterseniz sonuç raporunu kaydedebilir veya yeni bir eşleşme seçebilirsiniz.",
                    ExecutionState.CompletedWithWarnings => "İşlem uyarılarla tamamlandı. Uyarıları inceleyip sonuç raporunu kaydedin.",
                    ExecutionState.Canceled => "İşlem iptal edildi. Hedef sürücüyü doğrulayıp gerekirse yeniden başlatın.",
                    _ => "İşlem tamamlanamadı. Uyarıları inceleyip yeniden deneyin."
                };
            }

            if (Analysis is null)
            {
                return "Önce kaynak ve hedefi seçip denetimi çalıştırın.";
            }

            if (!Analysis.CanProceed)
            {
                return "Analiz engelleri kaldırılmadan işlem başlatılamaz.";
            }

            if (!ConfirmDestructiveAction)
            {
                return "Başlatmadan önce hedef sürücünün üzerine yazılacağını onaylayın.";
            }

            return "İşlemi başlatın, ilerlemeyi izleyin ve tamamlanınca sonuç raporunu kaydedin.";
        }
    }

    public string ScopeNote
    {
        get
        {
            return SelectedMode.Value switch
            {
                CloneMode.Raw => "Ham kopya bu sürümde sürücü düzeyinde gerçek bayt kopyası yapar. Aktif sistem kaynağı masaüstünde desteklenmez.",
                CloneMode.Smart => "Akıllı kopya dosya temelli eşleme yapar. Hedef kökü temizlenir ve erişilebilen dosyalar kopyalanır.",
                _ => string.Empty
            };
        }
    }

    public string AnalysisStatus
    {
        get => _analysisStatus;
        private set => SetProperty(ref _analysisStatus, value);
    }

    private void Analyze()
    {
        try
        {
            Analysis = _cloneWorkflowService.Analyze(BuildRequest());
            AnalysisStatus = Analysis.Summary;
        }
        catch (Exception ex)
        {
            Analysis = null;
            AnalysisStatus = $"Denetim tamamlanamadı: {ex.Message}";
        }
    }

    private async Task StartOperationAsync()
    {
        if (!CanStartOperation)
        {
            AnalysisStatus = "İşlem için denetimi tamamlayın ve onay kutusunu işaretleyin.";
            return;
        }

        IsOperationRunning = true;
        LastExecution = null;
        CurrentProgress = null;
        _executionCancellationTokenSource = new CancellationTokenSource();
        var progress = new Progress<OperationProgressSnapshot>(snapshot => CurrentProgress = snapshot);

        try
        {
            LastExecution = await _cloneWorkflowService.ExecuteAsync(BuildRequest(), progress, _executionCancellationTokenSource.Token);
            AnalysisStatus = LastExecution.Summary;
        }
        finally
        {
            IsOperationRunning = false;
            _executionCancellationTokenSource?.Dispose();
            _executionCancellationTokenSource = null;
        }
    }

    private void CancelOperation()
    {
        _executionCancellationTokenSource?.Cancel();
        AnalysisStatus = "İptal isteği gönderildi.";
    }

    private void Refresh()
    {
        try
        {
            var previousSourceId = SelectedSource?.Id;
            var previousTargetId = SelectedTarget?.Id;
            Snapshot = _cloneWorkflowService.GetSnapshot();
            _selectedSource = Snapshot.Candidates.FirstOrDefault(candidate => candidate.Id == previousSourceId)
                             ?? Snapshot.Candidates.FirstOrDefault(candidate => candidate.IsSystemVolume)
                             ?? Snapshot.Candidates.FirstOrDefault();
            _selectedTarget = Snapshot.Candidates.FirstOrDefault(candidate => candidate.Id == previousTargetId && candidate.Id != _selectedSource?.Id)
                             ?? Snapshot.Candidates.FirstOrDefault(candidate => candidate.Id != _selectedSource?.Id);
            RaisePropertyChanged(nameof(SelectedSource));
            RaisePropertyChanged(nameof(SelectedTarget));
            InvalidateAnalysis();
            AnalysisStatus = "Sürücü listesi yenilendi.";
        }
        catch (Exception ex)
        {
            AnalysisStatus = $"Sürücü listesi yenilenemedi: {ex.Message}";
        }
    }

    private void SavePlan()
    {
        if (Analysis is null)
        {
            return;
        }

        var dialog = new SaveFileDialog
        {
            Title = "Klonlama doğrulama raporunu kaydet",
            Filter = "Metin Dosyası|*.txt",
            FileName = $"CigerTool-Klonlama-Denetim-{DateTime.Now:yyyyMMdd-HHmm}.txt"
        };

        if (dialog.ShowDialog() != true)
        {
            AnalysisStatus = "Rapor kaydetme işlemi iptal edildi.";
            return;
        }

        var builder = new StringBuilder();
        builder.AppendLine("CigerTool Klonlama Denetim Raporu");
        builder.AppendLine(new string('=', 36));
        builder.AppendLine($"Kopyalama türü: {SelectedMode.Title}");
        builder.AppendLine($"Kaynak: {SelectedSource?.Name ?? "Belirtilmedi"}");
        builder.AppendLine($"Hedef: {SelectedTarget?.Name ?? "Belirtilmedi"}");
        builder.AppendLine($"Durum: {Analysis.Status}");
        builder.AppendLine($"Özet: {Analysis.Summary}");
        builder.AppendLine($"Kapasite karşılaştırması: {Analysis.ComparisonLabel}");
        builder.AppendLine($"Gereken alan: {Analysis.RequiredCapacityLabel}");
        builder.AppendLine();
        builder.AppendLine("Sonraki adım");
        builder.AppendLine(NextActionText);
        builder.AppendLine();
        builder.AppendLine("Kapsam notu");
        builder.AppendLine(ScopeNote);
        builder.AppendLine();
        builder.AppendLine("İş akışı");
        foreach (var step in WorkflowSteps)
        {
            builder.AppendLine($"- {step.Title}: {step.Description}");
        }

        if (AnalysisChecks.Count > 0)
        {
            builder.AppendLine();
            builder.AppendLine("Kontroller ve uyarılar");
            foreach (var check in AnalysisChecks)
            {
                builder.AppendLine($"- [{check.Severity}] {check.Title}: {check.Message}");
            }
        }

        File.WriteAllText(dialog.FileName, builder.ToString(), Encoding.UTF8);
        AnalysisStatus = "Klonlama denetim raporu kaydedildi.";
    }

    private void SaveExecutionReport()
    {
        if (LastExecution is null)
        {
            return;
        }

        var dialog = new SaveFileDialog
        {
            Title = "Klonlama sonuç raporunu kaydet",
            Filter = "Metin Dosyası|*.txt",
            FileName = $"CigerTool-Klonlama-Sonuc-{DateTime.Now:yyyyMMdd-HHmm}.txt"
        };

        if (dialog.ShowDialog() != true)
        {
            AnalysisStatus = "Sonuç raporu kaydetme işlemi iptal edildi.";
            return;
        }

        var builder = new StringBuilder();
        builder.AppendLine("CigerTool Klonlama Sonuç Raporu");
        builder.AppendLine(new string('=', 34));
        builder.AppendLine($"Kopyalama türü: {LastExecution.ModeLabel}");
        builder.AppendLine($"Kaynak: {LastExecution.SourceName}");
        builder.AppendLine($"Hedef: {LastExecution.TargetName}");
        builder.AppendLine($"Durum: {LastExecution.StatusLabel}");
        builder.AppendLine($"Özet: {LastExecution.Summary}");
        builder.AppendLine($"İşlenen veri: {ByteSizeFormatter.Format(LastExecution.ProcessedBytes)} / {ByteSizeFormatter.Format(LastExecution.TotalBytes)}");
        builder.AppendLine($"Taşınan öğe sayısı: {LastExecution.CopiedItems}");
        builder.AppendLine();

        if (LastExecution.Notes.Count > 0)
        {
            builder.AppendLine("Notlar");
            foreach (var note in LastExecution.Notes)
            {
                builder.AppendLine($"- {note}");
            }

            builder.AppendLine();
        }

        if (ExecutionWarnings.Count > 0)
        {
            builder.AppendLine("Uyarılar");
            foreach (var warning in ExecutionWarnings)
            {
                builder.AppendLine($"- {warning}");
            }
        }

        File.WriteAllText(dialog.FileName, builder.ToString(), Encoding.UTF8);

        _operationLogService.Record(
            OperationSeverity.Info,
            "Klonlama",
            "Klonlama sonuç raporu kaydedildi.",
            "cloning.result.saved",
            new Dictionary<string, string>
            {
                ["path"] = dialog.FileName,
                ["state"] = LastExecution.State.ToString()
            });

        AnalysisStatus = "Klonlama sonuç raporu kaydedildi.";
    }

    private CloneWorkflowRequest BuildRequest() => new(SelectedMode.Value, SelectedSource?.Id, SelectedTarget?.Id);

    private IReadOnlyList<WorkflowStepItem> BuildWorkflowSteps()
    {
        var hasSelections = SelectedSource is not null && SelectedTarget is not null;
        var analyzed = Analysis is not null;
        var started = CurrentProgress is not null || LastExecution is not null;
        var finished = LastExecution is not null;

        return
        [
            new WorkflowStepItem("Kaynağı seçin", "Kopyalanacak sürücüyü belirleyin.", !hasSelections, hasSelections),
            new WorkflowStepItem("Hedefi seçin", "Verinin yazılacağı sürücüyü belirleyin.", hasSelections && !analyzed, analyzed),
            new WorkflowStepItem("Denetimi çalıştırın", "Boyut, güvenlik ve kapsam kuralları doğrulanır.", analyzed && !CanStartOperation && !started, analyzed),
            new WorkflowStepItem("İşlemi başlatın", "Hedefin üzerine yazılacağını onaylayıp gerçek yürütmeyi başlatın.", analyzed && CanStartOperation && !started, started),
            new WorkflowStepItem("İlerlemeyi izleyin", "Hız, işlenen veri ve mevcut öğe burada izlenir.", IsOperationRunning, !IsOperationRunning && started),
            new WorkflowStepItem("Sonucu kaydedin", "İşlem sonrası raporu dışa aktarın ve günlükleri saklayın.", finished && LastExecution is not null, false)
        ];
    }

    private void InvalidateAnalysis()
    {
        Analysis = null;
        LastExecution = null;
        CurrentProgress = null;
        ConfirmDestructiveAction = false;
        AnalysisStatus = "Seçimler güncellendi. Devam etmek için denetimi yeniden çalıştırın.";
    }

    private void RaiseDerivedStateChanged()
    {
        RaisePropertyChanged(nameof(WorkflowSteps));
        RaisePropertyChanged(nameof(ExecutionWarnings));
        RaisePropertyChanged(nameof(CanSavePlan));
        RaisePropertyChanged(nameof(CanStartOperation));
        RaisePropertyChanged(nameof(CanCancelOperation));
        RaisePropertyChanged(nameof(CanSaveExecutionReport));
        RaisePropertyChanged(nameof(NextActionText));
        RaisePropertyChanged(nameof(ScopeNote));
        RaisePropertyChanged(nameof(ProgressPercent));
        RaisePropertyChanged(nameof(ProgressSummary));
        RaisePropertyChanged(nameof(ProgressDetail));
        _analyzeCommand.RaiseCanExecuteChanged();
        _savePlanCommand.RaiseCanExecuteChanged();
        _startOperationCommand.RaiseCanExecuteChanged();
        _cancelOperationCommand.RaiseCanExecuteChanged();
        _saveExecutionReportCommand.RaiseCanExecuteChanged();
    }
}

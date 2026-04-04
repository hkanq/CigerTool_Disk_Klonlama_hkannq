using CigerTool.Application.Models;

namespace CigerTool.Application.Contracts;

public interface IUsbCreationService
{
    UsbCreatorWorkspaceSnapshot GetSnapshot();

    Task<UsbCreatorOperationResult> RefreshReleaseInfoAsync(CancellationToken cancellationToken = default);

    Task<UsbCreatorOperationResult> RefreshUsbDevicesAsync(CancellationToken cancellationToken = default);

    UsbCreatorOperationResult SetManualImagePath(string imagePath);

    UsbCreatorOperationResult ClearManualImageSelection();

    Task<UsbCreatorOperationResult> DownloadImageAsync(CancellationToken cancellationToken = default);

    Task<UsbCreatorOperationResult> VerifyPreparedImageAsync(CancellationToken cancellationToken = default);

    Task<UsbCreatorOperationResult> WriteImageAsync(string? usbDeviceId, bool confirmedByUser, CancellationToken cancellationToken = default);
}

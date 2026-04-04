using CigerTool.Usb.Models;

namespace CigerTool.Usb.Contracts;

public interface IReleaseSourceResolver
{
    Task<ReleaseManifestSummary> ResolveAsync(string? manualImagePath, CancellationToken cancellationToken = default);
}

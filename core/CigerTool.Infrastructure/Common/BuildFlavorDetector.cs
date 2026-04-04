using System.Reflection;

namespace CigerTool.Infrastructure.Common;

internal static class BuildFlavorDetector
{
    private const string WinPeAssemblyToken = "WinPE";

    public static bool IsWinPeFlavor()
    {
        if (string.Equals(
                System.Environment.GetEnvironmentVariable("CIGERTOOL_FORCE_WINPE"),
                "1",
                StringComparison.OrdinalIgnoreCase))
        {
            return true;
        }

        var entryAssemblyName = Assembly.GetEntryAssembly()?.GetName().Name;
        if (!string.IsNullOrWhiteSpace(entryAssemblyName) &&
            entryAssemblyName.Contains(WinPeAssemblyToken, StringComparison.OrdinalIgnoreCase))
        {
            return true;
        }

        var friendlyName = AppDomain.CurrentDomain.FriendlyName;
        return !string.IsNullOrWhiteSpace(friendlyName) &&
               friendlyName.Contains(WinPeAssemblyToken, StringComparison.OrdinalIgnoreCase);
    }
}

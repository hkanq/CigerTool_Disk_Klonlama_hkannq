using System.Windows;
using System.IO;
using CigerTool.Infrastructure.Storage;

namespace CigerTool.App.Composition;

public static class UserFriendlyErrorReporter
{
    public static void Report(Exception exception, string area)
    {
        try
        {
            var logDirectory = RuntimeAppPathService.GetCrashLogDirectory();
            Directory.CreateDirectory(logDirectory);
            var crashPath = Path.Combine(logDirectory, "cigertool-crash.log");
            var line = $"[{DateTimeOffset.Now:yyyy-MM-dd HH:mm:ss}] {area}{Environment.NewLine}{exception}{Environment.NewLine}{Environment.NewLine}";
            File.AppendAllText(crashPath, line);
        }
        catch
        {
        }

        MessageBox.Show(
            "CigerTool beklenmeyen bir hata ile karşılaştı. Ayrıntılar günlük dosyasına yazıldı.",
            "CigerTool",
            MessageBoxButton.OK,
            MessageBoxImage.Warning);
    }
}

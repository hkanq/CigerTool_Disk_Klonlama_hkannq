using System.Diagnostics;
using CigerTool.Application.Contracts;
using CigerTool.Application.Models;
using CigerTool.Domain.Enums;
using CigerTool.Domain.Models;

namespace CigerTool.Infrastructure.Tools;

public sealed class ToolLaunchService(
    IOperationLogService logService,
    IAppPathService appPathService) : IToolLaunchService
{
    public ToolLaunchResult Launch(ToolDefinition tool)
    {
        try
        {
            if (!tool.Exists || !tool.CanLaunch)
            {
                logService.Record(
                    OperationSeverity.Warning,
                    "Tools",
                    $"{tool.Name} su anda calistirilabilir degil.",
                    "tools.launch.unavailable",
                    new Dictionary<string, string>
                    {
                        ["tool"] = tool.Name,
                        ["status"] = tool.AvailabilityStatus
                    });

                return new ToolLaunchResult(false, $"{tool.Name}: {tool.AvailabilityStatus}");
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = tool.ResolvedExecutablePath,
                UseShellExecute = true
            };

            if (!string.IsNullOrWhiteSpace(tool.Arguments))
            {
                startInfo.Arguments = ExpandPathTokens(System.Environment.ExpandEnvironmentVariables(tool.Arguments));
            }

            var workingDirectory = Path.GetDirectoryName(tool.ResolvedExecutablePath);
            if (!string.IsNullOrWhiteSpace(workingDirectory) && Directory.Exists(workingDirectory))
            {
                startInfo.WorkingDirectory = workingDirectory;
            }

            Process.Start(startInfo);

            logService.Record(
                OperationSeverity.Info,
                "Tools",
                $"{tool.Name} baslatildi.",
                "tools.launch.success",
                new Dictionary<string, string>
                {
                    ["tool"] = tool.Name,
                    ["path"] = tool.ResolvedExecutablePath
                });

            return new ToolLaunchResult(true, $"{tool.Name} baslatildi.");
        }
        catch (Exception ex)
        {
            logService.Record(
                OperationSeverity.Error,
                "Tools",
                $"{tool.Name} baslatilirken hata olustu.",
                "tools.launch.failure",
                new Dictionary<string, string>
                {
                    ["tool"] = tool.Name,
                    ["error"] = ex.Message
                });

            return new ToolLaunchResult(false, $"{tool.Name} acilamadi: {ex.Message}");
        }
    }

    private string ExpandPathTokens(string value)
    {
        var paths = appPathService.GetPaths();
        return value
            .Replace("{BaseDirectory}", paths.BaseDirectory, StringComparison.OrdinalIgnoreCase)
            .Replace("{ToolsDirectory}", paths.ToolsDirectory, StringComparison.OrdinalIgnoreCase)
            .Replace("{LogDirectory}", paths.LogDirectory, StringComparison.OrdinalIgnoreCase)
            .Replace("{DataRoot}", paths.DataRoot, StringComparison.OrdinalIgnoreCase);
    }
}

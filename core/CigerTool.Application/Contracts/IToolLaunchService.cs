using CigerTool.Application.Models;
using CigerTool.Domain.Models;

namespace CigerTool.Application.Contracts;

public interface IToolLaunchService
{
    ToolLaunchResult Launch(ToolDefinition tool);
}

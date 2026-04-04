using CigerTool.Domain.Models;

namespace CigerTool.Application.Contracts;

public interface IEnvironmentProfileService
{
    AppEnvironmentProfile GetCurrentProfile();
}

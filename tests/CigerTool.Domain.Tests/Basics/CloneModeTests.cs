using CigerTool.Domain.Enums;
using Xunit;

namespace CigerTool.Domain.Tests.Basics;

public sealed class CloneModeTests
{
    [Fact]
    public void CloneMode_ShouldExposeExpectedValues()
    {
        Assert.Contains(CloneMode.Raw, Enum.GetValues<CloneMode>());
        Assert.Contains(CloneMode.Smart, Enum.GetValues<CloneMode>());
    }
}

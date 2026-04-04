using CigerTool.Application.Models;
using Xunit;

namespace CigerTool.Application.Tests.Basics;

public sealed class ApplicationSettingsTests
{
    [Fact]
    public void ApplicationSettings_ShouldPreserveConfiguredValues()
    {
        var settings = new ApplicationSettings(
            ProductName: "CigerTool",
            Language: "tr-TR",
            DefaultChannel: "stable",
            DefaultManifestUrl: null,
            UseTurkishDefaults: true,
            PreferSingleFilePublishing: true);

        Assert.Equal("CigerTool", settings.ProductName);
        Assert.True(settings.UseTurkishDefaults);
    }
}

using CigerTool.App.Models;

namespace CigerTool.App.ViewModels;

public sealed class NavigationItemViewModel : ViewModelBase
{
    private bool _isSelected;

    public NavigationItemViewModel(
        NavigationTarget target,
        string title,
        string subtitle,
        string glyph)
    {
        Target = target;
        Title = title;
        Subtitle = subtitle;
        Glyph = glyph;
    }

    public NavigationTarget Target { get; }

    public string Title { get; }

    public string Subtitle { get; }

    public string Glyph { get; }

    public bool IsSelected
    {
        get => _isSelected;
        set => SetProperty(ref _isSelected, value);
    }
}

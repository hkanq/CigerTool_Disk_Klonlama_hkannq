using System.Globalization;
using System.Windows.Data;
using CigerTool.Domain.Enums;

namespace CigerTool.App.Converters;

public sealed class CloneSuitabilityStatusToFriendlyTextConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value switch
        {
            CloneSuitabilityStatus.Ready => "Hazır",
            CloneSuitabilityStatus.Caution => "Dikkatli ilerleyin",
            CloneSuitabilityStatus.Blocked => "Devam edilemez",
            _ => "Belirsiz"
        };
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        throw new NotSupportedException();
    }
}

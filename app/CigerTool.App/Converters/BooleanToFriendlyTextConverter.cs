using System.Globalization;
using System.Windows.Data;

namespace CigerTool.App.Converters;

public sealed class BooleanToFriendlyTextConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        var optionPair = (parameter as string)?.Split('|', 2);
        var trueText = optionPair?.ElementAtOrDefault(0) ?? "Evet";
        var falseText = optionPair?.ElementAtOrDefault(1) ?? "Hayır";

        return value is true ? trueText : falseText;
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        throw new NotSupportedException();
    }
}

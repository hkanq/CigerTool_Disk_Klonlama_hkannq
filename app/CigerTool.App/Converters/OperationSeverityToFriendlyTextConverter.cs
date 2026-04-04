using System.Globalization;
using System.Windows.Data;
using CigerTool.Domain.Enums;

namespace CigerTool.App.Converters;

public sealed class OperationSeverityToFriendlyTextConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value switch
        {
            OperationSeverity.Info => "Bilgi",
            OperationSeverity.Warning => "Uyarı",
            OperationSeverity.Error => "Hata",
            _ => "Bilgi"
        };
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        throw new NotSupportedException();
    }
}

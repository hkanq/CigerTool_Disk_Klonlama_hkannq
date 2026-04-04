using System.Windows;
using System.Windows.Threading;
using CigerTool.App.Composition;

namespace CigerTool.App;

public partial class App : System.Windows.Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        DispatcherUnhandledException += OnDispatcherUnhandledException;
        AppDomain.CurrentDomain.UnhandledException += OnCurrentDomainUnhandledException;
        TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;

        try
        {
            var shell = AppBootstrapper.CreateShellViewModel();
            var window = new MainWindow
            {
                DataContext = shell
            };

            MainWindow = window;
            window.Show();
        }
        catch (Exception exception)
        {
            UserFriendlyErrorReporter.Report(exception, "Startup");
            Shutdown(-1);
        }
    }

    private void OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        UserFriendlyErrorReporter.Report(e.Exception, "UI");
        e.Handled = true;
    }

    private void OnCurrentDomainUnhandledException(object? sender, UnhandledExceptionEventArgs e)
    {
        if (e.ExceptionObject is Exception exception)
        {
            UserFriendlyErrorReporter.Report(exception, "AppDomain");
        }
    }

    private void OnUnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
    {
        UserFriendlyErrorReporter.Report(e.Exception, "Task");
        e.SetObserved();
    }
}

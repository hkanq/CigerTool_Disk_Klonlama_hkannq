using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Security.Principal;
using Microsoft.Win32.SafeHandles;
using CigerTool.Usb.Models;

namespace CigerTool.Usb.Services;

internal sealed class RawDiskWriter
{
    private const uint GenericRead = 0x80000000;
    private const uint GenericWrite = 0x40000000;
    private const uint FileShareRead = 0x00000001;
    private const uint FileShareWrite = 0x00000002;
    private const uint OpenExisting = 3;
    private const uint FsctlLockVolume = 0x00090018;
    private const uint FsctlUnlockVolume = 0x0009001C;
    private const uint FsctlDismountVolume = 0x00090020;
    private const int BufferSize = 1024 * 1024;

    public bool IsAdministrator()
    {
        using var identity = WindowsIdentity.GetCurrent();
        var principal = new WindowsPrincipal(identity);
        return principal.IsInRole(WindowsBuiltInRole.Administrator);
    }

    public async Task WriteImageAsync(string imagePath, UsbPhysicalDeviceInfo device, CancellationToken cancellationToken)
    {
        var volumeHandles = new List<SafeFileHandle>();

        try
        {
            foreach (var volume in device.MountedVolumes)
            {
                var handle = OpenDevice($@"\\.\{volume.TrimEnd('\\')}", write: true);
                volumeHandles.Add(handle);
                TryControlVolume(handle, FsctlLockVolume);
                TryControlVolume(handle, FsctlDismountVolume);
            }

            using var diskHandle = OpenDevice(device.PhysicalPath, write: true);
            using var diskStream = new FileStream(diskHandle, FileAccess.ReadWrite, BufferSize, isAsync: false);
            using var imageStream = new FileStream(imagePath, FileMode.Open, FileAccess.Read, FileShare.Read, BufferSize, useAsync: false);
            diskStream.Position = 0;

            var buffer = new byte[BufferSize];
            while (true)
            {
                var read = await imageStream.ReadAsync(buffer.AsMemory(0, buffer.Length), cancellationToken);
                if (read == 0)
                {
                    break;
                }

                await diskStream.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
            }

            await diskStream.FlushAsync(cancellationToken);
            FlushFileBuffers(diskHandle);
        }
        finally
        {
            foreach (var handle in volumeHandles)
            {
                try
                {
                    TryControlVolume(handle, FsctlUnlockVolume);
                }
                finally
                {
                    handle.Dispose();
                }
            }
        }
    }

    public async Task<string> ComputeFileSha256Async(string filePath, CancellationToken cancellationToken)
    {
        await using var stream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, BufferSize, useAsync: true);
        return await ComputeSha256Async(stream, stream.Length, cancellationToken);
    }

    public async Task<string> ComputeDeviceSha256Async(string physicalPath, long length, CancellationToken cancellationToken)
    {
        using var handle = OpenDevice(physicalPath, write: false);
        await using var stream = new FileStream(handle, FileAccess.Read, BufferSize, isAsync: false);
        stream.Position = 0;
        return await ComputeSha256Async(stream, length, cancellationToken);
    }

    private static async Task<string> ComputeSha256Async(Stream stream, long length, CancellationToken cancellationToken)
    {
        using var sha256 = SHA256.Create();
        var buffer = new byte[BufferSize];
        long remaining = length;

        while (remaining > 0)
        {
            var requested = (int)Math.Min(buffer.Length, remaining);
            var read = await stream.ReadAsync(buffer.AsMemory(0, requested), cancellationToken);
            if (read == 0)
            {
                throw new IOException("SHA-256 hesaplanirken beklenmeyen dosya sonuna ulasildi.");
            }

            sha256.TransformBlock(buffer, 0, read, null, 0);
            remaining -= read;
        }

        sha256.TransformFinalBlock(Array.Empty<byte>(), 0, 0);
        return Convert.ToHexString(sha256.Hash!).ToLowerInvariant();
    }

    private static SafeFileHandle OpenDevice(string path, bool write)
    {
        var desiredAccess = write ? GenericRead | GenericWrite : GenericRead;
        var handle = CreateFile(path, desiredAccess, FileShareRead | FileShareWrite, IntPtr.Zero, OpenExisting, 0, IntPtr.Zero);

        if (handle.IsInvalid)
        {
            var error = Marshal.GetLastWin32Error();
            throw new IOException(
                $"Aygita erisilemedi '{path}': {new Win32Exception(error).Message}",
                new Win32Exception(error));
        }

        return handle;
    }

    private static void TryControlVolume(SafeFileHandle handle, uint controlCode)
    {
        DeviceIoControl(handle, controlCode, IntPtr.Zero, 0, IntPtr.Zero, 0, out _, IntPtr.Zero);
    }

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern SafeFileHandle CreateFile(
        string lpFileName,
        uint dwDesiredAccess,
        uint dwShareMode,
        IntPtr lpSecurityAttributes,
        uint dwCreationDisposition,
        uint dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool DeviceIoControl(
        SafeFileHandle hDevice,
        uint dwIoControlCode,
        IntPtr lpInBuffer,
        int nInBufferSize,
        IntPtr lpOutBuffer,
        int nOutBufferSize,
        out int lpBytesReturned,
        IntPtr lpOverlapped);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool FlushFileBuffers(SafeFileHandle hFile);
}

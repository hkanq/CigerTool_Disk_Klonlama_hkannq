# User USB Creation Flow

## Goal

This document defines the intended end-user flow for creating a CigerTool OS USB from the desktop app.

## Standard Flow

1. Open `USB Creator`.
2. Click `Release Yenile`.
3. Review release mode, version, image name, size, and notes.
4. If needed, use `Manual Dosya Sec` instead of manifest discovery.
5. Click `Image Indir` when the source is manifest-based and the image is not yet local.
6. Click `Checksum Dogrula`.
7. Click `USB Tara`.
8. Review the detected removable USB devices and their safety status.
9. Select the intended USB target.
10. Check the destructive confirmation checkbox.
11. Click `USB'ye Yaz`.
12. Confirm the final warning dialog.
13. Wait for write and post-write validation to complete.

## Manual Flow

1. Open `USB Creator`.
2. Click `Manual Dosya Sec`.
3. Select a previously downloaded image file.
4. Review the resolved local image path.
5. Run `Checksum Dogrula`.
6. Continue with USB selection and write confirmation.

## Local Override Flow

1. Place a valid `release-source.override.json` file in a supported override location.
2. Open `USB Creator`.
3. Click `Release Yenile`.
4. Confirm that the UI reports `Local Override` mode.
5. Continue with download or local image usage depending on the override type.

Supported override locations:

- `<DataRoot>\Config\release-source.override.json`
- `<BaseDirectory>\Config\release-source.override.json`
- `<BaseDirectory>\CigerTool\Config\release-source.override.json`
- `%ProgramData%\CigerTool\release-source.override.json`

## Expected Error Handling

The app should explain these situations clearly:

- manifest URL is not configured
- network failure while refreshing release info
- override file is invalid
- image download fails
- checksum does not match
- no eligible USB device is found
- selected device is too small
- app is not running as administrator
- write validation fails after image copy

## Scope Boundary

This flow writes an existing CigerTool OS image only.

The app may store downloads, cache, and logs either under `%LocalAppData%\CigerTool` or beside the app in `.\Data`, depending on standard vs portable deployment mode.

It does not:

- build WinPE
- generate the CigerTool OS image
- install Windows ADK
- construct boot media outside the downloaded or user-selected prebuilt image

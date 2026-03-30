from __future__ import annotations

import argparse
from pathlib import Path
import sys


def to_grub_path(path: Path, media_root: Path) -> str:
    relative = path.resolve().relative_to(media_root.resolve())
    return "/" + str(relative).replace("\\", "/")


def grub_label(value: str) -> str:
    return value.replace('"', "").strip()


def grub_literal(value: str) -> str:
    return value.replace("'", "")


def quoted_message(message: str) -> str:
    return message.replace('"', "").strip()


def indent_lines(lines: list[str], level: int = 1) -> list[str]:
    prefix = "    " * level
    return [f"{prefix}{line}" if line else "" for line in lines]


def render_windows_entry(
    name: str,
    iso_path: str,
    wimboot_path: str | None,
    efi_boot_path: str | None,
    failure_reason: str | None,
) -> list[str]:
    failure = quoted_message(failure_reason or "missing boot files")
    efi_path = grub_literal(efi_boot_path or "/efi/boot/bootx64.efi")
    lines = [
        f'menuentry "Windows: {grub_label(name)}" {{',
        f"    set isofile='{grub_literal(iso_path)}'",
        '    loopback loop "$isofile"',
    ]
    if wimboot_path:
        lines.extend(
            [
                f"    if [ -f {wimboot_path} ] && [ -f (loop)/sources/boot.wim ] && [ -f (loop)/boot/boot.sdi ]; then",
                f"        linux {wimboot_path}",
                "        if [ -f (loop)/efi/microsoft/boot/bcd ]; then",
                "            initrd newc:bootmgfw.efi:(loop)/efi/microsoft/boot/bootmgfw.efi newc:bcd:(loop)/efi/microsoft/boot/bcd newc:boot.sdi:(loop)/boot/boot.sdi newc:boot.wim:(loop)/sources/boot.wim",
                "            boot",
                "        fi",
                "        if [ -f (loop)/bootmgr ] && [ -f (loop)/boot/bcd ]; then",
                "            initrd newc:bootmgr:(loop)/bootmgr newc:bcd:(loop)/boot/bcd newc:boot.sdi:(loop)/boot/boot.sdi newc:boot.wim:(loop)/sources/boot.wim",
                "            boot",
                "        fi",
                "    fi",
            ]
        )
    lines.extend(
        [
            f"    if [ -f (loop){efi_path} ]; then",
            f"        chainloader (loop){efi_path}",
            "        boot",
            "    fi",
            f'    echo "{failure}"',
            "    sleep 6",
            "}",
        ]
    )
    return lines


def render_linux_entry(name: str, iso_path: str, label: str, kernel: str | None, initrd: str | None, kernel_args: str) -> list[str]:
    missing_kernel = quoted_message("unsupported kernel")
    missing_initrd = quoted_message("missing boot files")
    safe_kernel = kernel or ""
    safe_initrd = initrd or ""
    return [
        f'menuentry "{grub_label(label)}: {grub_label(name)}" {{',
        f"    set isofile='{grub_literal(iso_path)}'",
        '    loopback loop "$isofile"',
        f"    if [ ! -f (loop){safe_kernel} ]; then",
        f'        echo "{missing_kernel}"',
        "        sleep 6",
        "        return",
        "    fi",
        f"    if [ ! -f (loop){safe_initrd} ]; then",
        f'        echo "{missing_initrd}"',
        "        sleep 6",
        "        return",
        "    fi",
        f"    linux (loop){safe_kernel} {kernel_args} ---",
        f"    initrd (loop){safe_initrd}",
        "}",
    ]


def render_ubuntu_debian_entry(name: str, iso_path: str, kernel: str | None, initrd: str | None) -> list[str]:
    is_debian = "debian" in name.lower()
    kernel_args = "boot=live findiso=$isofile" if is_debian else "boot=casper iso-scan/filename=$isofile noeject noprompt splash"
    return render_linux_entry(name, iso_path, "Linux", kernel, initrd, kernel_args)


def render_arch_entry(name: str, iso_path: str, kernel: str | None, initrd: str | None) -> list[str]:
    missing_kernel = quoted_message("unsupported kernel")
    missing_initrd = quoted_message("missing boot files")
    safe_kernel = kernel or ""
    safe_initrd = initrd or ""
    return [
        f'menuentry "Arch: {grub_label(name)}" {{',
        f"    set isofile='{grub_literal(iso_path)}'",
        '    search --set=root --file "$isofile"',
        "    probe -u $root --set=rootuuid",
        '    loopback loop "$isofile"',
        f"    if [ ! -f (loop){safe_kernel} ]; then",
        f'        echo "{missing_kernel}"',
        "        sleep 6",
        "        return",
        "    fi",
        f"    if [ ! -f (loop){safe_initrd} ]; then",
        f'        echo "{missing_initrd}"',
        "        sleep 6",
        "        return",
        "    fi",
        f"    linux (loop){safe_kernel} img_dev=/dev/disk/by-uuid/${{rootuuid}} img_loop=$isofile earlymodules=loop",
        f"    initrd (loop){safe_initrd}",
        "}",
    ]


def render_custom_entry(name: str, iso_path: str, config_path: str) -> list[str]:
    return [
        f'menuentry "Custom: {grub_label(name)}" {{',
        f"    set isofile='{grub_literal(iso_path)}'",
        f"    configfile {grub_literal(config_path)}",
        "}",
    ]


def render_chainload_entry(
    label: str,
    name: str,
    iso_path: str,
    efi_boot_path: str | None,
    failure_reason: str | None,
) -> list[str]:
    failure = quoted_message(failure_reason or "missing boot files")
    efi_path = grub_literal(efi_boot_path or "/efi/boot/bootx64.efi")
    return [
        f'menuentry "{grub_label(label)}: {grub_label(name)}" {{',
        f"    set isofile='{grub_literal(iso_path)}'",
        '    loopback loop "$isofile"',
        f"    if [ -f (loop){efi_path} ]; then",
        f"        chainloader (loop){efi_path}",
        "        boot",
        "    fi",
        f'    echo "{failure}"',
        "    sleep 6",
        "}",
    ]


def render_fallback_entry(name: str, iso_path: str, failure_reason: str | None) -> list[str]:
    failure = quoted_message(failure_reason or "incompatible ISO type")
    return [
        f'menuentry "Unsupported: {grub_label(name)}" {{',
        f'    echo "{failure}"',
        f'    echo "{grub_literal(iso_path)}"',
        "    sleep 6",
        "}",
    ]


def render_cigertool_live_entry(wimboot_path: str | None) -> list[str]:
    failure = quoted_message("CigerTool Live boot assets missing")
    if not wimboot_path:
        return [
            'menuentry "CigerTool Live" {',
            f'    echo "{failure}"',
            "    sleep 5",
            "}",
            "",
        ]

    return [
        'menuentry "CigerTool Live" {',
        f"    if [ -f {wimboot_path} ] && [ -f /sources/boot.wim ] && [ -f /boot/boot.sdi ] && [ -f /EFI/Microsoft/Boot/BCD ]; then",
        f"        linux {wimboot_path}",
        "        if [ -f /EFI/Microsoft/Boot/bootmgfw.efi ]; then",
        "            initrd newc:bootmgfw.efi:/EFI/Microsoft/Boot/bootmgfw.efi newc:bcd:/EFI/Microsoft/Boot/BCD newc:boot.sdi:/boot/boot.sdi newc:boot.wim:/sources/boot.wim",
        "            boot",
        "        fi",
        "        if [ -f /bootmgr ] && [ -f /boot/BCD ]; then",
        "            initrd newc:bootmgr:/bootmgr newc:bcd:/boot/BCD newc:boot.sdi:/boot/boot.sdi newc:boot.wim:/sources/boot.wim",
        "            boot",
        "        fi",
        "    fi",
        f'    echo "{failure}"',
        "    sleep 5",
        "}",
        "",
    ]


def render_iso_entry(entry, media_root: Path, wimboot_path: str | None) -> list[str]:
    from cigertool.models import BootStrategy, IsoProfile, IsoSupportStatus

    iso_grub_path = to_grub_path(Path(entry.path), media_root)
    companion_cfg = (
        to_grub_path(Path(entry.companion_config), media_root)
        if entry.companion_config and Path(entry.companion_config).exists()
        else ""
    )
    if entry.support_status is IsoSupportStatus.UNSUPPORTED:
        return render_fallback_entry(entry.name, iso_grub_path, entry.failure_reason)
    if entry.boot_strategy is BootStrategy.CUSTOM_CONFIG and companion_cfg:
        return render_custom_entry(entry.name, iso_grub_path, companion_cfg)
    if entry.profile is IsoProfile.WINDOWS:
        return render_windows_entry(
            entry.name,
            iso_grub_path,
            wimboot_path,
            entry.efi_boot_path,
            entry.failure_reason,
        )
    if entry.profile is IsoProfile.UBUNTU_DEBIAN:
        return render_ubuntu_debian_entry(entry.name, iso_grub_path, entry.kernel_path, entry.initrd_path)
    if entry.profile is IsoProfile.ARCH:
        return render_arch_entry(entry.name, iso_grub_path, entry.kernel_path, entry.initrd_path)
    if entry.boot_strategy is BootStrategy.EFI_CHAINLOAD:
        return render_chainload_entry("Tool ISO", entry.name, iso_grub_path, entry.efi_boot_path, entry.failure_reason)
    return render_fallback_entry(entry.name, iso_grub_path, entry.failure_reason)


def render_iso_section(title: str, entries: list, media_root: Path, wimboot_path: str | None) -> list[str]:
    lines = [f'submenu "{grub_label(title)}" {{']
    for entry in entries:
        lines.extend(indent_lines(render_iso_entry(entry, media_root, wimboot_path), 1))
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append("}")
    return lines


def render_iso_library(entries: list, media_root: Path, wimboot_path: str | None) -> list[str]:
    section_titles = {
        "windows": "Windows ISO'lari",
        "linux": "Linux ISO'lari",
        "tools": "Arac ve Kurtarma ISO'lari",
        "legacy": "Legacy ISO Library",
        "other": "Diger ISO'lar",
        "unsupported": "Desteklenmeyen ISO'lar",
    }
    section_order = ["windows", "linux", "tools", "legacy", "other", "unsupported"]
    grouped: dict[str, list] = {section: [] for section in section_order}

    for entry in entries:
        target_section = entry.library_section or entry.category.value
        if getattr(entry, "support_status", None) and entry.support_status.value == "unsupported":
            target_section = "unsupported"
        grouped.setdefault(target_section, []).append(entry)

    lines = ['submenu "ISO Library" {']
    rendered_section = False
    for section in section_order:
        bucket = grouped.get(section, [])
        if not bucket:
            continue
        lines.extend(indent_lines(render_iso_section(section_titles[section], bucket, media_root, wimboot_path), 1))
        lines.append("")
        rendered_section = True

    if not rendered_section:
        lines.extend(
            indent_lines(
                [
                    'menuentry "ISO bulunamadi" {',
                    '    echo "incompatible ISO type"',
                    "    sleep 5",
                    "}",
                ],
                1,
            )
        )
    elif lines[-1] == "":
        lines.pop()

    lines.append("}")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--wimboot-path", default="")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))

    from cigertool.services.multiboot_service import MultibootService

    media_root = Path(args.media_root).resolve()
    output_path = Path(args.output).resolve()
    service = MultibootService()

    roots = [
        media_root / "isos" / "windows",
        media_root / "isos" / "linux",
        media_root / "isos" / "tools",
        media_root / "iso-library",
    ]
    entries = service.scan_isos([path for path in roots if path.exists()])
    wimboot_path = args.wimboot_path or ""

    lines = [
        "set default=0",
        "set timeout=12",
        "",
        "insmod part_gpt",
        "insmod part_msdos",
        "insmod fat",
        "insmod ntfs",
        "insmod exfat",
        "insmod iso9660",
        "insmod udf",
        "insmod loopback",
        "insmod chain",
        "insmod search",
        "insmod regexp",
        "insmod test",
        "insmod probe",
        "insmod normal",
        "",
        "terminal_output console",
        "",
    ]
    lines.extend(render_cigertool_live_entry(wimboot_path or None))

    for entry in entries:
        reason = entry.failure_reason or ""
        print(f"[{entry.support_status.value.upper()}] {entry.name} :: {reason or 'ready'}")
    lines.extend(render_iso_library(entries, media_root, wimboot_path or None))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

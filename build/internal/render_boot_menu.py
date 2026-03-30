from __future__ import annotations

import argparse
from pathlib import Path


def grub_literal(value: str) -> str:
    return value.replace("'", "")


def indent(lines: list[str], spaces: int = 4) -> list[str]:
    prefix = " " * spaces
    return [f"{prefix}{line}" if line else "" for line in lines]


def render_root_discovery(var_name: str = "cg_root") -> list[str]:
    return [
        f'if search --no-floppy --set={var_name} --file /CigerTool.workspace.json; then',
        f"    set root=${var_name}",
        "fi",
    ]


def render_workspace_entry(
    workspace_loader_path: str,
    workspace_vhd_path: str,
    workspace_bcd_path: str,
) -> list[str]:
    loader = grub_literal(workspace_loader_path)
    vhd = grub_literal(workspace_vhd_path)
    bcd = grub_literal(workspace_bcd_path)
    lines = [
        'menuentry "CigerTool Workspace" {',
        *indent(render_root_discovery("cg_workspace_root")),
        f"    if [ -f /CigerTool.workspace.json ] && [ -f {loader} ] && [ -f {bcd} ] && [ -f {vhd} ]; then",
        '        echo "CigerTool Workspace baslatiliyor..."',
        f"        chainloader {loader}",
        "        boot",
        "    fi",
        '    echo "Workspace boot dosyalari eksik veya hatali"',
        f'    echo "Loader: {loader}"',
        f'    echo "BCD: {bcd}"',
        f'    echo "VHDX: {vhd}"',
        '    echo "Boot Diagnostics menusunu kullanarak dosya durumunu kontrol edin"',
        "    sleep 8",
        "}",
        "",
    ]
    return lines


def render_windows_section(wimboot_path: str) -> list[str]:
    wimboot = grub_literal(wimboot_path)
    return [
        'submenu "Windows ISO\'lari" {',
        *indent(render_root_discovery("cg_windows_root")),
        "    set cg_windows_found=0",
        "    for isofile in /isos/windows/*.iso /isos/windows/*.ISO; do",
        '        if [ -f "$isofile" ]; then',
        "            set cg_windows_found=1",
        "            regexp --set=1 cg_iso_title '.*/([^/]+)\\.[Ii][Ss][Oo]$' \"$isofile\"",
        "            if [ -z \"$cg_iso_title\" ]; then",
        "                regexp --set=1 cg_iso_title '.*/([^/]+)$' \"$isofile\"",
        "            fi",
        '            menuentry "Windows: $cg_iso_title" "$isofile" {',
        '                set isofile="$2"',
        '                loopback loop "$isofile"',
        f"                if [ -n \"{wimboot}\" ] && [ -f {wimboot} ] && [ -f (loop)/sources/boot.wim ] && [ -f (loop)/boot/boot.sdi ]; then",
        f"                    linux {wimboot}",
        "                    if [ -f (loop)/efi/microsoft/boot/bcd ] && [ -f (loop)/efi/microsoft/boot/bootmgfw.efi ]; then",
        "                        initrd newc:bootmgfw.efi:(loop)/efi/microsoft/boot/bootmgfw.efi newc:bcd:(loop)/efi/microsoft/boot/bcd newc:boot.sdi:(loop)/boot/boot.sdi newc:boot.wim:(loop)/sources/boot.wim",
        "                        boot",
        "                    fi",
        "                    if [ -f (loop)/bootmgr ] && [ -f (loop)/boot/bcd ]; then",
        "                        initrd newc:bootmgr:(loop)/bootmgr newc:bcd:(loop)/boot/bcd newc:boot.sdi:(loop)/boot/boot.sdi newc:boot.wim:(loop)/sources/boot.wim",
        "                        boot",
        "                    fi",
        "                fi",
        "                if [ -f (loop)/EFI/BOOT/BOOTX64.EFI ]; then",
        "                    chainloader (loop)/EFI/BOOT/BOOTX64.EFI",
        "                    boot",
        "                fi",
        "                if [ -f (loop)/efi/boot/bootx64.efi ]; then",
        "                    chainloader (loop)/efi/boot/bootx64.efi",
        "                    boot",
        "                fi",
        '                echo "Bu Windows ISO icin uygun boot dosyalari bulunamadi"',
        "                sleep 6",
        "            }",
        "        fi",
        "    done",
        '    if [ "$cg_windows_found" = "0" ]; then',
        '        menuentry "ISO bulunamadi" {',
        '            echo "Bu klasorde Windows ISO bulunamadi"',
        "            sleep 5",
        "        }",
        "    fi",
        "}",
    ]


def render_linux_section() -> list[str]:
    return [
        'submenu "Linux ISO\'lari" {',
        *indent(render_root_discovery("cg_linux_root")),
        "    set cg_linux_found=0",
        "    for isofile in /isos/linux/*.iso /isos/linux/*.ISO; do",
        '        if [ -f "$isofile" ]; then',
        "            set cg_linux_found=1",
        "            regexp --set=1 cg_iso_title '.*/([^/]+)\\.[Ii][Ss][Oo]$' \"$isofile\"",
        "            if [ -z \"$cg_iso_title\" ]; then",
        "                regexp --set=1 cg_iso_title '.*/([^/]+)$' \"$isofile\"",
        "            fi",
        "            regexp --set=1 cg_cfg_base '(.*)\\.[Ii][Ss][Oo]$' \"$isofile\"",
        '            menuentry "Linux: $cg_iso_title" "$isofile" "${cg_cfg_base}.grub.cfg" {',
        '                set isofile="$2"',
        '                set cfgfile="$3"',
        '                if [ -f "$cfgfile" ]; then',
        '                    configfile "$cfgfile"',
        "                fi",
        '                loopback loop "$isofile"',
        '                if regexp ".*(ubuntu|debian|mint|pop-os|kubuntu|xubuntu|zorin).*" "$isofile"; then',
        "                    if [ -f (loop)/casper/vmlinuz ] && [ -f (loop)/casper/initrd ]; then",
        "                        linux (loop)/casper/vmlinuz boot=casper iso-scan/filename=$isofile noeject noprompt splash ---",
        "                        initrd (loop)/casper/initrd",
        "                        boot",
        "                    fi",
        "                    if [ -f (loop)/live/vmlinuz ] && [ -f (loop)/live/initrd.img ]; then",
        "                        linux (loop)/live/vmlinuz boot=live findiso=$isofile ---",
        "                        initrd (loop)/live/initrd.img",
        "                        boot",
        "                    fi",
        "                fi",
        '                if regexp ".*(arch|manjaro|endeavour|garuda).*" "$isofile"; then',
        '                    search --set=root --file "$isofile"',
        "                    probe -u $root --set=rootuuid",
        "                    if [ -f (loop)/arch/boot/x86_64/vmlinuz-linux ] && [ -f (loop)/arch/boot/x86_64/initramfs-linux.img ]; then",
        "                        linux (loop)/arch/boot/x86_64/vmlinuz-linux img_dev=/dev/disk/by-uuid/${rootuuid} img_loop=$isofile earlymodules=loop",
        "                        initrd (loop)/arch/boot/x86_64/initramfs-linux.img",
        "                        boot",
        "                    fi",
        "                fi",
        '                echo "Bu Linux ISO icin uygun kernel bulunamadi"',
        "                sleep 6",
        "            }",
        "        fi",
        "    done",
        '    if [ "$cg_linux_found" = "0" ]; then',
        '        menuentry "ISO bulunamadi" {',
        '            echo "Bu klasorde Linux ISO bulunamadi"',
        "            sleep 5",
        "        }",
        "    fi",
        "}",
    ]


def render_tools_section() -> list[str]:
    return [
        'submenu "Arac ve Kurtarma ISO\'lari" {',
        *indent(render_root_discovery("cg_tools_root")),
        "    set cg_tools_found=0",
        "    for isofile in /isos/tools/*.iso /isos/tools/*.ISO; do",
        '        if [ -f "$isofile" ]; then',
        "            set cg_tools_found=1",
        "            regexp --set=1 cg_iso_title '.*/([^/]+)\\.[Ii][Ss][Oo]$' \"$isofile\"",
        "            if [ -z \"$cg_iso_title\" ]; then",
        "                regexp --set=1 cg_iso_title '.*/([^/]+)$' \"$isofile\"",
        "            fi",
        "            regexp --set=1 cg_cfg_base '(.*)\\.[Ii][Ss][Oo]$' \"$isofile\"",
        '            menuentry "Tool ISO: $cg_iso_title" "$isofile" "${cg_cfg_base}.grub.cfg" {',
        '                set isofile="$2"',
        '                set cfgfile="$3"',
        '                if [ -f "$cfgfile" ]; then',
        '                    configfile "$cfgfile"',
        "                fi",
        '                loopback loop "$isofile"',
        "                if [ -f (loop)/EFI/BOOT/BOOTX64.EFI ]; then",
        "                    chainloader (loop)/EFI/BOOT/BOOTX64.EFI",
        "                    boot",
        "                fi",
        "                if [ -f (loop)/efi/boot/bootx64.efi ]; then",
        "                    chainloader (loop)/efi/boot/bootx64.efi",
        "                    boot",
        "                fi",
        '                echo "Bu tool ISO icin uygun EFI boot dosyasi bulunamadi"',
        "                sleep 6",
        "            }",
        "        fi",
        "    done",
        '    if [ "$cg_tools_found" = "0" ]; then',
        '        menuentry "ISO bulunamadi" {',
        '            echo "Bu klasorde arac ISO bulunamadi"',
        "            sleep 5",
        "        }",
        "    fi",
        "}",
    ]


def render_iso_library(wimboot_path: str) -> list[str]:
    lines = [
        'submenu "ISO Library" {',
        '    menuentry "ISO Library kullanimi" {',
        '        echo "ISO dosyalarini /isos/windows, /isos/linux veya /isos/tools altina kopyalayin"',
        '        echo "Menu her acilista bu dizinleri yeniden tarar"',
        "        sleep 8",
        "    }",
        "",
    ]
    for section in (
        render_windows_section(wimboot_path),
        render_linux_section(),
        render_tools_section(),
    ):
        lines.extend(indent(section))
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append("}")
    return lines


def render_boot_diagnostics(
    workspace_loader_path: str,
    workspace_vhd_path: str,
    workspace_bcd_path: str,
) -> list[str]:
    loader = grub_literal(workspace_loader_path)
    vhd = grub_literal(workspace_vhd_path)
    bcd = grub_literal(workspace_bcd_path)
    return [
        'submenu "Boot Diagnostics" {',
        '    menuentry "Workspace dosyalarini kontrol et" {',
        *indent(render_root_discovery("cg_diag_root"), 8),
        '        echo "Root: $root"',
        "        if [ -f /CigerTool.workspace.json ]; then echo 'Marker: OK'; else echo 'Marker: eksik'; fi",
        f"        if [ -f {loader} ]; then echo 'Loader: OK'; else echo 'Loader: eksik'; fi",
        f"        if [ -f {bcd} ]; then echo 'BCD: OK'; else echo 'BCD: eksik'; fi",
        f"        if [ -f {vhd} ]; then echo 'VHDX: OK'; else echo 'VHDX: eksik'; fi",
        "        echo 'Workspace girisi Setup veya OOBE kullanmaz; dogrudan Boot Manager + VHDX yoluna gider'",
        "        sleep 10",
        "    }",
        '    menuentry "ISO koklerini listele" {',
        *indent(render_root_discovery("cg_iso_diag_root"), 8),
        '        echo "isos/windows" ; ls /isos/windows',
        '        echo "isos/linux" ; ls /isos/linux',
        '        echo "isos/tools" ; ls /isos/tools',
        "        sleep 10",
        "    }",
        "}",
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workspace-loader-path", default="/EFI/Microsoft/Boot/bootmgfw.efi")
    parser.add_argument("--workspace-vhd-path", default="/workspace/CigerToolWorkspace.vhdx")
    parser.add_argument("--workspace-bcd-path", default="/EFI/Microsoft/Boot/BCD")
    parser.add_argument("--wimboot-path", default="/EFI/CigerTool/wimboot")
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "set default=0",
        "set timeout=10",
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
        "insmod search_fs_file",
        "insmod regexp",
        "insmod test",
        "insmod probe",
        "insmod normal",
        "",
        *render_root_discovery(),
        "",
        "terminal_output console",
        "",
    ]
    lines.extend(
        render_workspace_entry(
            args.workspace_loader_path,
            args.workspace_vhd_path,
            args.workspace_bcd_path,
        )
    )
    lines.extend(render_iso_library(args.wimboot_path))
    lines.append("")
    lines.extend(
        render_boot_diagnostics(
            args.workspace_loader_path,
            args.workspace_vhd_path,
            args.workspace_bcd_path,
        )
    )

    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

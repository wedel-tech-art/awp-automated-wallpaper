#!/usr/bin/env python3
"""
AWP-TRANSFER v2.1 – Backup & Transfer Tool (Timeshift style)
===========================================================

📦 -b : Create backup of current AWP state
🚀 -t : Transfer (restore) a selected backup
-l : List available backups

New in v2.1:
- system_files_map.txt inside every backup (shows exact origin of each file)
"""

import os
import shutil
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
AWP_DIR = HOME / "awp"
ARCHIVE_ROOT = HOME / "awp_backups"

def get_de():
    config_path = AWP_DIR / "awp_config.ini"
    if config_path.exists():
        from configparser import ConfigParser
        cp = ConfigParser()
        cp.read(config_path)
        try:
            return cp.get('general', 'os_detected', fallback='generic').lower()
        except:
            pass
    return 'generic'

def get_archive_size(path: Path) -> str:
    total = sum(p.stat().st_size for p in path.rglob('*') if p.is_file())
    return f"{total / 1024 / 1024:.1f} MB"

def dump_dconf(path: str) -> str | None:
    try:
        return subprocess.check_output(["dconf", "dump", path], text=True)
    except:
        return None

def create_backup():
    if not AWP_DIR.exists():
        print(f"❌ AWP folder not found: {AWP_DIR}")
        return

    print("📦 Creating backup of current AWP state")
    print("=" * 50)

    ARCHIVE_ROOT.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    note = input("Optional note (e.g. 'before new sharpen') [Enter for none]: ").strip()
    suffix = f"_{note.replace(' ', '_')}" if note else ""
    archive_name = f"awp_backup_{timestamp}{suffix}"
    archive_path = ARCHIVE_ROOT / archive_name
    archive_path.mkdir()

    print(f"\n📁 Saving to: {archive_path.name}")

    # 1. Copy application
    print("\n1/2 📂 Copying application...")
    app_dest = archive_path / "awp"
    shutil.copytree(AWP_DIR, app_dest, symlinks=True)
    print("   ✅ Done")

    # 2. System files + mapping
    print("\n2/2 🔧 Saving system configuration...")
    system_dir = archive_path / "system_original"
    system_dir.mkdir()

    de = get_de()

    # Files to save: (source_path, backup_name)
    files_to_save = [
        (HOME / ".config/autostart/awp_start.desktop", "autostart.desktop"),
    ]

    if de == 'xfce':
        files_to_save += [
            (HOME / ".config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml", "xfce-keybindings.xml"),
            (HOME / ".config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml", "xfce-panel.xml"),
        ]
    elif de == 'cinnamon':
        files_to_save += [
            (HOME / ".cinnamon/configs/menu@cinnamon.org/0.json", "cinnamon-menu.json"),
        ]

    # dconf paths: (dconf_path, backup_name)
    dconf_paths = []
    if de == 'cinnamon':
        dconf_paths = [("/org/cinnamon/desktop/keybindings/", "cinnamon-keybindings.dconf")]
    elif de == 'gnome':
        dconf_paths = [
            ("/org/gnome/desktop/wm/keybindings/", "gnome-wm-keybindings.dconf"),
            ("/org/gnome/mutter/keybindings/", "gnome-mutter-keybindings.dconf"),
        ]
    elif de == 'mate':
        dconf_paths = [
            ("/org/mate/marco/window-keybindings/", "mate-marco-keybindings.dconf"),
            ("/org/mate/desktop/keybindings/", "mate-desktop-keybindings.dconf"),
        ]

    # Save files and build map
    saved = 0
    map_lines = []
    for src, name in files_to_save:
        if src.exists():
            shutil.copy2(src, system_dir / name)
            map_lines.append(f"{name} → {src}")
            saved += 1

    for dpath, dname in dconf_paths:
        text = dump_dconf(dpath)
        if text:
            (system_dir / dname).write_text(text)
            map_lines.append(f"{dname} → dconf path {dpath}")
            saved += 1

    # Create mapping file
    if map_lines:
        map_path = system_dir / "system_files_map.txt"
        map_path.write_text("\n".join(map_lines) + "\n")
        print("   ✅ system_files_map.txt created (quick reference)")

    # Metadata
    metadata = {
        "created": datetime.now().isoformat(),
        "note": note or "No note",
        "de": de.upper()
    }
    (archive_path / "metadata.json").write_text(json.dumps(metadata, indent=2))

    size = get_archive_size(archive_path)
    print(f"\n🎉 BACKUP COMPLETE ({size})")
    print(f"   📁 {archive_path}")

def list_backups():
    if not ARCHIVE_ROOT.exists() or not any(ARCHIVE_ROOT.iterdir()):
        print("❌ No backups available yet.")
        return

    items = sorted(ARCHIVE_ROOT.iterdir(), key=lambda p: p.name, reverse=True)
    print("📦 Available backups (newest first):\n")
    for i, item in enumerate(items, 1):
        try:
            meta = json.loads((item / "metadata.json").read_text())
            date = datetime.fromisoformat(meta["created"]).strftime("%Y-%m-%d %H:%M")
            note = meta.get("note", "")
            de = meta.get("de", "?")
            size = get_archive_size(item)
            note_str = f" - {note}" if note != "No note" else ""
            print(f" {i:2d}. 📁 {item.name}{note_str} → {date} | {de} | {size}")
        except:
            print(f" {i:2d}. 📁 {item.name}")

def select_backup() -> Path | None:
    items = sorted(ARCHIVE_ROOT.iterdir(), key=lambda p: p.name, reverse=True)
    if not items:
        return None

    choice = input("\nSelect backup number (Enter to quit): ").strip()
    if not choice:
        return None

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]

    print("❌ Invalid selection")
    return None


def transfer_backup(archive_path: Path):
    if not AWP_DIR.exists():
        print(f"❌ AWP folder not found: {AWP_DIR}")
        return

    print(f"\n🚀 Transferring state from {archive_path.name}")

    if not (archive_path / "awp").exists():
        print("❌ Invalid backup (missing awp folder)")
        return

    confirm = input(f"⚠️  This will OVERWRITE your current AWP (~ /awp). Continue? [y/N]: ").lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return False

    # Quick safety backup of current state
    quick_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    quick_backup = ARCHIVE_ROOT / f"awp_pre_transfer_{quick_ts}"
    quick_backup.mkdir()
    print(f"📋 Quick backup of current state to {quick_backup.name}...")
    shutil.copytree(AWP_DIR, quick_backup / "awp", symlinks=True)

    # Transfer application
    shutil.rmtree(AWP_DIR)
    shutil.copytree(archive_path / "awp", AWP_DIR, symlinks=True)
    print("   ✅ Application transferred")

    # Transfer system files
    system_dir = archive_path / "system_original"
    if system_dir.exists():
        print("🔧 Restoring system configuration...")

        # Autostart
        autostart_src = system_dir / "autostart.desktop"
        if autostart_src.exists():
            autostart_dest = HOME / ".config/autostart/awp_start.desktop"
            autostart_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(autostart_src, autostart_dest)
            print("   ✅ autostart restored")

        # XFCE
        if (system_dir / "xfce-keybindings.xml").exists():
            dest = HOME / ".config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(system_dir / "xfce-keybindings.xml", dest)
            print("   ✅ XFCE keybindings restored")

        if (system_dir / "xfce-panel.xml").exists():
            dest = HOME / ".config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(system_dir / "xfce-panel.xml", dest)
            print("   ✅ XFCE panel restored")

        # Cinnamon
        if (system_dir / "cinnamon-menu.json").exists():
            dest = HOME / ".cinnamon/configs/menu@cinnamon.org/0.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(system_dir / "cinnamon-menu.json", dest)
            print("   ✅ Cinnamon menu restored")

        # dconf restore
        de = get_de()
        dconf_loads = {
            'cinnamon': [("/org/cinnamon/desktop/keybindings/", "cinnamon-keybindings.dconf")],
            'gnome': [
                ("/org/gnome/desktop/wm/keybindings/", "gnome-wm-keybindings.dconf"),
                ("/org/gnome/mutter/keybindings/", "gnome-mutter-keybindings.dconf"),
            ],
            'mate': [
                ("/org/mate/marco/window-keybindings/", "mate-marco-keybindings.dconf"),
                ("/org/mate/desktop/keybindings/", "mate-desktop-keybindings.dconf"),
            ],
        }
        for load_path, name in dconf_loads.get(de, []):
            src = system_dir / name
            if src.exists():
                try:
                    text = src.read_text()
                    proc = subprocess.Popen(["dconf", "load", load_path], stdin=subprocess.PIPE, text=True)
                    proc.communicate(input=text)
                    if proc.returncode == 0:
                        print(f"   ✅ {name} restored")
                except Exception as e:
                    print(f"   ⚠️ Error restoring {name}: {e}")

    print("\n🎉 STATE TRANSFERRED SUCCESSFULLY!")
    print("   📁 AWP restored")
    print("   ℹ️  Some changes (e.g. keybindings) may require re-login")
    return True

    if input("\nStart AWP now? [Y/n]: ").lower() in {'', 'y', 'yes'}:
        os.chdir(AWP_DIR)
        os.system("./awp_start.sh")

def main():
    parser = argparse.ArgumentParser(description="AWP Transfer v2.1 – Backup & Transfer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--backup', action='store_true', help="Create backup of current state")
    group.add_argument('-t', '--transfer', action='store_true', help="Transfer (restore) a selected backup")
    group.add_argument('-l', '--list', action='store_true', help="List backups")

    args = parser.parse_args()

    if args.backup:
        create_backup()
    elif args.transfer:
        while True:
            list_backups()
            backup = select_backup()
            if not backup:
                break
            if transfer_backup(backup):
                break
    elif args.list:
        list_backups()

if __name__ == "__main__":
    main()

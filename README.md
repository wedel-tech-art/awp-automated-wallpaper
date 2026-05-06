# AWP - Desktop Alchemy 🧪✨

[![Python](https://img.shields.io/badge/Python-3.9%2B-green)](https://python.org)
[![Qt](https://img.shields.io/badge/Qt-6-purple)](https://qt.io)
[![Refactored](https://img.shields.io/badge/status-desktop--alchemy-brightgreen)](https://github.com/wedel-tech-art/awp-automated-wallpaper)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎯 What is Desktop Alchemy?

Most wallpaper managers rotate images.
AWP **transmutes** your entire desktop environment.

Each workspace becomes a distinct visual identity — with its own themes, icons, cursors, and wallpapers — all synchronized through a unified, intelligent architecture. From a single color, AWP **bakes** complete GTK and icon themes, creating harmony across your entire system.

## 🚀 Key Features

## 🎨 GTK & Icon Preset System (V3.8)

- **Multi-Preset Architecture:** Replaces the old single-template model with selectable presets for both GTK themes and icon sets.

- **Icon Reconstruction Engine:** Icon presets now store only **18 canonical PNG files + `index.theme`**. The full icon theme tree (sizes, symlinks, directories) is rebuilt programmatically during baking.

- **GTK Preset Variants:**
  - `breeze` (default): PNG modulation + CSS/SVG replacement
  - `colloid`: CSS/SVG-only recoloring (no PNG processing)

- **Preset-Based Theme Baking:** `bake_awp_theme()` now supports presets (`awp-gtk-{preset}-{hex}` naming).

- **Dashboard Integration:** GTK and Icon presets can be selected per workspace in `dab.py`.

- **Lean & Maintainable:** Presets are lightweight and act as the single source of truth.

## ⚡ Low-Latency State Bridge & Logic (V3.7)

- **RAM-Backed Sync:** The system now utilizes `/dev/shm/qtile_current_ws` as a high-speed "Single Source of Truth," allowing the Window Manager to push workspace states directly to AWP.

- **Zero-Lag Transmutation:** By reading state from RAM, theme and wallpaper updates are triggered instantaneously upon workspace transition, eliminating polling delays and reducing CPU overhead.

- 🆕 **"Park" Action:** A new 7th navigation command in `nav.py` allows manual wallpaper application based on the current index without cycling through the library.

- 🔌 **Daemon-Less Mode:** Upgraded `awp_start.sh` with a conditional toggle to skip starting the background daemon, optimized for self-theming environments like Qtile.

- **Backend-Driven Logic:** Core actions are now delegated to specific backends (like `qtile_xfce.py`), ensuring perfect synchronization between the WM and the AWP dashboard.

- **Unified Qt6/GTK Aesthetics:** All backends now synchronize Qt6 accent colors in real-time via `/dev/shm` symlinks. This ensures Qt6 applications match your workspace’s GTK "signature" with zero disk writes.

* **🖨️ Unified Printer System (V3.6)**:
    * **Single Source of Truth**: All terminal output now flows through `core/printer.py` – no more scattered color codes.
    * **Context-Aware Prefixes**: Every module identifies itself clearly:
        - `[AWP-backends]` (🟡 Yellow) - Backend loader
        - `[AWP-daemon]` (🔵 Cyan) - Main daemon
        - `[AWP-xfce]`, `[AWP-qtile_xfce]` (🔵 Cyan) - Runtime backends
        - `[AWP-dab]` (🔵 Cyan) - Qt6 Dashboard
        - `[AWP-nav]` (🔵 Cyan) - Navigation tool
        - `[AWP-utils]` (🔵 Cyan) - Utilities
        - `[AWP-themes]` (🔵 Cyan) - Theme baking engine
    * **Zero Duplication**: Change formatting once, affects everywhere.
    * **Professional Output**: Clean, consistent, color-coded logs across all components.

* **🧬 Genetic Theme & Icon Generation (V3.5)**:  
    * **Full Identity Baking**: Analyzes workspace icons to physically "bake" both custom GTK themes (`~/.themes`) and Icon themes (`~/.icons`) simultaneously.
    * **The "Mom" Inheritance**: Uses the `awp-icon-mom` directory as a master reference for procedural hue-shifting of icon sets based on the Mint-Y architecture.
    * **Visual Identity Sync**: Automatically extracts hex accent colors from icons to synchronize the visual "signature" across themes, icons, and Conky scripts.
    * **🔍 Real-Time Metadata (Hover-to-Hex)**: Hover over any workspace preview icon in the Dashboard to instantly see the extracted Hex color code rendered in real-time.
    * **Dedicated Theme Engine**: Powered by `core/themes.py`, a specialized module for procedural asset generation and theme list management.    

* **🎮 Interactive Navigation & Aesthetic Effects**:
    * **Dynamic Library Control**: Rapid **Next** and **Previous** wallpaper cycling via keyboard shortcuts.
    * **Real-time Image Processing**: Instantly adapt your wallpaper's look with non-destructive effects:
        * **Sharpen**: Enhance detail and clarity for high-resolution displays.
        * **Black & White**: Instant minimalist grayscale conversion.
        * **Saturation**: Boost color vibrance to change the "energy" of your desktop.
    * **Asset Management**: Integrated **Delete** functionality to curate your wallpaper library on the fly.

* **⚡ Optimized for Low-Resource Hardware**:
    * **"Lean Mode"**: Specifically tailored for old systems. Kills desktop managers (xfdesktop, caja-desktop) and uses `feh` for ultra-lightweight wallpaper rendering without sacrificing the "Deep Theming" experience.

* **🏗️ Universal Modular Architecture**:
    * **DE-Centric Design**: Focuses on Desktop Environments (**XFCE, Cinnamon, GNOME, MATE, Qtile/XFCE**) rather than specific distributions.
    * **Smart Backend Factory**: `backends/__init__.py` dynamically loads only what's available.
    * **Capability Matrix**: UI knows exactly what each backend supports (window themes, desktop themes, etc.).

* **🖥️ Native X11 Blanking Management**: 
    * **Independent Power Control**: Integrated direct management of screen timeouts and DPMS via X11 (`xset`).
    * **Lean System Design**: Specifically designed to provide display control for users who choose to remove `xfce4-power-manager` or `light-locker`.

### 🚀 Desktop Environment Support

| Environment | Wallpaper | Icons | GTK | Cursors | WM Theme | Desktop Theme |
|-------------|-----------|-------|-----|---------|----------|---------------|
| **XFCE** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Qtile/XFCE** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Cinnamon** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GNOME** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **MATE** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Generic WM** | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ |

> ⚠️ Generic WM support depends on gsettings availability

## 🚀 Quick Start (Presets and Symlinks Technology)

### 📦 Prerequisites

# Install System Tools & Python Bindings
```
sudo apt update
sudo apt install imagemagick python3-pyqt6 feh
```

# ⚡ Installation & First Run

For AWP to function correctly, the main directory must be named awp and reside in your home folder.

# Clone the repository
```
git clone [https://github.com/wedel-tech-art/awp-automated-wallpaper.git](https://github.com/wedel-tech-art/awp-automated-wallpaper.git)
mv awp-automated-wallpaper/awp ~/awp
cd ~/awp
```

### Use the startup script with TEMPLATE
```
Once you have awp as ~/awp then you can open a terminal there and do:
./awp_start.sh TEMPLATE (this will start your AWP with default values for a typical 4 workspaces OS)
The format is ./awp_start.sh [PRESET_NAME] so you can have your own presets all with different values, the possibilities are endless.
```

## 🎮 Usage

### Dashboard Qt6
```
In ~/awp you do "python3 dab.py" for editing all default values and make AWP really "your own".
```

## Manual Navigation

### Next wallpaper
```
python3 nav.py next
```
### Previous wallpaper
```
python3 nav.py prev
```
### Delete current wallpaper
```
python3 nav.py delete
```
### Sharpen current wallpaper (temporary, via ImageMagick)
```
python3 nav.py sharpen
```
### Apply saturation to wallpaper (temporary, via ImageMagick)
```
python3 nav.py color
```
### Convert wallpaper to black and white (temporary, via ImageMagick)
```
python3 nav.py black
```

### Recommended Keybindings

- `Super + Right` → Next wallpaper
- `Super + Left` → Previous wallpaper
- `Super + Delete` → Delete current wallpaper
- `Super + s` → Sharpen wallpaper
- `Super + c` → Colorize wallpaper
- `Super + b` → Convert wallpaper to black and white

> [!TIP]
> **Non-Destructive Editing:** Last 3 effects are applied to a temporary copy in the `awp/` folder. The original wallpaper remains untouched. If you love a modified version (e.g., a sharpened or B&W version), you can manually replace the original file in your library with the processed one from the `awp/` directory.

## 🛠️ Configuration
```
Use the dashboard:
python3 dab.py
```

## Screenshots

### General Settings
![General Settings](screenshots/General_Settings.png)

### Workspace 1 Configuration
![Workspace 1 Configuration](screenshots/ws1_config.png)

### Workspace 2 Configuration
![Workspace 2 Configuration](screenshots/ws2_config.png)

### Workspace 3 Configuration
![Workspace 3 Configuration](screenshots/ws3_config.png)

## 📁 Project Structure
```
awp-automated-wallpaper/
├── awp/                            # Main Application Directory
│   ├── core/                       # Centralized business logic
│   │   ├── actions.py              # Core wallpaper operations
│   │   ├── config.py               # Configuration management
│   │   ├── constants.py            # Paths, colors, capability matrix
│   │   ├── printer.py              # 🖨️ Unified printing system (V3.6)
│   │   ├── runtime.py              # Runtime state management
│   │   ├── themes.py               # Theme baking engine (Genetic logic)
│   │   └── utils.py                # Utility functions
│   ├── backends/                   # Desktop environment backends
│   │   ├── __init__.py             # Dynamic backend factory
│   │   ├── xfce.py                 # XFCE backend (with orchestrator)
│   │   ├── qtile_xfce.py           # Qtile/XFCE hybrid
│   │   ├── cinnamon.py             # Cinnamon backend
│   │   ├── gnome.py                # GNOME backend
│   │   ├── mate.py                 # MATE backend
│   │   └── generic.py              # Generic WM fallback
│   ├── presets/                    # Identity Robbery Presets 🎭
│   │   ├── TEMPLATE/               # Generic self-healing baseline
│   │   └── [preset_name]/          # Custom user-defined identities
│   ├── presets-backup/             # Pre-flight safety mirror 🛡️
│   ├── template-theme-presets/     # GTK preset templates (breeze, colloid)
│   ├── template-icon-presets/      # Icon presets (18 canonical files each)
│   ├── awp-icon-mom/               # The "Mother" icon template
│   ├── branding-assets/            # 180 procedural color tones
│   ├── logos/                      # Active workspace icons (symlinks)
│   ├── daemon.py                   # Background service
│   ├── dab.py                      # Qt6 Dashboard
│   ├── nav.py                      # Navigation controller
│   ├── hud_ws_info.py              # Workspace transition HUD
│   ├── hud_vertical.py             # Sidebar system monitor
│   ├── hud_bottom.py               # Bottom dock monitor
│   ├── awp_setup.py                # Setup wizard (Legacy fallback)
│   └── awp_start.sh                # Identity manager & startup script
├── screenshots/                    # GitHub previews
├── .gitignore
├── LICENSE
└── README.md
```
### 📅 Version Timeline

| Version | Date | Key Feature |
|---------|------|-------------|
| **V3.8** | May 2026 | 🎨 GTK & Icon Preset System (Modular presets + icon reconstruction engine) |
| **V3.7** | Mar 2026 | ⚡ Backend Logic Delegation + State Consolidation |
| **V3.6** | Feb 2026 | 🖨️ Unified Printer System + 🖱️ Cursor Refresh + 🧠 Capability Matrix |
| **V3.5** | Feb 2026 | 🧬 Dual-Genetic Baking (Themes + Icons) |
| **V3.4** | Feb 2026 | 🏗️ Core Consolidation (Zero Duplication) |
| **V3.3** | Feb 2026 | 🛰️ Runtime State Engine + Native HUDs |
| **V3.2** | Feb 2026 | 🔍 Surgical Precision + Hover-to-Hex |
| **V3.1** | Feb 2026 | 🔌 Universal Logic + Core Sanitization |
| **V3.0** | Jan 2026 | 🧠 Genetic Intelligence + Qt6 |
| **V2.2** | Jan 2026 | ⚡ Lean Mode + Hybrid Backends |
| **V2.1** | Jan 2025 | 🧰 Centralized Utilities |

## 🔧 Troubleshooting

### Missing Printer Prefixes?
If you see `[AWP]` instead of `[AWP-xfce]` or similar, ensure:
- You're using the latest version (V3.6+)
- The printer is properly imported in each module
- Backend functions pass `backend="name"` parameter

### Themes Not Applying?
- Run `dab.py` and click **Sync Themes** to bake missing themes
- Check `~/.themes/` and `~/.icons/` for generated folders
- Ensure your DE is correctly detected in `awp_config.ini`

### Dashboard Shows Greyed Out Options?
That's normal! The UI intelligently disables options your DE doesn't support:
- **Window Theme**: Only for XFCE, MATE, Cinnamon
- **Desktop Theme**: Only for Cinnamon

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python 3 and PyQt6.
- Tested on Linux Mint XFCE, Debian, and other major distributions.
- Theme presets based on **Breeze Dark** (KDE), **Mint-Y** (Linux Mint), **Yaru** (Ubuntu), and custom styles.
- Special thanks to the open-source community and all AWP users.

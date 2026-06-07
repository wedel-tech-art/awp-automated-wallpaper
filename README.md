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

## 🔆 Daemon Modes V3.9

AWP offers two daemon operation modes for Desktop Environments:

### Full Daemon (Default)
- Rotates wallpapers based on timing settings
- Preloads next wallpaper for smooth transitions  
- Best for desktops where rotation is desired

### Light Daemon (No Rotation)
- Sets wallpaper once per workspace
- No timer overhead, lower CPU usage (ideal for laptops)
- All theming features work identically

**How to use:** Create a preset with `_light` suffix (e.g., `xfce_light-debian`) and AWP automatically uses the light daemon while keeping all theming features. The same backend is shared - zero code duplication. The _light suffix tells AWP to use daemon-light.py instead of daemon.py. The backend remains unchanged. You can run either commad always within ~/awp.

```bash
# Full daemon preset
./awp_start.sh xfce-debian

# Light daemon preset (no rotation)
./awp_start.sh xfce_light-debian
```

## 🎨 GTK & Icon Preset System V3.8

- **Multi-Preset Architecture:** Replaces the old single-template model with selectable presets for both GTK themes and icon sets.

- **Dual-Phase Core Modulation (Enhanced Color Fidelity):** Upgraded the theme engine to run a precise double-phase calculation. It dynamically extracts color ratios to modulate assets (PNG/SVG) while cross-referencing and auto-diagnosing the target style, ensuring maximum color fidelity relative to the active workspace identity color without breaking native theme gradients.

- **Dynamic Icon Reconstruction Engine:** Icon presets now store canonical PNG/SVG source assets, utilizing a high-speed RAM-Disk workspace (`/dev/shm`) to completely eliminate disk wear.

- **Expanded Preset Library:** Includes mint, yaru, `slot-multicolor`, rami, neon, adwaitaru, and the scalable `breeze-svg` and `sweet-svg` presets supporting hybrid PNG/SVG baking pipelines.

- **On-the-Fly Manifests:** The engine now programmatically generates the clean `index.theme` and full standard XDG directory structure for icon themes during the bake process.

- **Scalable SVG Support:** SVG-capable presets now generate proper `scalable/` XDG icon directories alongside traditional PNG sizes.

- **Expanded Coverage:** Beyond "Places," presets now include comprehensive icons support for Devices, Legacy, and Mimetypes (fully tracking Debian `.deb` packages, Word/Writer documents, Excel/Calc spreadsheets, and PowerPoint/Impress presentations across standard Microsoft, OpenXML, and OpenDocument specifications).

- **Manifest-Driven Expansion:** Adding new icons or categories is now handled entirely via centralized dictionaries in `core/constants.py`.

- **Unified Icon Registry (`ICON_REGISTRY`):** All icon metadata — context, PNG actions, SVG originals, and symlink aliases — now lives in a single source-of-truth dictionary in `core/constants.py`. Manifest generation is derived directly from the registry, eliminating redundancy and making preset expansion or icon reassignment straightforward.

- **Hybrid PNG/SVG Pipeline:** The baking engine now handles both PNG modulation and SVG direct color replacement in the same pass. SVG-capable presets use `sed`-based hex substitution with mathematically derived family ratios for dark/light variants, producing pixel-perfect colors with zero modulation drift.

- **SVG Encoding Normalization:** Template SVGs are validated for UTF-8 encoding and proper `width`/`height` attributes before baking, preventing silent GTK render failures.

- **Unified Text-Substitution (`gtkrc` & XFWM4 SVGs):** The theme engine now scans and normalizes raw GTK2 `gtkrc` configurations and XFWM4 window manager vector graphics (`*.svg`), binding them to a single source-of-truth color anchor to completely eliminate mismatched factory accent flashes.

- **Automated Artifact Cleanup:** Automatically strips legacy, non-functional visual clutter like `thumbnail.png` or `preview.png` files from baked assets to keep the system lightweight.

- **GTK Preset Variants:**
  - `breeze` (default): PNG modulation + CSS/SVG replacement.
  - `flat-remix`: High-density layout supporting normalized asset scales and 203° standard corrections.
  - `colloid` & `graphite`: Pure CSS/SVG-only recoloring for GTK3/4 and just some GTK2 PNG's.

- **Preset-Based Theme Baking:** `bake_awp_theme()` now supports presets (`awp-gtk-{preset}-{hex}` naming).

- **Dashboard Integration:** GTK and Icon presets can be selected per workspace in `dab.py`, with sorted preset selection and live workspace theming info integrated via awp_config.ini.

- **Lean & Maintainable:** Presets are lightweight and act as the single source of truth.

## ⚡ Low-Latency State Bridge & Logic V3.7

- **RAM-Backed Sync:** The system now utilizes `/dev/shm/qtile_current_ws` as a high-speed "Single Source of Truth," allowing the Window Manager to push workspace states directly to AWP.

- **Zero-Lag Transmutation:** By reading state from RAM, theme and wallpaper updates are triggered instantaneously upon workspace transition, eliminating polling delays and reducing CPU overhead.

- **"Park" Action:** A new 7th navigation command in `nav.py` allows manual wallpaper application based on the current index without cycling through the library.

- **Daemon-Less Mode:** Upgraded `awp_start.sh` with a conditional toggle to skip starting the background daemon, optimized for self-theming environments like Qtile.

- **Backend-Driven Logic:** Core actions are now delegated to specific backends (like `qtile_xfce.py`), ensuring perfect synchronization between the WM and the AWP dashboard.

- **Unified Qt6/GTK Aesthetics:** All backends now synchronize Qt6 accent colors in real-time via `/dev/shm` symlinks. This ensures Qt6 applications match your workspace's GTK "signature" with zero disk writes.

- **Unified Printer System:** All terminal output now flows through `core/printer.py` – no more scattered color codes. Context-aware prefixes (`[AWP-backends]`, `[AWP-daemon]`, etc.) provide professional, color-coded logs across all components with zero duplication.

- **Genetic Theme & Icon Generation:** Analyzes workspace icons to physically "bake" both custom GTK themes (`~/.themes`) and Icon themes (`~/.icons`) simultaneously. Uses the "Mom" inheritance (`awp-icon-mom`) for procedural hue-shifting based on Mint-Y architecture. Features real-time hover-to-hex color extraction in the dashboard.

### 🚀 Desktop Environment Support

| Environment | Wallpaper | Icons | GTK | Cursors | WM Theme | Desktop Theme |
|-------------|-----------|-------|-----|---------|----------|---------------|
| **XFCE** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Qtile/XFCE** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Cinnamon** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GNOME** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **MATE** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Generic WM** | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ |

> 💡 **Light Mode:** Presets with `_light` suffix use the same backends but with a lightweight daemon (no wallpaper rotation). All theming features work identically. Add `_light` to any preset name to enable.

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
### Creating a Light Preset (No Wallpaper Rotation)

```bash
# Clone an existing preset
cp -r ~/awp/presets/xfce-debian ~/awp/presets/xfce_light-debian

# Rename the INI file to match
mv ~/awp/presets/xfce_light-debian/xfce-debian.ini \
   ~/awp/presets/xfce_light-debian/xfce_light-debian.ini

# Use it with the light daemon
./awp_start.sh xfce_light-debian
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
│   ├── template-theme-presets/     # GTK preset templates (breeze, colloid, flat-remix, graphite)
│   ├── template-icon-presets/      # PNG + scalable SVG icon presets (mint, yaru, slot-multicolor, rami, neon, adwaitaru, breeze-svg, sweet-svg)
│   ├── awp-icon-mom/               # The "Mother" icon template
│   ├── branding-assets/            # 200 procedural color tones
│   ├── logos/                      # Active workspace icons (symlinks)
│   ├── daemon.py                   # Full background service (with rotation)
│   ├── daemon-light.py             # Light background service (no rotation)
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
| **V3.9** | Jun 2026 | 🔆 Light Daemon Mode — `_light` preset suffix for no-rotation operation, shared backends, zero duplication |
| **V3.8** | May 2026 | 🎨 GTK & Icon Preset System — Unified `ICON_REGISTRY`, hybrid PNG/SVG baking pipeline, scalable XDG icon tree with auto-generated symlinks, and mathematically pure SVG color replacement |
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

### Light daemon not working?
- Ensure your preset name ends with `_light-debian` (e.g., `xfce_light-debian`)
- Check that `LIGHT_DAEMON_LIST` in `awp_start.sh` includes your preset
- The same backend works for both full and light modes - no extra files needed

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

### Icon Preset Credits

AWP includes modified icon presets built upon the work of these open-source projects, all under GPLv3 or compatible licenses:

| Preset | Based On | Author | License | Source |
|--------|----------|--------|---------|--------|
| slot-multicolor | Slot-Multicolor-Dark-Icons | L4ki | GPLv3 | [GitHub](https://github.com/L4ki/Slot-Plasma-Themes) |
| breeze-svg | Breeze Chameleon Dark | L4ki (based on KDE Breeze) | GPLv3 | [GitHub](https://github.com/L4ki/Breeze-Chameleon-Icons) |
| sweet-svg | Sweet | EliverLara | GPLv3 | [GitHub](https://github.com/EliverLara/Sweet) |
| yaru | Yaru | Ubuntu Community | GPLv3/CC-BY-SA | [Ubuntu](https://ubuntu.com) |
| adwaitaru | Adwaitaru | ricardoherreramx | GPLv3 | [GitHub](https://github.com/ricardoherreramx/adwaitaru) |
| mint | Mint-Y | Linux Mint | GPLv3/CC-BY-SA | [Linux Mint](https://linuxmint.com) |
| neon | Royal-Z / Neon | SethStormR | GPLv3 | [GitHub](https://github.com/SethStormR/Royal-Z) |
| rami | Rami (based on Kora) | Rami author | GPLv3 | [gnome-look.org](https://www.gnome-look.org/p/2216265) |

AWP does not claim ownership of these icons. They are redistributed under their respective licenses.

## 🙏 Acknowledgments

- Built with Python 3 and PyQt6.
- Tested on Linux Mint XFCE, Debian, and other major distributions.
- Theme presets based on **Breeze Dark** (KDE), **Mint-Y** (Linux Mint), **Yaru** (Ubuntu), and many custom styles.
- **Icon Preset Credits:** slot-multicolor (L4ki), breeze-svg (L4ki/KDE), sweet-svg (EliverLara), yaru (Ubuntu), adwaitaru (ricardoherreramx), mint (Linux Mint), neon (SethStormR), rami (Rami author). All under GPLv3.
- Special thanks to the open-source community and all AWP users.

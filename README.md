# AWP - Automated Wallpaper Program

[![Python](https://img.shields.io/badge/Python-3.9%2B-green)](https://python.org)
[![Qt](https://img.shields.io/badge/Qt-6-purple)](https://qt.io)
[![Refactored](https://img.shields.io/badge/status-core--consolidated-brightgreen)](https://github.com/wedel-tech-art/awp-automated-wallpaper)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎯 Why AWP?

Most wallpaper managers rotate images.
AWP orchestrates the entire desktop identity.

It treats each workspace as a distinct visual environment — synchronizing themes, icons, cursors, and now runtime telemetry — under a unified architecture.


## 🚀 Key Features

* **🧬 Genetic Theme & Icon Generation (V3.5)**:  
    * **Full Identity Baking**: Analyzes workspace icons to physically "bake" both custom GTK themes (`~/.themes`) and Icon themes (`~/.icons`) simultaneously.
    * **The "Mom" Inheritance**: Uses the `awp-icon-mom` directory as a master reference for procedural hue-shifting of icon sets based on the Mint-Y architecture.
    * **Visual Identity Sync**: Automatically extracts hex accent colors from icons to synchronize the visual "signature" across themes, icons, and Conky scripts.
    * **🔍 Real-Time Metadata (Hover-to-Hex)**: Hover over any workspace preview icon in the Dashboard to instantly see the extracted Hex color code rendered in real-time.
    * **Dedicated Theme Engine**: Powered by `core/themes.py`, a specialized module for procedural asset generation and theme list management.    

* **🏗️ Modernized Qt6 Controller**:
    * **Zero-Restart Workflow**: Features a standalone **Sync & Refresh** engine that updates system themes and UI dropdowns in real-time without requiring a restart.
    * **Professional UI Styling**: Optimized dark-mode aesthetics with "faded" read-only states for locked system fields (Adwaita).

* **📦 Comprehensive "Deep" Theming**: Total environment synchronization per workspace.
    * **Visual Atmosphere**: Orchestrates a complete aesthetic shift by synchronizing Wallpapers, Icon Sets, GTK Widgets, and Window Decorations (GTK 2/3/4) in real-time.
    * **Cursor Themes**: Seamless mouse pointer synchronization to match your active style.
    * **🧪 Experimental "Generic" Scope**: Expanded support for **Icon, GTK, and Cursor** switching in hybrid environments (e.g., Openbox + XFCE), allowing AWP to act as a standalone theme manager.
    * **Universal Compatibility**: Designed to "embellish" the workspace across both **X11 and Wayland** sessions (Gnome/Cinnamon) using native backend integration.

* **🎮 Interactive Navigation & Aesthetic Effects**: Powered by `nav.py`.
    * **Dynamic Library Control**: Rapid **Next** and **Previous** wallpaper cycling via keyboard shortcuts for an evolving workspace.
    * **Real-time Image Processing**: Instantly adapt your wallpaper's look with non-destructive effects:
        * **Sharpen**: Enhance detail and clarity for high-resolution displays.
        * **Black & White**: Instant minimalist grayscale conversion.
        * **Saturation**: Boost color vibrance to change the "energy" of your desktop.
    * **Asset Management**: Integrated **Delete** functionality to curate your wallpaper library on the fly.

* **⚡ Optimized for Low-Resource Hardware**:
    * **"Lean Mode"**: Specifically tailored for old systems. Includes an optional bypass for `xfdesktop`, utilizing `feh` for ultra-lightweight wallpaper rendering without sacrificing the "Deep Theming" experience.

* **🏗️ Universal Modular Architecture**:
    * **DE-Centric Design**: Focuses on Desktop Environments (**XFCE, Cinnamon, Gnome, and Mate**) rather than specific distributions, making it truly distro-agnostic.
    * **Unified Logic Core**: Centralized libraries ensure that the "Desktop Experience" remains consistent and high-quality across all supported backends.

* **🖥️ Native X11 Blanking Management**: 
    * **Independent Power Control**: Integrated direct management of screen timeouts and DPMS via X11 (`xset`).
    * **Lean System Design**: Specifically designed to provide display control for users who choose to remove `xfce4-power-manager` or `light-locker`.

### 🚀 Supported Backends
AWP now uses a dynamic backend factory, supporting both native desktop setters and a "Lean Mode" via `feh`.

| Backend | Mode | Desktop Environment |
| :--- | :--- | :--- |
| **XFCE** | Native + Lean | xfdesktop / feh |
| **Qtile/XFCE** | Hybrid | qtile(X11)/xfsettingsd |
| **Cinnamon** | Native | gsettings |
| **GNOME** | Native | gsettings |
| **MATE** | Native | dconf |
| **Openbox/XFCE**| Lean | feh (Hybrid setup) |
| **Generic** | Lean | feh (Fallback) |

## 🚀 Quick Start

### 📦 Prerequisites
Before installing, ensure your system has the necessary background tools:

```bash
# Install System Tools & Python Bindings
sudo apt update
sudo apt install imagemagick python3-pyqt6 feh
```

### Installation
```bash
# Clone the repository
git clone https://github.com/wedel-tech-art/awp-automated-wallpaper.git
cd awp-automated-wallpaper

# Run the setup wizard
python3 awp_setup.py
```

### First-Time Setup
1. Run `python3 awp_setup.py` to create your initial configuration
2. Follow the interactive wizard to configure workspaces
3. The daemon will start automatically on login

### Manual Start
```bash
# Start the daemon manually
python3 daemon.py

# Or use the startup script
./awp_start.sh
```

## 🎮 Usage


### Or newer Dashboard Qt6
```bash
python3 dab.py
```

### Manual Navigation
```bash
# Next wallpaper
python3 nav.py next

# Previous wallpaper
python3 nav.py prev

# Delete current wallpaper
python3 nav.py delete

# Sharpen current wallpaper (temporary, via ImageMagick)
python3 nav.py sharpen

# Apply saturation to wallpaper (temporary, via ImageMagick)
python3 nav.py color

# Convert wallpaper to black and white (temporary, via ImageMagick)
python3 nav.py black
```

### Recommended Keybindings
- `Super + Right` → Next wallpaper
- `Super + Left` → Previous wallpaper
- `Super + Delete` → Delete current wallpaper
- `Super + s` → Sharpen wallpaper
- `Super + c` → Colorize wallpaper
- `Super + b` → Convert wallpaper to black and white
---
> [!TIP]
> **Non-Destructive Editing:** Last 3 effects are applied to a temporary copy in the `awp/` folder. The original wallpaper remains untouched. If you love a modified version (e.g., a sharpened or B&W version), you can manually replace the original file in your library with the processed one from the `awp/` directory.

## 🛠️ Configuration

Edit `~/awp/awp_config.ini` directly or use the dashboard:

```bash
python3 dab.py
```

### Example Configuration
See `awp_config.ini.example` for a complete configuration reference.

## Screenshots

### General Settings
![General Settings](screenshots/dab.py%20General%20Settings.png)

### Workspace 1 Configuration
![Workspace 1](screenshots/dab.py%20Workspace%201%20Configuration%20Example.png)

### Workspace 2 Configuration  
![Workspace 2](screenshots/dab.py%20Workspace%202%20Configuration%20Example.png)

### Workspace 3 Configuration
![Workspace 3](screenshots/dab.py%20Workspace%203%20Configuration%20Example.png)

## 📁 Project Structure
```
awp-automated-wallpaper/
├── awp/                            # Main Application Directory
│   ├── core/                       # Centralized business logic
│   │   ├── actions.py              # ✨ IMPROVED - Smart logic (only applies changes if different)
│   │   ├── config.py               # Configuration management
│   │   ├── constants.py            # Paths and constants
│   │   ├── runtime.py              # Runtime state management
│   │   ├── themes.py               # ✨ NEW - Theming & Baking engine (Genetic logic)
│   │   └── utils.py                # Utility functions
│   ├── template-themes/            # 🧬 Theme DNA (Breeze Dark base)
│   ├── template-icons/             # 🧬 Icon DNA (Mint-Y base)
│   ├── awp-icon-mom/               # 👩 The "Mother" of all icons (Mint-Y master assets)
│   ├── branding-assets/            # 🎨 AWP Spectrum Hunt (180 procedural tones)
│   ├── logos/                      # Workspace-specific Debian logos (synced to accent colors)
│   ├── backends/                   # Desktop scripts (now includes qtile_xfce.py)
│   ├── daemon.py                   # Background service (integrated with mini-HUD)
│   ├── dab.py                      # Qt6 Dashboard (integrated with mini-HUD)
│   ├── nav.py                      # Navigation controller (was awp_nav.py)
│   ├── hud_ws_info.py              # Transient Workspace/WP "Flash" HUD
│   ├── hud_vertical.py             # Sidebar system monitor
│   ├── hud_bottom.py               # Bottom dock system monitor
│   ├── awp_setup.py          # Setup wizard (keep as is)
│   ├── awp_start.sh          # Quick-start script (keep as is)
│   ├── awp_config.ini        # Configuration file
│   └── *.png                 # UI icons (debian.png, awp-148-if0096.png)
├── screenshots/              # Previews for GitHub README
├── .gitignore                # Git exclusion rules
├── LICENSE                   # MIT License
└── README.md                 # Project Documentation
```

## 🔄 Recent Architecture Improvements

### 🧬 Dual-Genetic Baking & Efficiency Engine (V3.5 - February 2026)

**Version 3.5 – The "Spectrum" Update**

The system now creates a complete visual identity by "baking" both GTK themes and Icon themes simultaneously.

* **Dual-Baking Engine**: 
    * `template-themes`: Generates custom GTK 2/3/4 and Xfwm4 styles.
    * `template-icons`: Generates custom Icon sets based on the "Mother" (`awp-icon-mom`) assets.
* **Intelligent Sync**: The `set_themes` function is now "Diff-Aware." It compares the new workspace requirements against the current state. If the Icon theme is already correct, it skips the reload to save CPU and prevent flickering.
* **Transient Workspace HUD (`hud-ws-info.py`)**: A new, lightweight horizontal HUD that "flashes" workspace and wallpaper metadata for a few seconds during transitions, integrated directly into the `daemon` and `dab`.
* **New Hybrid Backend**: Added `qtile_xfce.py` for users running the Qtile Tiling Window Manager within an XFCE session.
* **Branding Assets**: Integration of the `branding-assets` library, offering 180 different color tones for procedural UI elements.

### 🧬 Core Consolidation & Zero-Duplication Architecture (V3.4 - Current)

**Version 3.4 – Unified Logic Core (February 2026)**

AWP has undergone a major architectural refactoring to centralize all business logic in `core/actions.py`, eliminating code duplication across the entire suite.

#### 🎯 Single Source of Truth

- **`core/actions.py`** now contains ALL wallpaper operations:
  - `next_wallpaper()`, `prev_wallpaper()`, `delete_wallpaper()`
  - `apply_effect()`, `clear_effect()` for temporary effects
  - `refresh_current_workspace()` for instant theme application
  - Shared helpers: `get_workspace_images()`, `get_workspace_index()`
  - Backend wrappers: `set_themes()`, `set_panel_icon()`

#### 🔄 Unified Components

All three major components now use the **exact same core functions**:

| Component | Before | After |
|-----------|--------|-------|
| **Daemon** (`daemon.py`) | Duplicate logic | Calls `next_wallpaper()` from core |
| **Nav** (`nav.py`) | Duplicate logic | Calls `next_wallpaper()` from core |
| **Dashboard** (`dab.py`) | Had to restart | Calls `refresh_current_workspace()` from core |

#### ✨ Instant Feedback Dashboard

**Theme changes apply immediately** when saving in the dashboard. No more switching workspaces twice to see your new theme!

# One line in dab.py after saving:
from core.actions import refresh_current_workspace
refresh_current_workspace()  # Applies themes NOW

### 🛰️ Runtime State Engine & Native HUD (V3.3)

**Version 3.3 – Native Runtime Monitoring (February 2026)**

AWP now includes a lightweight, backend-agnostic Runtime State engine with fully native Qt Heads-Up Displays (HUDs). This replaces the previous external monitoring bridge used in earlier versions.

### 🧠 Runtime State Engine

- **Shared Memory JSON State**:  
  Uses `/dev/shm/awp_full_state.json` for ultra-fast in-memory state updates.
- **Backend Decoupling**:  
  Removed legacy `bar()` hooks from `backends/` for cleaner separation of concerns.
- **Modular State Updates**:  
  The daemon writes structured runtime data (workspace, wallpaper, system stats) that any UI component can consume.
- **Low-Latency Refresh Model**:
  Uses shared memory to minimize disk I/O and eliminate filesystem wear.

### 🖥️ Native Qt HUD System

Two fully independent monitoring overlays:

| HUD | Layout | Purpose |
|-----|--------|----------|
| `hud_vertical.py` | Vertical Panel | Sidebar-style system monitor |
| `hud_bottom.py`   | Horizontal Bar | Minimal bottom dock monitor |

### 📊 Real-Time System Metrics

HUDs now use centralized utility functions from `core/utils.py`:

- `get_ram_info()`  
- `get_swap_info()`  
- `get_mounts_info()`  

These utilities are reusable across dashboards, widgets, or future monitoring modules.

### 🧹 Architecture Cleanup

- Removed legacy external monitoring bridge logic
- Removed deprecated `get_fs_info()` utility
- Simplified backend factory (no more optional `bar` injection)
- Introduced `RUNTIME_STATE_PATH` in `core/constants.py`

### ⚡ Design Philosophy

The new HUD system aligns with AWP’s modular vision:

- Runtime data is **written once**
- UI components **read independently**
- Backends remain strictly responsible for **theme & wallpaper application only**

This prepares AWP for future:
- Wayland-native overlays
- Multi-monitor HUDs
- Expanded workspace telemetry


**Version 3.2 - Surgical Precision & Metadata (February 2026)**
- **Swift Graphics Engine**: Optimized `bake_awp_theme` to use a hardcoded `TARGET_ASSETS` list. This removes the need for reference folders and speeds up theme generation significantly.
- **Hover-to-Hex Preview**: Added a "Human-Readable" feature to the Dashboard. Hovering over a workspace icon now performs a real-time first-pixel analysis to display the exact Hex color code.
- **Fluent Backend Linkage**: Refactored the `backends/` core with an `__init__.py` factory for seamless environment detection (Mint vs. Debian).
- **UI Gatekeeper**: Implemented dynamic UI controls that enable/disable features based on backend capabilities, plus alphabetical sorting for all dropdown menus.

**Version 3.1 - Universal Logic & Core Sanitization (February 2026)**
- **Dynamic Discovery**: Removed hardcoded backend lists (`VALID_DES`). The core now performs filesystem-based validation, allowing AWP to support any new DE/WM by simply adding a `.py` file to the `backends/` directory.
- **Config Safety (Zero-Flicker)**: Sanitized all backends to remove `sed`-based path manipulation. This eliminates `tint2` panel flickering and prevents potential configuration file corruption.
- **Log Professionalism**: Refactored terminal output to be "Logic-First," providing clean, honest feedback about applied themes and wallpapers without redundant debug noise.

**Version 3.0 - Genetic Intelligence (January 2026)**
- **Standardized Qt6**: Officially deprecated `awp_dab.py` (PyQt5) in favor of the modern `awp_dab_qt6.py`. Added a dedicated **Sync Themes** button to trigger the baking engine and real-time UI refresh.
- **Genetic Theme Baking**: Integrated `bake_awp_theme` in `core/utils.py`. AWP now physically generates theme directories with accent colors based on the workspace icon, including automated `folder.png` thumbnails.
- **Smart Setup**: The `awp_setup.py` wizard now triggers the baking engine during initial configuration for "Day One" readiness.
- **Refresh Logic**: Created a standalone `refresh_theme_lists()` function to allow real-time UI updates after a theme sync without program restarts.
- **X11 Utility**: Centralized display blanking/timeout logic in `core/utils.py`, allowing for standalone display management without DE-specific power daemons.

**Version 2.2 - Lean Mode & Hybrid Backends (January 2026)**
- **Lean Mode**: Universal function in `daemon` to toggle between native XFCE wallpaper handling and `feh` for legacy hardware (Optiplex 755).
- **Hybrid Support**: Refactored `generic.py` to support mixed environments like Openbox running inside XFCE.

**Version 2.1 - Centralized Utilities (January 2025)**
- Created `core/utils.py` module to eliminate code duplication.
- Consolidated `get_icon_color()` and `get_available_themes()` functions.
- All dashboard components now share common utilities for a cleaner codebase.

## 🌐 Supported Desktop Environments

🖥️ XFCE (Optimized)

    ✅ Wallpapers, Icons, GTK Themes, Cursors, Window Dec.

🌿 Cinnamon

    ✅ Wallpapers, Icons, GTK Themes, Cursors, Window Dec., Desktop Icons

👤 GNOME

    ✅ Wallpapers, Icons, GTK Themes, Cursors

    ❌ Window Decorations (Limited by Libadwaita)

🧉 MATE

    ✅ Wallpapers, Icons, GTK Themes, Cursors, Window Dec.

⚙️ Generic WMs (Openbox/i3)

    ✅ Wallpapers, GTK Themes

    ❌ Icons & Cursors (Requires manual Xresources)
    
## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python 3 and PyQt5 and experimental PyQt6
- Tested on Linux Mint XFCE, Cinnamon, and other major distributions
- Icons from the system theme collections

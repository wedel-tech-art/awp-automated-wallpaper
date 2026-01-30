# AWP - Automated Wallpaper Program

[![AWP](https://img.shields.io/badge/AWP-Automated%20Wallpaper%20Program-blue)](https://github.com/wedel-tech-art/awp-automated-wallpaper)
[![Python](https://img.shields.io/badge/Python-3.6%2B-green)](https://python.org)
[![Qt](https://img.shields.io/badge/Qt-6-purple)](https://qt.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A professional-grade Linux environment manager that goes beyond wallpaper rotation. AWP synchronizes the entire visual identity of your desktop based on your current workspace.

## 🚀 Key Features

* **🧬 Genetic Theme Generation (V3.0)**: 
    * **Automated Asset Creation**: Analyzes workspace icons to physically "bake" custom GTK and Xfwm4 themes in `~/.themes` based on a neutral template.
    * **Visual Identity Sync**: Automatically extracts hex accent colors from icons to synchronize the visual "signature" across themes and Conky scripts.
    * **Dynamic Thumbnails**: Generates `folder.png` assets inside the themes, ensuring your file manager (Thunar/PCManFM) matches the active workspace style.

* **🏗️ Modernized Qt6 Controller**:
    * **Zero-Restart Workflow**: Features a standalone **Sync & Refresh** engine that updates system themes and UI dropdowns in real-time without requiring a restart.
    * **Professional UI Styling**: Optimized dark-mode aesthetics with "faded" read-only states for locked system fields (Adwaita).

* **📦 Comprehensive "Deep" Theming**: Total environment synchronization per workspace.
    * **Visual Atmosphere**: Orchestrates a complete aesthetic shift by synchronizing Wallpapers, Icon Sets, GTK Widgets, and Window Decorations (GTK 2/3/4) in real-time.
    * **Cursor Themes**: Seamless mouse pointer synchronization to match your active style.
    * **🧪 Experimental "Generic" Scope**: Expanded support for **Icon, GTK, and Cursor** switching in hybrid environments (e.g., Openbox + XFCE), allowing AWP to act as a standalone theme manager.
    * **Universal Compatibility**: Designed to "embellish" the workspace across both **X11 and Wayland** sessions (Gnome/Cinnamon) using native backend integration.

* **🎮 Interactive Navigation & Aesthetic Effects**: Powered by `awp_nav.py`.
    * **Dynamic Library Control**: Rapid **Next** and **Previous** wallpaper cycling via keyboard shortcuts for an evolving workspace.
    * **Real-time Image Processing**: Instantly adapt your wallpaper's look with non-destructive effects:
        * **Sharpen**: Enhance detail and clarity for high-resolution displays.
        * **Black & White**: Instant minimalist grayscale conversion.
        * **Saturation**: Boost color vibrance to change the "energy" of your desktop.
    * **Asset Management**: Integrated **Delete** functionality to curate your wallpaper library on the fly.

* **📡 Advanced Conky IPC Integration**:
    * **State-Aware Monitoring**: Uses a custom `.awp_conky_state` bridge to keep system monitors in sync with the active theme.
    * **Visual Cohesion**: Automatically pushes color palettes and font settings to Conky's Lua/Cairo scripts, ensuring your system data looks like a native part of the wallpaper.

* **⚡ Optimized for Low-Resource Hardware**:
    * **Optiplex 755 "Lean Mode"**: Specifically tailored for legacy systems (Core 2 Duo / 6GB RAM). Includes an optional bypass for `xfdesktop`, utilizing `feh` for ultra-lightweight wallpaper rendering without sacrificing the "Deep Theming" experience.

* **🏗️ Universal Modular Architecture**:
    * **DE-Centric Design**: Focuses on Desktop Environments (**XFCE, Cinnamon, Gnome, and Mate**) rather than specific distributions, making it truly distro-agnostic.
    * **Unified Logic Core**: Centralized libraries ensure that the "Desktop Experience" remains consistent and high-quality across all supported backends.

* **🖥️ Native X11 Blanking Management**: 
    * **Independent Power Control**: Integrated direct management of screen timeouts and DPMS via X11 (`xset`).
    * **Lean System Design**: Specifically designed to provide display control for users who choose to remove `xfce4-power-manager` or `light-locker`.

## 🚀 Quick Start

### 📦 Prerequisites
Before installing, ensure your system has the necessary background tools:

```bash
# Install System Tools & Python Bindings
sudo apt update
sudo apt install conky-all imagemagick python3-pyqt5 python3-pyqt6 feh
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
python3 awp_daemon.py

# Or use the startup script
./awp_start.sh
```

## 🎮 Usage


### Or newer Dashboard Qt6
```bash
python3 awp_dab_qt6.py
```

### Manual Navigation
```bash
# Next wallpaper
python3 awp_nav.py next

# Previous wallpaper
python3 awp_nav.py prev

# Delete current wallpaper
python3 awp_nav.py delete

# Sharpen current wallpaper (temporary, via ImageMagick)
python3 awp_nav.py sharpen

# Apply saturation to wallpaper (temporary, via ImageMagick)
python3 awp_nav.py color

# Convert wallpaper to black and white (temporary, via ImageMagick)
python3 awp_nav.py black
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
python3 awp_dab.py
```

### Example Configuration
See `awp_config.ini.example` for a complete configuration reference.

## Screenshots

### General Settings
![General Settings](screenshots/awp_dab_qt6.py%20General%20Settings.png)

### Workspace 1 Configuration
![Workspace 1](screenshots/awp_dab_qt6.py%20Workspace%201%20Configuration%20Example.png)

### Workspace 2 Configuration  
![Workspace 2](screenshots/awp_dab_qt6.py%20Workspace%202%20Configuration%20Example.png)

### Workspace 3 Configuration
![Workspace 3](screenshots/awp_dab_qt6.py%20Workspace%203%20Configuration%20Example.png)

## 📁 Project Structure
```
awp-automated-wallpaper/
├── awp/                      # Main Application Directory
│   ├── backends/             # Desktop-specific scripts (XFCE, GNOME, etc.)
│   ├── conky/                # Conky configs and Lua scripts
│   ├── core/                 # Central logic (config.py, constants.py, utils.py)
│   ├── logos/                # Branding assets (ws1, ws2, ws3)
│   ├── template/             # Master Theme DNA (Mint-Y-Dark-Grey base) 🧬
│   ├── awp_dab_qt6.py        # New Professional Dashboard (Qt6) 🚀
│   ├── awp_daemon.py         # The background service
│   ├── awp_nav.py            # Navigation (Next/Prev/Del)
│   ├── awp_setup.py          # Setup wizard
│   ├── awp_start.sh          # Quick-start script
│   └── *.png                 # UI icons (debian.png, ws1-3.png)
├── screenshots/              # Previews for GitHub README
├── .gitignore                # Git exclusion rules
├── LICENSE                   # MIT License
└── README.md                 # Project Documentation
```

## 🔄 Recent Architecture Improvements

**Version 3.0 - Genetic Intelligence (January 2026)**
- **Standardized Qt6**: Officially deprecated `awp_dab.py` (PyQt5) in favor of the modern `awp_dab_qt6.py`. Added a dedicated **Sync Themes** button to trigger the baking engine and real-time UI refresh.
- **Genetic Theme Baking**: Integrated `bake_awp_theme` in `core/utils.py`. AWP now physically generates theme directories with accent colors based on the workspace icon, including automated `folder.png` thumbnails.
- **Smart Setup**: The `awp_setup.py` wizard now triggers the baking engine during initial configuration for "Day One" readiness.
- **Refresh Logic**: Created a standalone `refresh_theme_lists()` function to allow real-time UI updates after a theme sync without program restarts.
- **X11 Utility**: Centralized display blanking/timeout logic in `core/utils.py`, allowing for standalone display management without DE-specific power daemons.

**Version 2.2 - Lean Mode & Hybrid Backends (January 2026)**
- **Lean Mode**: Universal function in `awp_daemon` to toggle between native XFCE wallpaper handling and `feh` for legacy hardware (Optiplex 755).
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

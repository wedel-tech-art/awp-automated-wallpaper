# AWP - Automated Wallpaper Program

[![AWP](https://img.shields.io/badge/AWP-Automated%20Wallpaper%20Program-blue)](https://github.com/wedel-tech-art/awp-automated-wallpaper)
[![Python](https://img.shields.io/badge/Python-3.6%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A professional-grade Linux environment manager that goes beyond wallpaper rotation. AWP synchronizes the entire visual identity of your desktop based on your current workspace.

## 🚀 Key Features

* **📦 Comprehensive "Deep" Theming**: Total environment synchronization per workspace.
    * **Wallpapers**: Independent rotation and scaling.
    * **Icon Sets**: Dynamic switching of system-wide icon packs.
    * **GTK & WM Themes**: Real-time widget and window decoration updates.
    * **Cursor Themes**: Mouse pointer synchronization.
* **📡 Conky IPC Integration**: Advanced Inter-Process Communication between the AWP daemon and Conky.
    * Monitors internal state via `.awp_conky_state`.
    * Synchronizes Lua-based system monitoring aesthetics with the active workspace theme.
* **🖥️ Universal X11 Power Management**: 
    * Intelligent **X11 Screen Blanking** control compatible with any desktop running X11.
    * Manual and automated power-save overrides.
* **🎮 Navigation Effects**: Keyboard-driven wallpaper cycling with "Next/Previous" effects and direct file management (deletion).
* **🛠️ Dual Dashboard System**:
    * **Next-Gen Qt6 Dashboard**: A professional, modular configuration interface.
    * **Legacy PyQt5 Dashboard**: Maintained for maximum compatibility on older systems.

## 🚀 Quick Start

### 📦 Prerequisites
Before installing, ensure your system has the necessary background tools:

```bash
# Install System Tools & Python Bindings
sudo apt update
sudo apt install conky-all imagemagick python3-pyqt6
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

### Dashboard (Recommended)
```bash
python3 awp_dab.py
```

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
![General Settings](screenshots/awp_dab.py%20General%20Settings.png)

### Workspace 1 Configuration
![Workspace 1](screenshots/awp_dab.py%20Workspace%201%20Configuration%20Example.png)

### Workspace 2 Configuration  
![Workspace 2](screenshots/awp_dab.py%20Workspace%202%20Configuration%20Example.png)

### Workspace 3 Configuration
![Workspace 3](screenshots/awp_dab.py%20Workspace%203%20Configuration%20Example.png)

## 📁 Project Structure
```
awp-automated-wallpaper/
├── awp/                      # Main Application Directory
│   ├── backends/             # Desktop-specific scripts (XFCE, GNOME, etc.)
│   ├── conky/                # Conky configs and Lua scripts
│   ├── core/                 # Central logic (config.py, constants.py)
│   ├── logos/                # Branding assets (ws1, ws2, ws3)
│   ├── awp_dab.py            # Original Dashboard (PyQt5)
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

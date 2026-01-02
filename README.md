# AWP - Automated Wallpaper Program

[![AWP](https://img.shields.io/badge/AWP-Automated%20Wallpaper%20Program-blue)](https://github.com/wedel-tech-art/awp-automated-wallpaper)
[![Python](https://img.shields.io/badge/Python-3.6%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A professional wallpaper and theme management system for Linux desktop environments.
Per-workspace automated wallpaper rotation with dynamic theme switching.

## 🌟 Features

- **Multi-Desktop Support**: XFCE, Cinnamon, GNOME, MATE, and generic WMs
- **Per-Workspace Configuration**: Different wallpapers and themes for each workspace
- **Smart Automation**: Automatic rotation with customizable timing
- **Theme Management**: Dynamic icon, GTK, cursor, and window theme switching
- **Professional Dashboard**: Graphical configuration interface
- **Manual Controls**: Keyboard shortcuts for navigation and deletion
- **Screen Blanking**: Intelligent power management for XFCE/X11

## 🚀 Quick Start

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

### Manual Navigation
```bash
# Next wallpaper
python3 awp_nav.py next

# Previous wallpaper
python3 awp_nav.py prev

# Delete current wallpaper
python3 awp_nav.py delete
```

### Recommended Keybindings
- `Super+Right` → Next wallpaper
- `Super+Left` → Previous wallpaper
- `Super+Delete` → Delete current wallpaper

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

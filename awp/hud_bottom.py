import sys, json, os
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush
from core.constants import RUNTIME_STATE_PATH, AWP_CONFIG_RAM, THEME_CAPABILITIES
from core.utils import get_ram_info, get_swap_info, get_mounts_info, get_dynamic_mount_labels

class StudioBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        SCREEN_W, SCREEN_H = 1676, 943
        BAR_H    = 62
        GAP_SIDE = 10
        GAP_BOT  = 25
        BAR_W    = SCREEN_W - (GAP_SIDE * 2)

        self.resize(BAR_W, BAR_H)
        self.move(GAP_SIDE, SCREEN_H - BAR_H - GAP_BOT)
        self._r = 10

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(2)

        self.label = QLabel("INITIALIZING...")
        self.label.setFont(QFont("Source Code Pro", 10, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)

        self.target_mounts = ["/", "/mnt/internal1500", "/mnt/internal2000"]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(3000)
        self.update_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 160)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self._r, self._r)

    def update_ui(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        ram_str = get_ram_info()
        swap_str = get_swap_info()

        if os.path.exists(RUNTIME_STATE_PATH):
            try:
                with open(RUNTIME_STATE_PATH, "r") as f:
                    data = json.load(f)

                color = data.get('icon_color', '#ffffff')
                ws = data.get('workspace_name', '??').upper()

                def fmt(l, v, color):
                    spaced_label = " ".join(list(l))
                    val_str = str(v)[:60] + ".." if len(str(v)) > 60 else str(v)
                    return f'<span style="color:white;">{spaced_label} - </span><span style="color:{color};"><b>{val_str}</b></span>'

                wall_name = os.path.basename(data.get("wallpaper_path", "None"))
                wall_short = wall_name[:60] + ".." if len(wall_name) > 60 else wall_name

                mount_labels = get_dynamic_mount_labels(self.target_mounts)
                drives_info = get_mounts_info(self.target_mounts)

                mount_parts = []
                for path in self.target_mounts:
                    label = mount_labels.get(path, "???")
                    mount_parts.append(
                        fmt(label, drives_info.get(path, "N/A|N/A|N/A"), color)
                    )
                mounts_str = " &nbsp;&nbsp;&nbsp; ".join(mount_parts)

                line1 = (
                    f'<span style="color:white;">〔 <span style="color:{color};">{ws}</span> 〉 </span>'
                    f'<span style="color:#999;">{date_str} | {time_str}</span> &nbsp;&nbsp;&nbsp; '
                    f'{fmt("FLOW", data.get("flow", "?"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("VIEW", data.get("view", "?"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("SORT", data.get("sort", "?"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("COLR", data.get("icon_color", "??"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("INTV", data.get("intv", "??"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("WALL", wall_short, color)}'
                )

                line2 = (
                    f'{fmt("MEMR", ram_str, color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("SWAP", swap_str, color)} &nbsp;&nbsp;&nbsp; '
                    f'{fmt("BLNK", data.get("blanking_timeout", "??"), color)} &nbsp;&nbsp;&nbsp; '
                    f'{mounts_str}'
                )

                # line3 — capability-aware theme fields
                line3_parts = []
                if os.path.exists(AWP_CONFIG_RAM):
                    with open(AWP_CONFIG_RAM, "r") as f:
                        cfg = json.load(f)
                    general    = cfg.get("general", {})
                    os_detected = general.get("os_detected", "generic")
                    caps       = THEME_CAPABILITIES.get(os_detected, THEME_CAPABILITIES["generic"])
                    ws_cfg     = cfg.get(data.get("workspace_name", ""), {})

                    if caps.get("has_gtk"):
                        line3_parts.append(fmt("GTKТ", ws_cfg.get("gtk_theme", "?"), color))
                    if caps.get("has_icons"):
                        line3_parts.append(fmt("ICON", ws_cfg.get("icon_theme", "?"), color))
                    if caps.get("has_cursor"):
                        line3_parts.append(fmt("CURS", ws_cfg.get("cursor_theme", "?"), color))
                    if caps.get("has_wm_theme"):
                        line3_parts.append(fmt("WMTH", ws_cfg.get("wm_theme", "?"), color))
                    if caps.get("has_desktop_theme"):
                        line3_parts.append(fmt("DESK", ws_cfg.get("desktop_theme", "?"), color))

                line3 = " &nbsp;&nbsp;&nbsp; ".join(line3_parts)

                report = f'<div style="line-height: 125%; text-align: center;">{line1}<br>{line2}<br>{line3}</div>'
                self.label.setText(report)
                self.label.setTextFormat(Qt.TextFormat.RichText)

            except Exception as e:
                self.label.setText(f"FEED ERROR: {str(e)[:50]}")
        else:
            self.label.setText("NO STATE FILE")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = StudioBar()
    bar.show()
    sys.exit(app.exec())

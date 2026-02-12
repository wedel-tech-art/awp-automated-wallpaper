import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPixmap

# Importamos las funciones que calculan fresco
from core.utils import get_ram_info, get_swap_info, get_mounts_info

class StudioHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.resize(560, 550)
        self.move(950, 40)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(25, 20, 20, 20)

        self.label = QLabel()
        self.label.setFont(QFont("Source Code Pro", 11, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Ícono flotante
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.move(16, 8)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Timer más lento: 3 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(3000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 190)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def update_ui(self):
        now_time = datetime.now().strftime("%H:%M:%S")
        now_date = datetime.now().strftime("%Y-%m-%d")

        state_file = "/dev/shm/awp_full_state.json"
        if not os.path.exists(state_file):
            self.label.setText("NO STATE FILE")
            return

        try:
            with open(state_file, "r") as f:
                data = json.load(f)

            color = data.get('icon_color', '#ffffff')
            ws = data.get('workspace_name', '??').upper()
            wall_name = os.path.basename(data.get('wallpaper_path', 'None'))

            # Cálculo fresco (como el bottom)
            ram_val = get_ram_info()
            swap_val = get_swap_info()

            # Monts fresco (lista completa de 6)
            mounts = [
                "/mnt/windows",
                "/mnt/owstudios",
                "/mnt/internal1500",
                "/",
                "/home",
                "/mnt/internal2000"
            ]
            drives_info = get_mounts_info(mounts)

            # Ícono
            logo_path = data.get('logo_path')
            if logo_path and os.path.exists(logo_path):
                pix = QPixmap(logo_path)
                scaled = pix.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                self.icon_label.setPixmap(scaled)
                self.icon_label.show()
            else:
                self.icon_label.clear()
                self.icon_label.hide()

            def fmt(label, value):
                spaced_label = " ".join(list(label))
                return (f'<div style="text-align: left;">'
                        f'<span style="color:white;">{spaced_label} - </span>'
                        f'<span style="color:{color};"><b>{value}</b></span>'
                        f'</div>')

            def drive_row(label, path):
                spaced_label = " ".join(list(label))
                value = drives_info.get(path, "N/A|N/A|N/A")
                return (f'<div style="margin-top: 4px;">'
                        f'<span style="color:#555; font-size:9px;">{path}</span><br>'
                        f'<span style="color:white;">{spaced_label} - </span>'
                        f'<span style="color:{color};"><b>{value}</b></span>'
                        f'</div>')

            divider = '<div style="color:#444; margin-top: 5px; margin-bottom: 5px;">────────────────────────────────────────────────────────</div>'

            offset_px = 55
            first_line_style = f"margin-left: {offset_px}px; padding-left: {offset_px}px;"

            report = (
                f'<div style="text-align: left; line-height: 90%;">'
                f'<div align="right" style="color:#333; font-size:9px;">AWP - HUD</div>'
                f'<div style="color:white; margin-bottom: 8px; {first_line_style}">'
                f'〔 <span style="color:{color};">{ws}</span> 〕 {now_date} | {now_time}'
                f'</div>'
                f'{divider}'
                f'{fmt("MEMR", ram_val)}'
                f'{fmt("SWAP", swap_val)}'
                f'{fmt("BLNK", data.get("blanking_timeout", "??"))}'
                f'{divider}'
                f'{drive_row("SDA2", "/mnt/windows")}'
                f'{drive_row("SDA3", "/mnt/owstudios")}'
                f'{drive_row("SDA5", "/mnt/internal1500")}'
                f'{drive_row("SDB1", "/")}'
                f'{drive_row("SDB3", "/home")}'
                f'{drive_row("SDC1", "/mnt/internal2000")}'
                f'{divider}'
                f'{fmt("WALL", wall_name)}'
                f'{fmt("VIEW", data.get("view", "??"))}'
                f'{fmt("FLOW", data.get("flow", "??"))}'
                f'{fmt("SORT", data.get("sort", "??"))}'
                f'{fmt("COLR", data.get("icon_color", "??"))}'
                f'{fmt("INTV", data.get("intv", "??"))}'
                f'</div>'
            )

            self.label.setText(report)
            self.label.setTextFormat(Qt.TextFormat.RichText)

        except Exception as e:
            print("Error in vertical HUD:", str(e))
            self.label.setText(f"ERROR: {str(e)[:50]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = StudioHUD()
    hud.show()
    sys.exit(app.exec())

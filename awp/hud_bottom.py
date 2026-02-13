import sys, json, os
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush

from core.utils import get_ram_info, get_swap_info, get_mounts_info

# === MOUNT CONFIG (easy to edit) ===
MOUNT_LABELS = {
    "/mnt/internal1500": "SDA5",
    "/": "SDB1",
    "/home": "SDB3",
    "/mnt/internal2000": "SDC1",
}

class StudioBar(QWidget):
    def __init__(self):
        super().__init__()
       
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            #Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            #Qt.WindowType.X11BypassWindowManagerHint |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.resize(1600, 25)
        self.move(0, 850)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 6, 0, 6)
        self.layout.setSpacing(2)
       
        self.label = QLabel("INITIALIZING...")
        self.label.setFont(QFont("Source Code Pro", 9, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
       
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(3000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 160)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def update_ui(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        ram_str = get_ram_info()
        swap_str = get_swap_info()

        if os.path.exists("/dev/shm/awp_full_state.json"):
            try:
                with open("/dev/shm/awp_full_state.json", "r") as f:
                    data = json.load(f)
               
                color = data.get('icon_color', '#ffffff')
                ws = data.get('workspace_name', '??').upper()
               
                def fmt(l, v, color):
                    spaced_label = " ".join(list(l))
                    val_str = str(v)[:60] + ".." if len(str(v)) > 60 else str(v)
                    return f'<span style="color:white;">{spaced_label} - </span><span style="color:{color};"><b>{val_str}</b></span>'
               
                wall_name = os.path.basename(data.get("wallpaper_path", "None"))
                wall_short = wall_name[:60] + ".." if len(wall_name) > 60 else wall_name
                
                drives_info = get_mounts_info(list(MOUNT_LABELS.keys()))
                
                mount_parts = []
                for path, label in MOUNT_LABELS.items():
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
                report = f'<div style="line-height: 125%; text-align: center;">{line1}<br>{line2}</div>'
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

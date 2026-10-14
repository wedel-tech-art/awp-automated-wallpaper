#!/usr/bin/env python3
"""
AWP Preset Preview HUD
Shows what Wini will create: per-workspace colors and wallpaper filenames.
Reads from WORKSPACE_TEMPLATES (Phase 1) — shuffle-aware in Phase 2.
"""

import sys
import signal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush

from core.constants import WORKSPACE_TEMPLATES, SHM_ACTIVE_PRESET
from core.runtime import read_raw_accent
from core.wallpaper import compute_wallpaper_name
from core.printer import get_printer

_printer = get_printer()

# ============================================================
# HUD WIDGET
# ============================================================

class PresetPreviewHUD(QWidget):
    def __init__(self, get_ui_state):
        """
        get_ui_state: a callable that returns a dict like
            {
                "backend": "qtile_xfce",
                "session": "x11",
                "workspace_count": 8,
                "shuffle": False,
                "style_id": "awp-firma-cave",
                "pending_shuffle": None,   # Phase 2 — a list of dicts or None
            }
        """
        super().__init__()

        self.get_ui_state = get_ui_state

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # ============================================================
        # AUTO-DETECT WORK AREA
        # ============================================================
        avail = QApplication.primaryScreen().availableGeometry()

        GAP_X = 10
        GAP_Y = 10

        pos_x = avail.x() + GAP_X
        pos_y = avail.y() + GAP_Y

        # Band-aid: Qtile doesn't publish _NET_WORKAREA, so avail.y()
        # reports 0 even though the bar occupies the top ~32px. If the
        # currently active preset targets Qtile, nudge the HUD down.
        try:
            with open(SHM_ACTIVE_PRESET, "r") as f:
                active = f.read().strip()
            if "qtile" in active.lower():
                pos_y += 32
        except (FileNotFoundError, OSError):
            pass

        self.move(pos_x, pos_y)
        self.resize(500, 550)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 20, 20)

        self.label = QLabel()
        self.label.setFont(QFont("Source Code Pro", 11, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setTextFormat(Qt.TextFormat.RichText)

        layout.addWidget(self.label)
        self.setLayout(layout)

        # Initial render
        self.update_from_state()

        # Periodic re-render so the accent color (and any future live state)
        # stays in sync with AWP. Same cadence as hud_wp.py.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_state)
        self.timer.start(3000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 190)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    # ============================================================
    # STATE → HTML
    # ============================================================

    def _fmt_kv(self, label: str, value: str, accent: str) -> str:
        """A label/value row in the HUD's signature letter-spaced style."""
        spaced = " ".join(list(label))
        return (
            f'<div style="text-align: left; font-size:15px;">'
            f'<span style="color:white;">{spaced} - </span>'
            f'<span style="color:{accent};"><b>{value}</b></span>'
            f'</div>'
        )

    def _render_workspace_rows(self, state: dict) -> str:
        count = state.get("workspace_count", 8)
        style_id = state.get("style_id", "")
        pending = state.get("pending_shuffle")
        ini_colors = state.get("ini_colors")

        rows = ""
        for i in range(1, count + 1):
            section = f"ws{i}"

            if ini_colors and i - 1 < len(ini_colors) and ini_colors[i - 1]:
                color = ini_colors[i - 1]
            elif pending is not None and i - 1 < len(pending):
                color = pending[i - 1].get("icon_color", "#666666")
            else:
                template = WORKSPACE_TEMPLATES.get(section, {})
                color = template.get("icon_color", "#666666")

            wp_name = compute_wallpaper_name(color, style_id)

            rows += (
                f'<div style="margin-top: 4px; line-height: 26px;">'
                f'<span style="color:#888; font-size:15px;">{section}</span>'
                f'&nbsp;&nbsp;'
                f'<span style="color:{color}; font-size:22px; vertical-align:middle;">▮</span>'
                f'&nbsp;'
                f'<span style="color:#ddd; font-size:15px; font-weight:bold;">{color}</span>'
                f'&nbsp;&nbsp;'
                f'<span style="font-family: \'Source Code Pro\', monospace; '
                f'font-size:14px; color:#aaa;">{wp_name}</span>'
                f'</div>'
            )

        return rows

    def _render_html(self, state: dict) -> str:
        accent = read_raw_accent()
        divider = (
            '<div style="color:#444; margin-top: 6px; margin-bottom: 6px;">'
            '────────────────────────────────────────────────'
            '</div>'
        )

        # ─── Header ───
        header = (
            f'<div align="right" style="color:#333; font-size:10px;">AWP - HUD PRESET</div>'
            f'<div style="color:white; margin-bottom: 8px; font-size:16px;">'
            f'〔 <span style="color:{accent};">PRESET PREVIEW</span> 〕'
            f'</div>'
        )

        # ─── [general] section ───
        general_rows = (
            self._fmt_kv("BACK", state.get("backend", "?"), accent) +
            self._fmt_kv("SESS", state.get("session", "?"), accent) +
            self._fmt_kv("WORK", str(state.get("workspace_count", "?")), accent) +
            self._fmt_kv("SRCE", state.get("source", "?"), accent) +
            self._fmt_kv("STYL", state.get("style_id", "?"), accent)
        )

        # ─── [wsN] section header ───
        ws_header = (
            f'<div style="margin-top: 4px; font-size:14px;">'
            f'<span style="color:#888;">🗂  WORKSPACES</span>'
            f'</div>'
        )

        ws_rows = self._render_workspace_rows(state)

        # ─── Shuffle hint (Phase 1 only) ───
        shuffle_note = ""
        if state.get("shuffle") and state.get("pending_shuffle") is None:
            shuffle_note = (
                f'<div style="margin-top: 10px; color:#d4a017; font-size:12px;">'
                f'⚠️  Shuffle is on — colors shown are the defaults, '
                f'actual colors will be randomized on Create.'
                f'</div>'
            )

        return (
            f'<div style="text-align: left; line-height: 90%;">'
            f'{header}'
            f'{divider}'
            f'{general_rows}'
            f'{divider}'
            f'{ws_header}'
            f'{ws_rows}'
            f'{shuffle_note}'
            f'</div>'
        )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def update_from_state(self):
        """Re-render the panel from the current UI state."""
        try:
            state = self.get_ui_state()
            html = self._render_html(state)
            self.label.setText(html)
        except Exception as e:
            _printer.error(f"HUD render failed: {e}")
            self.label.setText(f"<div style='color:#d04040;'>HUD error: {e}</div>")

    def closeEvent(self, event):
        # Stop the timer so it doesn't fire on a dead widget
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    # Allow Ctrl+C to quit cleanly (Qt's C event loop doesn't
    # process Python signals reliably on its own).
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Fake state for testing the HUD without Wini
    FAKE_STATE = {
        "backend": "qtile_xfce",
        "session": "x11",
        "workspace_count": 8,
        "shuffle": False,
        "style_id": "awp-center",
        "pending_shuffle": None,
    }

    app = QApplication(sys.argv)
    hud = PresetPreviewHUD(lambda: FAKE_STATE)
    hud.show()
    sys.exit(app.exec())

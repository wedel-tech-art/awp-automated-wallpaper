#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
import os
import time

# --- 1. THE CLEANUP & DELAY (BEFORE GTK STARTS) ---
if __name__ == "__main__":
    me = os.getpid()
    try:
        # Kill old instances immediately
        output = subprocess.check_output(["pgrep", "-f", "hud_ws_info.py"]).decode()
        pids = output.strip().split("\n")
        for pid in pids:
            if int(pid) != me:
                subprocess.run(["kill", str(pid)], stderr=subprocess.DEVNULL)
    except:
        pass

    # THE "SMOOTHNESS" DELAY
    # 0.7s - 1.0s gives the wallpaper time to settle
    time.sleep(0.7)

# --- 2. THE HUD CLASS ---
class FadingHUD(Gtk.Window):
    def __init__(self):
        super().__init__(title="AWP_HUD_FADE")
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        Gtk.Widget.set_opacity(self, 0.0)
        
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual: self.set_visual(visual)

        # DATA EXTRACTION
        try:
            state_file = "/dev/shm/awp_full_state.json"
            with open(state_file, 'r') as f:
                data = json.load(f)
                color = data.get('icon_color', '#FFD700')
                wall_name = os.path.basename(data.get('wallpaper_path', 'None'))
        except:
            color, wall_name = '#FFD700', 'None'

        # CSS (Modern 0.5 Opacity)
        style_provider = Gtk.CssProvider()
        css = f"""
            window {{
                background-color: rgba(0, 0, 0, 0.5); 
                border: 1px solid {color};
                border-radius: 12px;
            }}
            label {{ font-family: 'Source Code Pro', 'Monospace'; color: white; }}
            .data-text {{ font-size: 10px; }}
        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(screen, style_provider, 600)

        # LAYOUT
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        main_box.set_margin_top(4); main_box.set_margin_bottom(4)
        main_box.set_margin_start(20); main_box.set_margin_end(60)

        def fmt_row(text, val):
            spaced = " ".join(list(text))
            return f'<span alpha="70%">{spaced} - </span><span color="{color}"><b>{val}</b></span>'

        fields = [
            (" VIEW", data.get("view", "??")),
            (" FLOW", data.get("flow", "??")),
            (" SORT", data.get("sort", "??")),
            (" COLR", color),
            (" INTV", data.get("intv", "??")),
            (" WALL", wall_name),
        ]

        for label, value in fields:
            lbl = Gtk.Label(xalign=0)
            lbl.get_style_context().add_class("data-text")
            lbl.set_markup(fmt_row(label, value))
            main_box.pack_start(lbl, False, False, 0)

        self.add(main_box)
        self.show_all()

        # POSITIONING
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geo = monitor.get_geometry()
        window_w = self.get_size()[0]
        self.move(geo.width - window_w - 320, 875)

        # ANIMATION
        self.current_opacity = 0.0
        GLib.timeout_add(20, self.fade_in)
        GLib.timeout_add_seconds(14, lambda: GLib.timeout_add(40, self.fade_out))

    def fade_in(self):
        if self.current_opacity < 1.0:
            self.current_opacity += 0.05
            Gtk.Widget.set_opacity(self, self.current_opacity)
            return True
        return False

    def fade_out(self):
        if self.current_opacity > 0.0:
            self.current_opacity -= 0.05
            Gtk.Widget.set_opacity(self, self.current_opacity)
            return True
        else:
            Gtk.main_quit()
            return False

if __name__ == "__main__":
    # The cleanup and sleep happened at the top, now we start GTK
    FadingHUD()
    Gtk.main()

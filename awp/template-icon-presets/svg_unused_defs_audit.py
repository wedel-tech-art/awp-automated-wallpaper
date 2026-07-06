#!/usr/bin/env python3
"""
svg_unused_defs_audit.py

Scans a directory of SVG icons and reports:
  1. Every distinct fill/stroke color used in each file (so you can eyeball
     inconsistencies like a stray #222222 or #333333 hiding among your
     purple/neon palette).
  2. Any <defs> entry (gradient, clipPath, pattern, etc.) that is never
     referenced anywhere else in the file via url(#id) or xlink:href/href
     -- i.e. dead weight left over from a template.

Usage:
    python3 svg_unused_defs_audit.py /path/to/awp/template-icon-presets/neon
"""

import sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"svg": "http://www.w3.org/2000/svg"}

COLOR_ATTRS = ("fill", "stroke", "stop-color")
# also catch colors buried inside style="fill:#xxxxxx;..."
STYLE_COLOR_RE = re.compile(r"(fill|stroke|stop-color)\s*:\s*(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")
URL_REF_RE = re.compile(r"url\(#([^)]+)\)")


def local_tag(elem):
    return elem.tag.split("}")[-1]


def collect_colors(root):
    colors = set()
    for elem in root.iter():
        for attr in COLOR_ATTRS:
            val = elem.attrib.get(attr)
            if val and HEX_RE.match(val):
                colors.add(val.lower())
        style = elem.attrib.get("style", "")
        for prop, val in STYLE_COLOR_RE.findall(style):
            if HEX_RE.match(val):
                colors.add(val.lower())
    return colors


def collect_def_ids(root):
    """Find the id of every TOP-LEVEL child inside <defs> (gradients, clipPaths,
    patterns, filters...). Only top-level entries are checked for external
    references -- their own descendants (e.g. <stop> inside a gradient, or the
    helper <path>/<circle> inside a clipPath) are structural parts consumed by
    their parent and shouldn't be flagged individually."""
    def_ids = {}
    for defs in root.iter():
        if local_tag(defs) == "defs":
            for child in list(defs):
                _id = child.attrib.get("id")
                if _id:
                    def_ids[_id] = local_tag(child)
    return def_ids


def collect_referenced_ids(root, raw_text):
    referenced = set()
    # url(#id) references anywhere (fill="url(#x)", clip-path="url(#x)", style="...")
    referenced.update(URL_REF_RE.findall(raw_text))
    # xlink:href="#id" / href="#id" (gradient inheritance, <use>)
    for elem in root.iter():
        for attr, val in elem.attrib.items():
            if attr.endswith("href") and val.startswith("#"):
                referenced.add(val[1:])
    return referenced


SUSPECT_DARK_COLORS = {"#333333", "#222222", "#4d4d4d", "#2b2b2b", "#1a1a1a"}


def find_muddy_fills(root):
    """Find elements OUTSIDE <defs>/<clipPath> that use a suspiciously dark
    fill (#333333, #222222, etc.) at high opacity -- the exact 'solid/near-
    opaque dark patch dominating the icon' bug we found in several files.
    Legit uses of these colors inside <defs> or <clipPath> (pure clip
    geometry, never painted) are skipped."""
    hits = []

    def in_defs_or_clip(elem, ancestors):
        return any(local_tag(a) in ("defs", "clipPath") for a in ancestors)

    def walk(elem, ancestors):
        tag = local_tag(elem)
        if tag not in ("defs", "clipPath"):
            fill = elem.attrib.get("fill", "")
            style = elem.attrib.get("style", "")
            style_colors = dict(STYLE_COLOR_RE.findall(style))
            style_fill = style_colors.get("fill", "")
            # style overrides the presentation attribute in SVG/CSS -- check style FIRST
            color = style_fill.lower() if HEX_RE.match(style_fill) else (
                fill.lower() if HEX_RE.match(fill) else None
            )
            if color in SUSPECT_DARK_COLORS and not in_defs_or_clip(elem, ancestors):
                # opacity: style "opacity" wins over attribute; same for fill-opacity
                op = style_colors.get("opacity") if "opacity" in style_colors else None
                if op is None:
                    m = re.search(r"(?<!fill-)(?<!stroke-)opacity\s*:\s*([\d.]+)", style)
                    op = m.group(1) if m else elem.attrib.get("opacity", "1")
                fop = elem.attrib.get("fill-opacity")
                if fop is None:
                    m2 = re.search(r"fill-opacity\s*:\s*([\d.]+)", style)
                    fop = m2.group(1) if m2 else "1"
                try:
                    op_val = float(op) * float(fop)
                except ValueError:
                    op_val = 1.0
                if op_val > 0.01:  # skip fully/near-invisible fills -- they can't look muddy
                    hits.append((tag, elem.attrib.get("id", "?"), color, op_val))
        for child in list(elem):
            walk(child, ancestors + [elem])

    walk(root, [])
    return hits


def audit_file(path: Path):
    raw = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return None, None, None, None, f"PARSE ERROR: {e}"

    colors = collect_colors(root)
    def_ids = collect_def_ids(root)
    referenced = collect_referenced_ids(root, raw)
    muddy = find_muddy_fills(root)

    unused = {i: kind for i, kind in def_ids.items() if i not in referenced}
    return colors, def_ids, unused, muddy, None


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.is_dir():
        print(f"Not a directory: {target}")
        sys.exit(1)

    svg_files = sorted(target.glob("*.svg"))
    if not svg_files:
        print("No .svg files found.")
        sys.exit(0)

    all_colors = {}
    any_unused = False

    print(f"Auditing {len(svg_files)} files in {target}\n")

    for f in svg_files:
        colors, def_ids, unused, muddy, err = audit_file(f)
        if err:
            print(f"[{f.name}] {err}")
            continue

        all_colors[f.name] = colors

        if unused or muddy:
            any_unused = True
            print(f"[{f.name}]")
            for _id, kind in unused.items():
                print(f"    UNUSED <{kind} id=\"{_id}\"> — safe to delete")
            for tag, _id, color, op_val in muddy:
                severity = "SOLID/OPAQUE" if op_val >= 0.5 else "translucent"
                print(f"    SUSPECT <{tag} id=\"{_id}\"> fill={color} opacity={op_val} ({severity}) — likely the 'muddy patch' bug")
            print()

    if not any_unused:
        print("No unused <defs> entries found in any file.\n")

    # Cross-file color summary: flag colors that appear in very few files
    # (likely leftovers / inconsistencies) vs. the common palette.
    color_counts = {}
    for fname, colors in all_colors.items():
        for c in colors:
            color_counts.setdefault(c, []).append(fname)

    print("=== Color usage across all files ===")
    for color, files in sorted(color_counts.items(), key=lambda kv: -len(kv[1])):
        marker = "  <-- only in a few files, double check" if len(files) <= 2 else ""
        print(f"  {color:10s} used in {len(files):2d}/{len(svg_files)} files{marker}")

    print()
    print("Tip: colors used in only 1-2 files (like a stray #222222 or #333333)")
    print("are the ones worth eyeballing -- they're often template leftovers.")


if __name__ == "__main__":
    main()

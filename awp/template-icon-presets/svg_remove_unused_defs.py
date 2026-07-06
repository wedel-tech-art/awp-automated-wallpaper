#!/usr/bin/env python3
"""
svg_remove_unused_defs.py

Companion to svg_unused_defs_audit.py. Removes any TOP-LEVEL <defs> child
(gradient, clipPath, pattern, filter, style, etc.) that is never referenced
anywhere else in the file via url(#id) or href="#id" -- the exact same
"unused" check the audit script reports, applied for real this time.

Safety:
  - Writes a .bak copy of every file it touches before modifying it.
  - Never touches elements outside <defs>, so it can't affect anything
    that's actually painted on screen.
  - Skips <style> elements entirely by default (they're often referenced
    by CSS class, e.g. class="ColorScheme-Text", which this tool can't
    verify -- so it's safer to leave them alone). Use --include-style to
    force-check them too.

Usage:
    python3 svg_remove_unused_defs.py /path/to/awp/template-icon-presets/neon
    python3 svg_remove_unused_defs.py neon --dry-run     # preview only, no writes
    python3 svg_remove_unused_defs.py neon --no-backup   # skip .bak files
"""

import sys
import re
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

NS_URI = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS_URI)

URL_REF_RE = re.compile(r"url\(#([^)]+)\)")


def local_tag(elem):
    return elem.tag.split("}")[-1]


def collect_def_ids(root, include_style):
    def_ids = {}  # id -> (defs_elem, child_elem)
    for defs in root.iter():
        if local_tag(defs) == "defs":
            for child in list(defs):
                tag = local_tag(child)
                if tag == "style" and not include_style:
                    continue
                _id = child.attrib.get("id")
                if _id:
                    def_ids[_id] = (defs, child)
    return def_ids


def collect_referenced_ids(root, raw_text):
    referenced = set(URL_REF_RE.findall(raw_text))
    for elem in root.iter():
        for attr, val in elem.attrib.items():
            if attr.endswith("href") and val.startswith("#"):
                referenced.add(val[1:])
    return referenced


def process_file(path: Path, dry_run: bool, make_backup: bool, include_style: bool):
    raw = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"[{path.name}] PARSE ERROR: {e} -- skipped")
        return

    def_ids = collect_def_ids(root, include_style)
    referenced = collect_referenced_ids(root, raw)
    unused = {i: pair for i, pair in def_ids.items() if i not in referenced}

    if not unused:
        return  # nothing to do, stay silent

    print(f"[{path.name}]")
    for _id, (defs, child) in unused.items():
        print(f"    removing <{local_tag(child)} id=\"{_id}\">")
        if not dry_run:
            defs.remove(child)

    if dry_run:
        print("    (dry-run, nothing written)\n")
        return

    # if a <defs> block ends up empty, drop it too (keeps files tidy)
    for defs in list(root.iter()):
        if local_tag(defs) == "defs" and len(list(defs)) == 0:
            parent_map = {c: p for p in root.iter() for c in p}
            parent = parent_map.get(defs)
            if parent is not None:
                parent.remove(defs)

    if make_backup:
        path.with_suffix(path.suffix + ".bak").write_text(raw, encoding="utf-8")

    new_content = ET.tostring(root, encoding="unicode")
    if not new_content.startswith("<?xml"):
        new_content = "<?xml version='1.0' encoding='UTF-8'?>\n" + new_content
    path.write_text(new_content, encoding="utf-8")
    print("    written.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--no-backup", action="store_true", help="Skip .bak files")
    parser.add_argument("--include-style", action="store_true",
                         help="Also remove <style> blocks if unreferenced by id/url "
                              "(risky -- they're often used via CSS class instead)")
    args = parser.parse_args()

    target = Path(args.directory)
    if not target.is_dir():
        print(f"Not a directory: {target}")
        sys.exit(1)

    svg_files = sorted(target.glob("*.svg"))
    if not svg_files:
        print("No .svg files found.")
        sys.exit(0)

    print(f"Processing {len(svg_files)} files in {target}"
          f"{' (dry run)' if args.dry_run else ''}\n")

    for f in svg_files:
        process_file(f, args.dry_run, not args.no_backup, args.include_style)

    print("Done.")


if __name__ == "__main__":
    main()

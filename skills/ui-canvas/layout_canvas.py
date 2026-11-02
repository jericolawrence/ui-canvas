#!/usr/bin/env python3
"""Place artboards on a Design canvas the way the Drive UI canvas (249oVPZ7) is laid out.

usage: layout_canvas.py layout.json canvas.json

Writes canvas.json. If it already exists, everything in it is kept and the new rows go below
what is on the target page (or on a new page). The layout.json shape is in SKILL.md.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

GAP = 80          # between frames in a row
ROW_GAP = 380     # tallest frame of a row to the next row's frames; holds the row title
TITLE_ABOVE = 260
STICKY_W = 420
HEADER_TITLE_Y = -1000
HEADER_STICKY_Y = -770
FILE_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*\.dc\.html$")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(layout_path, canvas_path):
    layout = json.loads(Path(layout_path).read_text())
    canvas_path = Path(canvas_path)
    if canvas_path.exists():
        canvas = json.loads(canvas_path.read_text())
    else:
        canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": now()}, "title": layout["title"],
                  "launch": {"view": "canvas"}, "pages": [], "boards": {}, "order": [], "notes": {},
                  "designSystems": []}
    boards, order, notes, pages = canvas["boards"], canvas["order"], canvas["notes"], canvas["pages"]

    page = layout.get("page")
    page_id = page["id"] if page else (pages[0]["id"] if pages else None)
    if page and not any(p["id"] == page_id for p in pages):
        # Artboards without a `page` live on the first page; keep them there.
        if not pages and boards:
            pages.append({"id": "main", "name": "Main"})
        pages.append({"id": page_id, "name": page["name"]})
    first_page = pages[0]["id"] if pages else None

    def on_page(entry):
        return entry.get("page", first_page) == page_id

    def tag(entry):
        if page_id is not None and page_id != first_page:
            entry["page"] = page_id
        return entry

    def note_id(stem):
        n, base = 0, re.sub(r"[^A-Za-z0-9_-]", "-", f"{page_id or 'p'}-{stem}")[:34]
        while f"{base}{n}" in notes:
            n += 1
        return f"{base}{n}"

    existing = [b for b in boards.values() if on_page(b)]
    if existing:
        y = max(b["y"] + b["h"] for b in existing) + ROW_GAP
    else:
        y = 0
        notes[note_id("t")] = tag({"x": 0, "y": HEADER_TITLE_Y, "text": layout["title"], "kind": "title1",
                                    "maxW": 3000})
        for i, s in enumerate(layout.get("stickies", [])):
            notes[note_id("s")] = tag({"x": i * 1080, "y": HEADER_STICKY_Y, "w": 1000, "maxH": s.get("maxH", 260),
                                        "size": 22, "fill": s.get("fill", "blue"), "text": s["text"]})

    for row in layout["rows"]:
        x = 0
        for f in row["frames"]:
            name = f["file"]
            if not FILE_RE.match(name) or name in boards:
                sys.exit(f"bad or duplicate artboard file: {name!r}")
            boards[name] = tag({"x": x, "y": y, "w": f["w"], "h": f["h"], "title": f["title"]})
            order.append(name)
            x += f["w"] + GAP
        notes[note_id("row")] = tag({"x": 0, "y": y - TITLE_ABOVE, "text": row["title"], "kind": "title1",
                                      "maxW": max(x - GAP, 1330)})
        if row.get("note"):
            notes[note_id("n")] = tag({"x": x, "y": y, "w": STICKY_W, "maxH": STICKY_W, "size": 22,
                                        "fill": row.get("noteFill", "gray"), "text": row["note"]})
        y += max(f["h"] for f in row["frames"]) + ROW_GAP

    canvas_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_path.write_text(json.dumps(canvas, indent=1, ensure_ascii=False))
    print(f"{sum(len(r['frames']) for r in layout['rows'])} frames in {len(layout['rows'])} rows"
          f"{f' on page {page_id}' if page_id else ''} -> {canvas_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

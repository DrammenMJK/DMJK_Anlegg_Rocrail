"""Extract and draw the Solberg portion of a Rocrail plan.

Usage: python solberg_plan.py [PLAN.xml]
       python solberg_plan.py --check
"""
import argparse
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
BOUNDS = (1, 36, 1, 8)
CELL = 56


def extract_plan(xml_path, report_path):
    root = ET.parse(xml_path).getroot()
    report = report_path.read_text(encoding="utf-8").split("## Solberg (s)", 1)[1]
    report = report.split("## Solberg Skiftegård", 1)[0]
    references = sorted(set(re.findall(r"\b(?:ss\d+|sv\d+|gv\d+)\b", report)))
    objects = []
    for tag in ("tk", "sw", "sg", "fb", "bk"):
        for element in root.findall(f"./{tag}list/{tag}"):
            x, y, z = (int(element.get(key, "0")) for key in ("x", "y", "z"))
            if z != 0 or not (BOUNDS[0] <= x <= BOUNDS[1] and BOUNDS[2] <= y <= BOUNDS[3]):
                continue
            if tag == "fb" and element.get("desc"):
                continue
            item = {"kind": tag, "id": element.get("id"), "x": x, "y": y, "z": z}
            for key in ("type", "ori", "state", "blockid", "signal", "dwarf", "smallsymbol"):
                if element.get(key) is not None:
                    item[key] = element.get(key)
            if tag in ("sg", "sw"):
                item["referenced"] = item["id"] in references
            objects.append(item)
    found = {item["id"] for item in objects}
    return {
        "station": "Solberg",
        "source_xml": xml_path.name,
        "source_report": report_path.name,
        "description": "Rocrail schematic grid, not a physical or live track plan.",
        "bounds": dict(zip(("min_x", "max_x", "min_y", "max_y"), BOUNDS)),
        "report_references": references,
        "references_outside_drawing": sorted(set(references) - found),
        "objects": objects,
    }


def rotated_path(path, orientation):
    angle = {"west": 0, "north": 270, "east": 180, "south": 90}.get(orientation, 0)
    return f'<path d="{path}" transform="rotate({angle} 16 16)"/>'


def track_shape(item):
    kind, typ = item["kind"], item.get("type", "")
    orientation = item.get("ori", "west")
    if kind == "tk" and typ == "curve":
        return rotated_path("M 0 16 L 16 32", orientation)
    if kind == "tk" and typ == "buffer":
        return rotated_path("M 0 16 H 26 M 26 9 V 23", orientation)
    if kind == "sw":
        if typ == "crossing":
            return '<path d="M 0 16 H 32 M 16 0 V 32"/>'
        if typ in ("left", "right"):
            branch = "M 32 16 L 16 32" if typ == "left" else "M 0 16 L 16 32"
            return '<path d="M 0 16 H 32"/>' + rotated_path(branch, orientation)
    if kind == "bk":
        return '<path d="M 0 16 H 64"/>'
    if orientation in ("north", "south"):
        return '<path d="M 16 0 V 32"/>'
    return '<path d="M 0 16 H 32"/>'


def render_object(item):
    x = (item["x"] - BOUNDS[0]) * CELL
    y = (item["y"] - BOUNDS[2]) * CELL
    kind = item["kind"]
    title = html.escape(" · ".join(f"{key}: {value}" for key, value in item.items()))
    parts = [f'<g transform="translate({x} {y})"><title>{title}</title>',
             f'<g class="track" transform="scale({CELL / 32})">{track_shape(item)}</g>']
    if kind in ("sg", "sw", "bk", "fb"):
        name = html.escape(item["id"])
        if kind == "sg":
            # Saved aspects are metadata, not an indication of the current railway state.
            parts.append('<circle class="signal" cx="28" cy="28" r="5"/>')
            parts.append(f'<text class="signal-label" x="28" y="15">{name}</text>')
        elif kind == "sw":
            parts.append(f'<text class="turnout-label" x="28" y="48">{name}</text>')
        elif kind == "bk":
            parts.append(f'<text class="block-label" x="56" y="23">{name}</text>')
        else:
            parts.append(f'<circle class="sensor" cx="28" cy="28" r="3"/><text class="sensor-label" x="28" y="48">{name}</text>')
    parts.append("</g>")
    return "".join(parts)


def render_html(plan):
    width = (BOUNDS[1] - BOUNDS[0] + 1) * CELL
    height = (BOUNDS[3] - BOUNDS[2] + 1) * CELL
    drawing = "\n".join(render_object(item) for item in plan["objects"])
    missing = ", ".join(plan["references_outside_drawing"]) or "none"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solberg station — Rocrail schematic</title>
<style>
body {{ margin: 0; background: #f3f5f7; color: #17212b; font: 16px system-ui, sans-serif; }}
main {{ max-width: 1500px; margin: auto; padding: 1.5rem; }}
h1 {{ margin: 0 0 .4rem; }} p {{ line-height: 1.45; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 1rem; font-size: .9rem; }}
.canvas {{ overflow: auto; background: white; border: 1px solid #cbd5df; border-radius: 8px; margin: 1rem 0; }}
svg {{ display: block; min-width: {width}px; }}
.track {{ fill: none; stroke: #34495e; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
text {{ text-anchor: middle; font: bold 12px system-ui, sans-serif; paint-order: stroke; stroke: white; stroke-width: 3px; stroke-linejoin: round; }}
.signal {{ fill: #394eaf; stroke: white; stroke-width: 2; }}
.signal-label {{ fill: #293d9e; }} .turnout-label {{ fill: #a44c12; }}
.block-label {{ fill: #16634c; }} .sensor-label {{ fill: #657280; font-size: 10px; }}
.sensor {{ fill: #657280; stroke: white; stroke-width: 1; }}
</style>
</head>
<body><main>
<h1>Solberg station</h1>
<p>Rocrail grid schematic from <strong>{html.escape(plan["source_xml"])}</strong>, with the adjacent Skiftegård connection. This is not a scale drawing or live railway status. Signal dots show locations, not aspects; turnout lines show both possible paths, not their current setting.</p>
<div class="legend"><span>🔵 Signal</span><span style="color:#a44c12">Turnout / crossing</span><span style="color:#16634c">Block</span><span style="color:#657280">● Detector</span><span>Hover for XML details; scroll horizontally to see the full plan.</span></div>
<div class="canvas"><svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Rocrail schematic of Solberg station">
{drawing}
</svg></div>
<p>Coordinates and saved attributes are in <code>solberg.json</code>. Report references outside this drawing: {html.escape(missing)}.</p>
</main></body></html>
"""


def self_check(plan, drawing):
    objects = {item["id"]: item for item in plan["objects"]}
    assert not plan["references_outside_drawing"], plan["references_outside_drawing"]
    assert (objects["ss01"]["x"], objects["ss01"]["y"]) == (3, 5)
    assert (objects["gv01"]["x"], objects["gv01"]["y"]) == (27, 3)
    assert objects["sx"]["type"] == "crossing"
    assert "sd05" not in objects
    assert 'M 0 16 H 32 M 16 0 V 32' in drawing
    assert all(f">{name}</text>" in drawing for name in plan["report_references"])
    assert "not a scale drawing or live railway status" in drawing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true", help="run checks without writing output")
    args = parser.parse_args()
    xml_path = args.xml or max(ROOT.glob("*-DMJK-Layout.xml"), key=lambda path: path.name)
    plan = extract_plan(xml_path, ROOT / "signal_logic.md")
    if args.check:
        self_check(plan, render_html(plan))
        print("Solberg extraction and drawing checks passed.")
        return
    json_path = ROOT / "solberg.json"
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    saved_plan = json.loads(json_path.read_text(encoding="utf-8"))
    (ROOT / "solberg.html").write_text(render_html(saved_plan), encoding="utf-8")
    print(f"Wrote solberg.json and solberg.html from {xml_path.name}.")


if __name__ == "__main__":
    main()

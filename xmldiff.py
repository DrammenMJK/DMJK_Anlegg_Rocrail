"""Element-level diff of two Rocrail plan XML files.

Usage: python xmldiff.py OLD.xml NEW.xml [OUT.txt]

Elements are matched by path, using the id attribute where present,
else the position among same-tag siblings. Reports added/removed
elements and changed attributes/text.
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter


def flatten(root):
    """Map element path -> (attrib, text) for every element."""
    out = {}

    def walk(el, path):
        out[path] = (dict(el.attrib), (el.text or "").strip())
        seen = Counter()
        for child in el:
            # Same id can repeat among siblings (e.g. two actionctrl), so number them.
            key = child.get("id", "")
            seen[(child.tag, key)] += 1
            n = seen[(child.tag, key)]
            key = f"{key}#{n}" if not key or n > 1 else key
            walk(child, f"{path}/{child.tag}[{key}]")

    walk(root, root.tag)
    return out


def diff(old, new):
    lines, attr_stats = [], Counter()
    for path in sorted(old.keys() - new.keys()):
        lines.append(f"REMOVED {path} {old[path][0]}")
    for path in sorted(new.keys() - old.keys()):
        lines.append(f"ADDED   {path} {new[path][0]}")
    for path in sorted(old.keys() & new.keys()):
        (oa, ot), (na, nt) = old[path], new[path]
        for name in sorted(oa.keys() | na.keys()):
            if oa.get(name) != na.get(name):
                attr_stats[name] += 1
                lines.append(f"CHANGED {path} @{name}: {oa.get(name)!r} -> {na.get(name)!r}")
        if ot != nt:
            attr_stats["#text"] += 1
            lines.append(f"CHANGED {path} text: {ot!r} -> {nt!r}")
    return lines, attr_stats


def main():
    old_file, new_file = sys.argv[1], sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else "xmldiff.txt"
    lines, stats = diff(flatten(ET.parse(old_file).getroot()),
                        flatten(ET.parse(new_file).getroot()))
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# {old_file} -> {new_file}\n# changed attribute counts: {dict(stats.most_common())}\n")
        f.write("\n".join(lines) + "\n")
    print(f"{len(lines)} differences written to {out_file}")
    print(dict(stats.most_common()))


if __name__ == "__main__":
    main()

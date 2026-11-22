"""Compare addresses in DMJK-Adresser.pdf with a Rocrail plan XML.

Usage: python pdfcheck.py PDF XML [OUT.txt] [--json ERRORS.json]
       python pdfcheck.py --check

Needs pdftotext (poppler) on PATH. The -raw mode keeps each table row on one line.
Signals and level-crossing outputs: set of DCC addresses vs sg port1-4 / co port.
Switches: DCC address vs sw port1. Detectors: sensor address vs fb addr.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict

NAME = r"([a-z]{2}[A-Za-z]*\d+)"
SIGNAL_ROW = re.compile(rf"^{NAME} \S+ \d+ (?:\S+ )?\d+ (\d+)\b")
SWITCH_ROW = re.compile(r"^([a-z]v\d+(?:, [a-z]v\d+)*) \d+ \d+ \d+ (\d+)\b")
DETECTOR_ROW = re.compile(rf"^{NAME}(?: \S+)*? \d+ \d+ \d+ (\d+)\b")
ADDRESS_FIELDS = {"sg": ("port1", "port2", "port3", "port4"), "co": ("port",),
                  "sw": ("port1", "port2"), "fb": ("addr",)}
DECODER_FIELDS = {"sg": ("addr", "addr2", "addr3", "addr4"), "co": ("addr",),
                  "sw": ("addr1", "addr2"), "fb": ()}


def parse_pdf(pdf):
    """Return {kind: {name: set(addresses)}}; kind is signal, switch or detector."""
    text = subprocess.run(["pdftotext", "-raw", pdf, "-"], capture_output=True,
                          check=True).stdout.decode("utf-8", "replace")
    found = defaultdict(lambda: defaultdict(set))
    kind = None
    for line in text.splitlines():
        if line.startswith("Signal /"):
            kind = "signal"
        elif line.startswith("Veksel:"):
            kind = "switch"
        elif "Detektor:" in line or "detektor-adresser" in line:
            kind = "detector"
        elif line.startswith("Havna"):
            kind = None
        row = {"signal": SIGNAL_ROW, "switch": SWITCH_ROW, "detector": DETECTOR_ROW}.get(kind)
        m = row and row.match(line)
        if m:
            for name in m.group(1).split(", "):
                found[kind][name].add(int(m.group(2)))
    return found


def xml_addresses(xml):
    """Return {id: (tag, set(addresses), iid)} for sg, co, sw and fb."""
    out = {}
    root = ET.parse(xml).getroot()
    for tag, names in ADDRESS_FIELDS.items():
        for el in root.iter(tag):
            ports = {int(el.get(a, 0)) for a in names} - {0}
            out[el.get("id")] = (tag, ports, el.get("iid", ""))
    return out


def compare(pdf, xml):
    lines, by_address = [], defaultdict(list)
    for kind, names in pdf.items():
        for name, addresses in sorted(names.items()):
            tag, ports, iid = xml.get(name, (None, set(), ""))
            for a in addresses:
                by_address[(kind, a)].append(name)
            if tag is None:
                status = "NOT IN XML"
            elif ports == addresses:
                continue
            else:
                status = f"MISMATCH xml <{tag}> {sorted(ports)}" + (f" iid={iid}" if iid else "")
            lines.append(f"{kind:8} {name:8} pdf {sorted(addresses)}  {status}")
    # XML objects whose address the PDF gives to another name of the same kind.
    kind_of = {"sg": "signal", "co": "signal", "sw": "switch", "fb": "detector"}
    for oid, (tag, ports, iid) in sorted(xml.items()):
        for p in ports:
            owners = by_address.get((kind_of[tag], p), [])
            if owners and oid not in owners and not iid:
                lines.append(f"{kind_of[tag]:8} {oid:8} xml <{tag}> {p} is {owners} in pdf")
    return lines


def address_findings(pdf, root):
    allowed = {"signal": ("sg", "co"), "switch": ("sw",), "detector": ("fb",)}
    objects = {(tag, element.get("id")): element for tag in ADDRESS_FIELDS
               for element in root.findall(f"./{tag}list/{tag}")}
    findings = []
    for category, names in pdf.items():
        for name, expected in sorted(names.items()):
            found = [(tag, objects[(tag, name)]) for tag in allowed[category] if (tag, name) in objects]
            if len(found) != 1:
                continue
            tag, element = found[0]
            if element.get("iid", "").lower() == "vrt":
                continue
            if any(element.get(field, "0") not in ("0", "") for field in DECODER_FIELDS[tag]):
                continue
            fields = ADDRESS_FIELDS[tag]
            observed = {field: element.get(field) for field in fields
                        if element.get(field, "0") not in ("0", "")}
            actual = {int(value) for value in observed.values()}
            if actual != expected:
                findings.append({"kind": tag, "id": name, "category": category,
                                 "attributes": list(fields), "decoder_attributes": list(DECODER_FIELDS[tag]),
                                 "observed": observed,
                                 "expected": sorted(expected)})
    return findings


def self_check():
    pdf = {"signal": {"is03": {1005, 1006}, "yoP1": {1017}, "si01": {1001}},
           "switch": {"iv02": {113}}, "detector": {"yoP1": {689}}}
    root = ET.fromstring("""<plan><sglist><sg id="is03" port1="1005" port2="1005"/></sglist>
      <colist><co id="yoP1" port="1025"/></colist>
      <swlist><sw id="iv02" port1="412" iid="vrt"/></swlist></plan>""")
    findings = address_findings(pdf, root)
    assert {(item["kind"], item["id"]) for item in findings} == {("sg", "is03"), ("co", "yoP1")}
    assert findings[0]["observed"] == {"port1": "1005", "port2": "1005"}
    root.find("./sglist/sg").set("port2", "1006")
    assert [item["id"] for item in address_findings(pdf, root)] == ["yoP1"]
    root.find("./colist/co").set("addr", "3")
    assert not address_findings(pdf, root)
    print("Address analysis checks passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path)
    parser.add_argument("xml", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path, default=Path("pdfcheck.txt"))
    parser.add_argument("--json", type=Path, default=Path(__file__).resolve().parent / "drawings" / "error.json",
                        help="structured address findings for the drawings")
    parser.add_argument("--check", action="store_true", help="run address analysis checks")
    args = parser.parse_args()
    if args.check:
        self_check()
        return
    if args.pdf is None or args.xml is None:
        parser.error("PDF and XML are required")
    pdf_file, xml_file, out_file = args.pdf, args.xml, args.output
    inputs = {pdf_file.resolve(), xml_file.resolve()}
    if out_file.resolve() in inputs or args.json.resolve() in inputs or out_file.resolve() == args.json.resolve():
        parser.error("output files must be distinct from the PDF, XML and each other")
    pdf = parse_pdf(str(pdf_file))
    missing = [category for category in ("signal", "switch", "detector") if not pdf.get(category)]
    if missing:
        parser.error(f"PDF has no recognised address table for: {', '.join(missing)}")
    lines = compare(pdf, xml_addresses(xml_file))
    findings = address_findings(pdf, ET.parse(xml_file).getroot())
    document = {"source_pdf": pdf_file.name, "source_xml": xml_file.name,
                "source_xml_sha256": hashlib.sha256(xml_file.read_bytes()).hexdigest(),
                "findings": findings}
    args.json.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# {pdf_file} vs {xml_file}\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"{len(lines)} findings written to {out_file}")
    print(f"{len(findings)} address mismatches written to {args.json}")


if __name__ == "__main__":
    main()

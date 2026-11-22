"""Scan Rocrail/Rocview trace files for messages that point to problems.

Usage: python trc_issues.py [OUT.md] [FILE.trc ...]   (default: all *.trc here, trc_issues.md)

Trace line format: YYYYMMDD.HHMMSS.mmm <r|g>9999<level> <thread> <module> <line> <message>
Level W/E are warnings/exceptions. Some info-level messages are also listed,
because they show missing objects, broken connections or manual operator actions.
"""
import glob
import re
import sys
from collections import defaultdict

LINE = re.compile(r"^(\d{8}\.\d{6}\.\d{3}) [rg]\d{4}(\S) +(\S+) +(\S+) +(\d+) (.*)$")

# (category, regex on message). First match wins.
RULES = [
    ("Unregistered sensor (address not in plan)", r"unregistered sensor event"),
    ("Connection problem", r"\*broken\*|disconnect|reader ended|connection|timeout|refused"),
    ("Error / exception", r"(?i)\berror\b|exception|fail"),
    ("Output without address", r"has no address set"),
    ("Route not locked", r"route \S+ is not locked"),
    ("Manual sensor change by operator", r"sendToRocrail\( <fb "),
    ("Manual signal change by operator", r"sendToRocrail\( <sg "),
    ("Manual output change by operator", r"sendToRocrail\( <co "),
]


def classify(level, message):
    for category, pattern in RULES:
        if re.search(pattern, message):
            return category
    return "Warning" if level in "WwEe" else None


def scan(path):
    """Return {category: {message: [times]}}."""
    found = defaultdict(lambda: defaultdict(list))
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = LINE.match(line.rstrip())
            if not m:
                continue  # XML dumps and other continuation lines
            time, level, _thread, module, _no, message = m.groups()
            category = classify(level, message)
            if category:
                found[category][f"{module}: {message.strip()}"].append(time)
    return found


def fmt(t):
    return f"{t[0:4]}-{t[4:6]}-{t[6:8]} {t[9:11]}:{t[11:13]}:{t[13:15]}"


def report(files):
    out = ["# Trace file issues", ""]
    for path in files:
        found = scan(path)
        out += [f"## {path}", ""]
        if not found:
            out += ["No issues found.", ""]
        for category, messages in found.items():
            out += [f"### {category}", "",
                    "| Count | First               | Last                | Message |",
                    "|------:|---------------------|---------------------|---------|"]
            for message, times in messages.items():
                text = message.replace("|", "\\|")
                out.append(f"| {len(times):5} | {fmt(times[0])} | {fmt(times[-1])} | `{text}` |")
            out.append("")
    return "\n".join(out)


def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else "trc_issues.md"
    files = sys.argv[2:] or sorted(glob.glob("*.trc"))
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report(files))
    print(f"{len(files)} files scanned, report written to {out_file}")


if __name__ == "__main__":
    main()

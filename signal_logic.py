"""List the action logic around signals in a Rocrail plan.

Usage: python signal_logic.py PLAN.xml [OUT.md]

1. Turnouts (sw) that affect signals (as trigger or as condition of a signal action).
2. Sensors (track sections) that stop a signal from showing a proceed aspect:
   a "must be free" condition on a green/yellow/white action, or a red action
   triggered when the sensor goes occupied. Also routes that set signals.
3. Other actions: everything that isn't a signal aspect action.

Rocrail semantics: an <actionctrl> on object X runs action <ac id=...> when X
reaches actionctrl/@state. allconditions="true" means all conditions must hold;
"false" means at least one, plus every condition with mustbetrue="true".
"""
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict

PROCEED = {"green", "yellow", "white"}
CALLER_TAGS = ("sw", "fb", "co", "sg", "st", "vr")


class Trigger:
    """One actionctrl: caller object + state fires action, under conditions."""

    def __init__(self, caller_tag, caller_id, ctrl, action):
        self.caller = f"{caller_tag}:{caller_id}"
        self.caller_tag, self.caller_id = caller_tag, caller_id
        self.state = ctrl.get("state") or "any"
        self.desc = ctrl.get("desc", "")
        self.action = action
        self.all = ctrl.get("allconditions", "true") == "true"
        self.conds = [c.attrib for c in ctrl.findall("actioncond")]

    @property
    def target(self):
        return self.action.get("oid", "") if self.action is not None else ""

    @property
    def command(self):
        return self.action.get("cmd", "") if self.action is not None else ""

    @property
    def action_type(self):
        return self.action.get("type", "?") if self.action is not None else "missing"

    def conditions_text(self):
        def term(c):
            return f"{c['type']}:{c['id']}={c.get('state', '')}"
        required = [term(c) for c in self.conds if self.all or c.get("mustbetrue") == "true"]
        optional = [term(c) for c in self.conds if not self.all and c.get("mustbetrue") != "true"]
        parts = required + ([f"({' or '.join(optional)})"] if optional else [])
        return " and ".join(parts) or "-"

    def is_required(self, cond):
        return self.all or cond.get("mustbetrue") == "true" or len(self.conds) == 1


def load(path):
    root = ET.parse(path).getroot()
    actions = {a.get("id"): a for a in root.iter("ac")}
    triggers = []
    for tag in CALLER_TAGS:
        for el in root.iter(tag):
            for ctrl in el.findall("actionctrl"):
                triggers.append(Trigger(tag, el.get("id"), ctrl, actions.get(ctrl.get("id"))))
    block_of = {}
    for bk in root.iter("bk"):
        for ev in bk.findall("fbevent"):
            block_of.setdefault(ev.get("id"), bk.get("id"))
    for fb in root.iter("fb"):
        if fb.get("blockid"):
            block_of.setdefault(fb.get("id"), fb.get("blockid"))
    return root, triggers, block_of


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in sorted(rows)]
    return out + [""]


STATIONS = {"s": "Solberg (s)", "g": "Solberg Skiftegård (g)", "k": "Kobbarvik (k)", "m": "Mjøndalen (m)",
            "y": "Myra (y)", "i": "Sigdal (i)", "n": "Norbotten (n)", "h": "Havna (h)"}


def station(object_id):
    """Station name from the first letter of an object id, as in DMJK-Adresser.pdf."""
    return STATIONS.get(object_id[:1], "Other")


class Section:
    """One report table; key(row) gives the object id that decides the station."""

    def __init__(self, title, note, header, rows, key):
        self.title, self.note, self.header, self.rows, self.key = title, note, header, rows, key

    def for_station(self, name):
        rows = {r for r in self.rows if station(self.key(r)) == name}
        if not rows:
            return []
        return [f"### {self.title}", "", *([self.note, ""] if self.note else []), *table(self.header, rows)]


def switches_affecting_signals(triggers):
    rows = set()
    for t in triggers:
        if t.action_type != "sg":
            continue
        if t.caller_tag == "sw":
            rows.add((t.target, t.command, t.caller_id, f"trigger when {t.state}", t.conditions_text()))
        for c in t.conds:
            if c["type"] == "sw":
                how = "required" if t.is_required(c) else "one of (or)"
                rows.add((t.target, t.command, c["id"], f"condition {c.get('state')} ({how}), trigger {t.caller}={t.state}",
                          t.conditions_text()))
    return Section("1. Turnouts that affect signals", "",
                   ["Signal", "Aspect", "Turnout", "How", "Full condition"], rows, lambda r: r[0])


def sensors_blocking_signals(triggers, block_of):
    rows = set()
    for t in triggers:
        if t.action_type != "sg":
            continue
        if t.command in PROCEED:
            for c in t.conds:
                if c["type"] == "fb" and c.get("state") == "false":
                    how = "must be free" if t.is_required(c) else "one of (or) must be free"
                    rows.add((t.target, t.command, c["id"], block_of.get(c["id"], ""),
                              f"{how}; trigger {t.caller}={t.state}"))
        if t.command == "red" and t.caller_tag == "fb" and t.state == "true":
            rows.add((t.target, "red", t.caller_id, block_of.get(t.caller_id, ""),
                      f"occupied sets red; condition {t.conditions_text()}"))
    return Section("2. Sensors that stop signals from showing proceed",
                   "Sensor conditions on green/yellow/white actions, and red actions triggered when a sensor goes occupied.",
                   ["Signal", "Aspect", "Sensor", "Block", "How"], rows, lambda r: r[0])


def routes_setting_signals(root):
    rows = set()
    for st in root.iter("st"):
        for cmd in st.findall("swcmd"):
            if cmd.get("type") == "sg" and cmd.get("atfree") != "true":
                rows.add((cmd.get("id"), cmd.get("cmd"), st.get("id"), f"{st.get('bka')} -> {st.get('bkb')}"))
    return Section("2.1 Routes that set signals",
                   "Rocrail sets these aspects only when it can lock the route, so an occupied destination block stops them.",
                   ["Signal", "Aspect when set", "Route", "From -> to block"], rows, lambda r: r[0])


def signal_chains(triggers):
    rows = {(t.target, t.command, t.caller_id, t.state, t.conditions_text())
            for t in triggers if t.action_type == "sg" and t.caller_tag == "sg"}
    return Section("3.1 Signals triggered by other signals", "",
                   ["Signal", "Aspect", "Triggered by signal", "When", "Conditions"], rows, lambda r: r[0])


def other_actions(triggers):
    rows = set()
    for t in triggers:
        if t.action_type == "sg" or t.action is None:
            continue
        rows.add((t.target or t.caller_id, t.action_type, t.action.get("id"), t.command,
                  f"{t.caller}={t.state}", t.conditions_text(), t.desc))
    return Section("3.2 Actions that don't set a signal", "",
                   ["Target", "Type", "Action", "Command", "Trigger", "Conditions", "Desc"], rows, lambda r: r[0])


def missing_actions(triggers):
    rows = {(t.caller, t.state) for t in triggers if t.action is None}
    return table(["Caller", "State"], rows) if rows else ["None.", ""]


def main():
    plan = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "signal_logic.md"
    root, triggers, block_of = load(plan)
    sections = [switches_affecting_signals(triggers), sensors_blocking_signals(triggers, block_of),
                routes_setting_signals(root), signal_chains(triggers), other_actions(triggers)]
    md = [f"# Signal logic in {plan}", "",
          "Grouped by station, from the first letter of the signal or target id.",
          "Conditions: `type:id=state`. `and` = all required, `(a or b)` = at least one.", ""]
    intro = Path(__file__).with_name("signal_logic_intro.md")
    if intro.exists():
        md += [intro.read_text(encoding="utf-8"), ""]
    for name in [*STATIONS.values(), "Other"]:
        body = [line for s in sections for line in s.for_station(name)]
        if body:
            md += [f"## {name}", "", *body]
    md += ["## Action controls that point to a missing action", "", *missing_actions(triggers)]
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"{len(triggers)} action controls, report written to {out_file}")


if __name__ == "__main__":
    main()

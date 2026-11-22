"""Generate offline Rocrail station drawings and their JSON data.

Usage: python drawings\\stations.py [PLAN.xml]
       python drawings\\stations.py --check
"""
import argparse
from collections import deque
import hashlib
import html
from itertools import groupby
import json
from pathlib import Path
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path(__file__).resolve().parent
CELL = 56
STATIONS = {
    "solberg": ("Solberg", "s", [(1, 36, 1, 8)]),
    "skiftegaard": ("Solberg Skiftegård", "g", [(25, 43, 1, 5)]),
    "kobbarvik": ("Kobbarvik", "k", [(40, 55, 2, 8)]),
    "mjondalen": ("Mjøndalen", "m", [(0, 24, 11, 19), (49, 55, 5, 7)]),
    "myra": ("Myra", "y", [(23, 35, 13, 26)]),
    "sigdal": ("Sigdal", "i", [(34, 55, 11, 22)]),
    "norbotten": ("Norbotten", "n", [(1, 30, 19, 30)]),
    "havna": ("Havna", "h", [(47, 55, 6, 9)]),
}
PANEL_INPUTS = {
    "sd05", "sd06", "sd07", "sd08", "sd18", "sd19", "sd21",
    "gd08", "gd09", "gd10", "gd11", "md09", "md10", "md11", "md12", "md13", "md14",
    "id16", "id17", "id18", "id19", "id20", "id21", "hd02", "hd03",
}
PANEL_STATIONS = {**{letter: name for name, letter, _ in STATIONS.values()}, "r": "Rognmo"}
# Module allocations come from DMJK-Adresser.pdf; the XML supplies configured inputs.
FEEDBACK_MODULES = [
    ("s#1", "RS-8", 65), ("s#2", "RS-8", 66), ("s#3", "RS-16-O", 67),
    ("g#1", "RS-8", 73), ("k#1", "RS-8", 81),
    ("m#1", "RS-8", 85), ("m#2", "RS-16-O", 86), ("y#1", "RS-8", 93),
    ("i#1", "RS-8", 97), ("i#2", "RS-8", 98), ("i#3", "RS-16-O", 99),
    ("i#5 test", "RS-16-O", 101),
    ("n#1", "RS-8", 105), ("n#2", "RS-8", 106),
    ("n#3", "RS-8", 107), ("n#4", "RS-8", 108),
]
# LS100 port assignments and DCC addresses are documented in DMJK-Adresser.pdf.
LS100_MODULES = [
    ("s#1", 1, 1, ("sv01", "sv02", "sv03", "sv04")),
    ("s#2", 2, 5, ("sv05", "sv07", "sv08", "sv09")),
    ("s#3", 3, 9, ("sv10", "sv11 sv12", "sv13 sv14", "sv15")),
    ("g#1", 9, 33, ("gv01", "gv02", "gv03", "gv04")),
    ("g#2", 10, 37, ("gv05", "gv06", "", "sv06")),
    ("k#1", 17, 65, ("kv01 kv02", "kv03", "kv04 kv05", "kv07")),
    ("k#2", 18, 69, ("kv06", "", "", "")),
    ("m#1", 21, 81, ("mv01 mv02", "mv03", "mv04", "mv06")),
    ("m#2", 22, 85, ("mv08", "mv11", "mv12 mv13", "mv14")),
    ("y#1", 25, 97, ("", "", "yv01", "yv02")),
    ("y#2", 26, 101, ("yv03", "yv04", "yv05", "yv06 yv07")),
    ("y#3", 27, 105, ("yv08", "yv09", "", "")),
    ("i#1", 29, 113, ("iv01 iv02", "", "iv04", "iv05")),
    ("i#2", 30, 117, ("iv06", "iv07", "iv08", "iv09")),
    ("i#3", 31, 121, ("iv10", "iv11", "iv12", "iv13")),
    ("i#4", 32, 125, ("iv14 iv15", "iv16 iv17", "iv18", "iv19")),
    ("i#5", 33, 129, ("iv20", "iv21", "iv22", "iv23")),
    ("i#6", 34, 133, ("iv24", "iv25", "iv26", "iv27")),
    ("n#1", 37, 145, ("nv01", "nv02", "nv03", "nv04")),
    ("n#2", 38, 149, ("nv05", "nv06", "nv07", "")),
    ("n#3", 39, 153, ("nv08", "nv09", "nv10", "nv11")),
    ("n#4", 40, 157, ("nv12", "nv13", "nv14", "nv15")),
]
# OD-2 assignments: signal ID, documented output ports, and first/last DCC address.
SIGNAL_MODULES = [
    ("s#1", [("ss27", "1-2", 513, 514), ("ss28", "3-4", 515, 515),
             ("ss01", "5-6", 516, 517), ("is13", "7-8", 518, 519)]),
    ("s#2", [("ss06", "D1", 521, 522), ("ss05", "D2", 523, 524),
             ("ss07", "D3", 525, 526), ("ss26", "D4", 527, 528),
             ("ss23", "1-3", 529, 530), ("ss22", "4-5", 531, 531), ("ss24", "6-7", 532, 532)]),
    ("s#3", [("ss09", "D1", 537, 538), ("ss10", "D2", 539, 540),
             ("ss08", "D4", 543, 544), ("ss25", "1-2", 545, 545)]),
    ("s#4", [("ss11", "D1", 549, 550), ("ss12", "D2", 551, 552),
             ("ss13", "D3", 553, 554), ("ss15", "D4", 555, 556),
             ("ss18", "1-2", 557, 557), ("ss19", "5-6", 559, 559), ("ss21", "7-8", 560, 560)]),
    ("s#5", [("ss16", "1-5, 1-3", 561, 562), ("ss17", "4-5", 563, 564),
             ("ss20", "6-8", 565, 566), ("ss14", "D1", 567, 568)]),
    ("s#6", [("ss30", "7-8", 581, 581)]),
    ("g#1", [("gs04", "D1", 673, 674), ("gs05", "D2", 675, 676),
             ("gs06", "D3", 677, 678), ("gs07", "D4", 679, 680),
             ("gs03", "1-2", 681, 681), ("ss29", "3-4", 682, 683)]),
    ("g#2", [("gs08", "D1", 685, 686), ("gs09", "D2", 687, 688),
             ("gs10", "D4", 691, 692), ("gs02", "1-3", 693, 694),
             ("gs01", "4-5", 695, 696), ("gs11", "6-7", 697, 697)]),
    ("k#1", [("ks01", "1-3", 833, 834), ("ks03", "4-6", 835, 836), ("ks02", "7-8", 837, 837)]),
    ("m#1", [("ms03", "1-5, 1-3", 929, 930), ("ms02", "4-5", 931, 932),
             ("ms01", "6-7", 933, 934), ("ms05", "8", 935, 935)]),
    ("m#2", [("ms04", "1-3", 945, 946), ("ms06", "4", 947, 947),
             ("ms07", "5", 948, 948), ("ms08", "6", 949, 949)]),
    ("m#3", [("ms13", "1-3", 961, 962), ("ms09", "4", 963, 963),
             ("ms10", "5", 964, 964), ("ms11", "6", 965, 965)]),
    ("m#4", [("ms14", "1-5, 1-3", 977, 978), ("ms15", "4-5", 979, 980),
             ("ms16", "6-7", 981, 982), ("ms12", "8", 983, 983)]),
    ("y#1", [("ys01", "1-3", 985, 986), ("ys04", "4-6", 987, 988), ("ys06", "7-8", 989, 989)]),
    ("y#2", [("ys05", "1-3", 993, 994), ("ys02", "4-6", 995, 996), ("ys07", "7-8", 997, 997)]),
    ("i#1", [("is01", "1-5, 1-3", 1001, 1002), ("is02", "4-5", 1003, 1004),
             ("is03", "6-8", 1005, 1006)]),
]
TEST_FEEDBACK_INPUTS = {"fb26", "fb27", "fb28"}
# shortcut: other track-style output types are omitted until their symbols are identified.
TRACK_OUTPUT_TYPES = {"6", "7", "8", "11", "12"}
DESTINATIONS = {
    "solberg": [
        ("tk20131116001925260", "Sigdal", "left", 0, 0, "1"),
        ("tk20121118012606983", "Skiftegård / Kobbarvik", "right", 0, 0.5, None),
        ("tk20160110181012646", "Rognmo", "right", 0, 0, None),
    ],
    "skiftegaard": [
        ("sv13", "Solberg", "left", 0, 0.5, None),
        ("kv01", "Kobbarvik", "right", 0, 0.5, None),
    ],
    "kobbarvik": [
        ("tk20120531213042312", "Skiftegård / Solberg", "left", 0, 0.5, None),
        ("tk20131116002813019", "Myra", "right", 0, 0.5, "3"),
        ("tk20131116002811551", "Mjøndalen", "right", 0, 0, "2"),
        ("hd01", "Havna", "right", 0, 0, None),
    ],
    "mjondalen": [
        ("tk20131116224647069", "Kobbarvik", "left", 0, 0, "2"),
        ("ms16", "Myra", "right", 0, 0, None),
        ("tk20171018010922787", "Myra", "right", 0, 0, "4"),
        ("tk20131116002811551", "Mjøndalen", "right", 0, 0, "2"),
    ],
    "myra": [
        ("ms16", "Mjøndalen", "left", 0, 0, None),
        ("tk20130902230101613", "Sigdal", "right", 0, 0.5, None),
        ("tk20131116224401371", "Kobbarvik", "above-left", 0, 0, "3"),
        ("tk2130326262", "Norbotten", "bottom", 0.5, 0, None),
    ],
    "sigdal": [
        ("tk2130326263", "Myra", "left", 0, 0.5, None),
        ("tk20131116223951961", "Solberg", "right", 0, 0, "1"),
    ],
    "norbotten": [
        ("n-in", "Myra", "top", 0.5, 0, None),
        ("tk20131116224401371", "Kobbarvik", "left", 0, 0.5, "3"),
    ],
    "havna": [
        ("tk20120107221855944", "Kobbarvik", "top", 0, 0, None),
        ("tk20131116002811551", "Mjøndalen", "right", 0, 0, "2"),
        ("hd01", "Havna", "right", 0, 0, None),
    ],
}


def address_for(element):
    tag = element.tag
    address = {}
    if tag == "fb":
        if element.get("addr", "0") != "0":
            address["addr"] = element.get("addr")
    elif tag in ("sg", "sw"):
        for number in range(1, 5 if tag == "sg" else 3):
            addr_key = "addr" if tag == "sg" and number == 1 else f"addr{number}"
            port_key, gate_key = f"port{number}", f"gate{number}"
            if element.get(addr_key, "0") == "0" and element.get(port_key, "0") == "0":
                continue
            for key in (addr_key, port_key, gate_key):
                if element.get(key) is not None:
                    address[key] = element.get(key)
    elif tag in ("bk", "co") and (element.get("addr", "0") != "0" or element.get("port", "0") != "0"):
        address.update((key, element.get(key)) for key in ("addr", "port") if element.get(key) is not None)
    if address:
        for key in ("iid", "bus", "prot"):
            if element.get(key):
                address[key] = element.get(key)
    return address


def in_region(element, bounds):
    x, y = int(element.get("x", "0")), int(element.get("y", "0"))
    return element.get("z", "0") == "0" and bounds[0] <= x <= bounds[1] and bounds[2] <= y <= bounds[3]


def connector_matches(item, number, target, connectors):
    pair = connectors.get(number, [])
    regions = next((regions for name, _, regions in STATIONS.values() if name == target), [])
    peers = [element for element in pair if element.get("id") != item["id"]]
    return (item.get("tknr") == number and len(pair) == 2 and len(peers) == 1
            and any(in_region(peers[0], bounds) for bounds in regions))


def panel_action_turnouts(root, sensor_ids):
    sensor_ids = set(sensor_ids)
    actions = {action.get("id"): action for action in root.findall("./aclist/ac")}
    objects = {(tag, element.get("id")): element for tag in ("fb", "co", "st")
               for element in root.findall(f"./{tag}list/{tag}")}
    selector_checks = {sensor_id: set() for sensor_id in sensor_ids}
    for control in root.iter("actionctrl"):
        if control.get("id") not in actions:
            continue
        conditions = control.findall("actioncond")
        selectors = {condition.get("id") for condition in conditions if condition.get("type") == "fb"} & sensor_ids
        turnouts = {condition.get("id") for condition in conditions
                    if condition.get("type") == "sw" and condition.get("id")}
        for selector in selectors:
            selector_checks[selector].update(turnouts)

    def event_state(kind, state):
        return {"on": "true", "off": "false"}.get(state, state) if kind == "fb" else state

    results = {}
    for sensor_id in sensor_ids:
        pending = deque([("fb", sensor_id, "true"), ("fb", sensor_id, "false")])
        seen, checked, commanded = set(), set(selector_checks[sensor_id]), set()
        while pending:
            event = pending.popleft()
            if event in seen:
                continue
            seen.add(event)
            kind, object_id, state = event
            element = objects.get((kind, object_id))
            if element is None:
                continue
            if kind == "st" and state == "locked":
                commanded.update(cmd.get("id") for cmd in element.findall("swcmd")
                                 if cmd.get("type") == "sw" and cmd.get("id") and cmd.get("atfree") != "true")
            for control in element.findall("actionctrl"):
                trigger = event_state(kind, control.get("state", ""))
                action = actions.get(control.get("id"))
                if action is None or (trigger not in ("", "any") and trigger != state):
                    continue
                checked.update(condition.get("id") for condition in control.findall("actioncond")
                               if condition.get("type") == "sw" and condition.get("id"))
                target_type, target, command = action.get("type"), action.get("oid"), action.get("cmd")
                if not target:
                    continue
                if target_type == "sw" and command in ("straight", "turnout", "left", "right"):
                    commanded.add(target)
                elif target_type in ("co", "fb"):
                    states = ("on", "off") if target_type == "co" and command == "flip" else (command,)
                    for target_state in states:
                        if target_state in ("on", "off", "true", "false"):
                            pending.append((target_type, target, event_state(target_type, target_state)))
                elif target_type == "st" and command in ("lockset", "lock", "set"):
                    pending.append(("st", target, "locked"))
        results[sensor_id] = {"checked": sorted(checked), "commanded": sorted(commanded)}
    return results


def panel_input_name(sensor):
    description = (sensor.get("desc") or "").strip()
    direction = re.fullmatch(r"(ut|inn|mot)\s+([a-z](?:/[a-z])*)", description, re.IGNORECASE)
    if direction:
        action, codes = direction.groups()
        names = [PANEL_STATIONS.get(code.lower()) for code in codes.split("/")]
        if all(names):
            places = " / ".join(names)
            return {"ut": f"Til {places} Ut", "inn": f"Inn fra {places}",
                    "mot": f"Mot {places}"}[action.lower()]
    bit = re.fullmatch(r"fra\s+([a-z])\s+bit(\d+)", description, re.IGNORECASE)
    if bit and bit.group(1).lower() in PANEL_STATIONS:
        return f"Fra {PANEL_STATIONS[bit.group(1).lower()]} (bit {bit.group(2)})"
    return description[:1].upper() + description[1:] if description else sensor.get("id", "")


def dependency_objects(root):
    turnout_feedback = {turnout.get(attribute) for turnout in root.findall("./swlist/sw")
                        for attribute in ("fbG", "fbR", "fb2G", "fb2R") if turnout.get(attribute)}
    objects = {}
    for kind in ("fb", "sw", "sg", "co"):
        for element in root.findall(f"./{kind}list/{kind}"):
            object_id = element.get("id", "")
            place = PANEL_STATIONS.get(object_id[:1])
            number = re.fullmatch(r"[sgkmyinh][dvs](\d+)", object_id)
            route_output = re.fullmatch(r"([sgkmyinh])o(UT|IN)([sgkmyinhr])", object_id)
            info = {}
            if kind == "fb" and object_id in PANEL_INPUTS:
                name = panel_input_name(element)
                info = {"name": f"{place} {name} panel switch" if place else f"{name} panel switch",
                        "role": "panel"}
            elif kind == "fb" and object_id in turnout_feedback:
                info = {"name": f"Turnout feedback {object_id}", "role": "feedback"}
            elif kind == "fb" and object_id in TEST_FEEDBACK_INPUTS:
                info = {"name": f"Test input {object_id}", "role": "feedback"}
            elif place and number and kind == "fb" and object_id[1] == "d":
                info = {"name": f"{place} block {number.group(1)}", "role": "track"}
            elif place and number and kind == "sw" and object_id[1] == "v":
                info = {"name": f"{place} turnout {number.group(1)}"}
            elif place and number and kind == "sg" and object_id[1] == "s":
                info = {"name": f"{place} signal {number.group(1)}"}
            elif kind == "co" and place and re.fullmatch(r"[sgkmyinh]oP\d+", object_id):
                info = {"name": f"{place} Planovergang {object_id[3:]} output"}
            elif kind == "co" and route_output:
                direction = "exit towards" if route_output.group(2) == "UT" else "entry from"
                info = {"name": f"{place} {direction} {PANEL_STATIONS[route_output.group(3)]} selection",
                        "role": "route_selection"}
            if (kind == "co" and all(element.get(attr, "") in ("", "0") for attr in ("addr", "port"))
                    and all(not element.get(attr) for attr in ("iid", "cmd_on", "cmd_off", "publish", "subscribe"))):
                info["internal"] = True
            if info:
                objects[f"{kind}:{object_id}"] = info
    return objects


def feedback_modules(root, key):
    letter = STATIONS[key][1]
    sensors = [element for element in root.findall("./fblist/fb")
               if re.fullmatch(rf"{letter}d\d+", element.get("id", ""))
               or (key == "sigdal" and element.get("id") in TEST_FEEDBACK_INPUTS)]
    panel_turnouts = panel_action_turnouts(root, {sensor.get("id") for sensor in sensors}
                                          & PANEL_INPUTS)
    turnout_feedback = {}
    for turnout in root.findall("./swlist/sw"):
        for attribute in ("fbG", "fbR", "fb2G", "fb2R"):
            sensor_id = turnout.get(attribute)
            if sensor_id:
                turnout_feedback.setdefault(sensor_id, set()).add(turnout.get("id"))
    block_feedback = {}
    blocks = root.findall("./bklist/bk")
    block_ids = {block.get("id") for block in blocks}
    for block in blocks:
        for event in block.findall("./fbevent"):
            if event.get("id"):
                block_feedback.setdefault(event.get("id"), set()).add(block.get("id"))
    for sensor in sensors:
        if sensor.get("blockid") in block_ids:
            block_feedback.setdefault(sensor.get("id"), set()).add(sensor.get("blockid"))
    modules = []
    for name, kind, rs_address in FEEDBACK_MODULES:
        size = 16 if kind == "RS-16-O" else 8
        first = (rs_address - 1) * 8
        inputs = []
        for sensor in sensors:
            address = int(sensor.get("addr", "0"))
            if first <= address < first + size:
                sensor_id = sensor.get("id")
                types = []
                if sensor_id in PANEL_INPUTS:
                    types.append("Panel switch")
                if sensor_id in turnout_feedback:
                    types.append("Turnout feedback")
                if sensor_id in TEST_FEEDBACK_INPUTS:
                    types.append("Test input")
                if not types:
                    types.append("Track / block detector")
                inputs.append({"id": sensor_id, "address": address, "port": address - first + 1,
                               "types": types, "description": sensor.get("desc", ""),
                               "display_name": panel_input_name(sensor) if sensor_id in PANEL_INPUTS else sensor_id,
                               "turnouts": sorted(turnout_feedback.get(sensor_id, set())),
                               "blocks": sorted(block_feedback.get(sensor_id, set())),
                               "action_turnouts": panel_turnouts.get(sensor_id, {"checked": [], "commanded": []})})
        if inputs:
            modules.append({"name": name, "type": kind,
                            "rs_addresses": list(range(rs_address, rs_address + size // 8)),
                            "inputs": sorted(inputs, key=lambda item: (item["port"], item["id"]))})
    return modules


def ls100_modules(objects):
    turnouts = {item["id"]: item for item in objects if item["kind"] == "sw"}
    modules = []
    for name, rs_address, first_dcc, ports in LS100_MODULES:
        assignments = []
        for port, ids in enumerate(ports, 1):
            for turnout_id in ids.split():
                if turnout_id in turnouts:
                    assignments.append({"id": turnout_id, "port": port, "dcc_address": first_dcc + port - 1,
                                        "rocrail_address": turnouts[turnout_id]["address"]})
        if assignments:
            modules.append({"name": name, "type": "LS100", "rs_address": rs_address,
                            "turnouts": assignments})
    return modules


def signal_modules(objects):
    signals = {item["id"]: item for item in objects if item["kind"] == "sg"}
    modules = []
    for name, assignments in SIGNAL_MODULES:
        shown = [{"id": signal_id, "ports": ports, "dcc_addresses": list(range(first, last + 1)),
                  "rocrail_address": signals[signal_id]["address"]}
                 for signal_id, ports, first, last in assignments if signal_id in signals]
        if shown:
            modules.append({"name": name, "type": "OD-2", "signals": shown})
    return modules


def dependency_actions(root):
    actions = {action.get("id"): action for action in root.findall("./aclist/ac")}
    records = []
    for owner in root.iter():
        if owner.tag not in ("sw", "fb", "co", "sg", "st", "vr"):
            continue
        for control in owner.findall("actionctrl"):
            action = actions.get(control.get("id"))
            settings = {}
            for key in ("auto", "manual", "atcmd", "atevt"):
                if control.get(key) == "false":
                    settings[key] = "false"
            for key in ("lcid", "identifier", "substate", "timer", "duration"):
                if control.get(key) not in (None, "", "0", "00"):
                    settings[key] = control.get(key)
            if action is not None:
                for key in ("timed", "random", "timer", "actiontime", "param"):
                    if action.get(key) not in (None, "", "0", "00", "false"):
                        settings[f"action.{key}"] = action.get(key)
            records.append({
                "id": control.get("id", ""),
                "kind": "action",
                "trigger": {"type": owner.tag, "id": owner.get("id", ""),
                            "state": control.get("state") or "any"},
                "result": {"type": action.get("type", ""), "id": action.get("oid", ""),
                           "command": action.get("cmd", "")} if action is not None else None,
                "all_conditions": control.get("allconditions", "true") == "true",
                "conditions": [condition.attrib.copy() for condition in control.findall("actioncond")],
                "settings": settings,
            })
    for route in root.findall("./stlist/st"):
        for command in route.findall("swcmd"):
            settings = {key: command.get(key) for key in ("atfree", "lock", "protect")
                        if command.get(key) is not None}
            for key in ("bka", "bkb"):
                if route.get(key):
                    settings[f"route.{key}"] = route.get(key)
            records.append({
                "id": f'{route.get("id", "")} / {command.get("id", "")}',
                "kind": "route_command",
                "trigger": {"type": "st", "id": route.get("id", ""), "state": "route command"},
                "result": {"type": command.get("type", ""), "id": command.get("id", ""),
                           "command": command.get("cmd", "")},
                "all_conditions": True, "conditions": [], "settings": settings,
            })
    return records


def block_detectors(root):
    blocks = {}
    for block in root.findall("./bklist/bk"):
        blocks[block.get("id")] = {event.get("id") for event in block.findall("fbevent") if event.get("id")}
    for sensor in root.findall("./fblist/fb"):
        if sensor.get("blockid") in blocks:
            blocks[sensor.get("blockid")].add(sensor.get("id"))
    return {block: sorted(sensors) for block, sensors in blocks.items() if sensors}


def drawing_locations(plans):
    locations = {}
    for key, plan in plans.items():
        objects = {(item["kind"], item["id"]) for item in plan["objects"]
                   if item["kind"] in ("sw", "sg", "fb", "bk", "co")}
        objects.update(("fb", item["id"]) for module in plan.get("feedback_modules", [])
                       for item in module["inputs"] if "Panel switch" in item["types"])
        for kind, object_id in sorted(objects):
            anchor = f"#control-{kind}-{object_id}" if key == "control" else ""
            locations.setdefault(kind, {}).setdefault(object_id, []).append(
                {"name": plan["station"], "file": f"{key}.html{anchor}"})
    return locations


def check_address_findings(root, entries, plans):
    results = []
    for entry in entries:
        kind, object_id = entry["kind"], entry["id"]
        element = next((node for node in root.findall(f"./{kind}list/{kind}")
                        if node.get("id") == object_id), None)
        actual = ({field: element.get(field) for field in entry["attributes"]
                   if element.get(field, "0") not in ("0", "")} if element is not None else None)
        decoder = ({field: element.get(field) for field in entry.get("decoder_attributes", [])
                    if element.get(field, "0") not in ("0", "")} if element is not None else {})
        valid = actual is not None and not decoder and all(value.isdecimal() for value in actual.values())
        status = ("unverified" if not valid else
                  "match" if {int(value) for value in actual.values()} == set(entry["expected"]) else "mismatch")
        locations = []
        finding = {**entry, "actual": actual, "decoder": decoder, "status": status}
        for key, plan in plans.items():
            for item_kind, item in finding_objects(plan):
                if item_kind != kind or item["id"] != object_id:
                    continue
                item.setdefault("findings", []).append(finding)
                anchor = f"control-{kind}-{object_id}" if key == "control" else f"finding-{kind}-{object_id}"
                locations.append({"name": plan["station"], "file": f"{key}.html#{anchor}"})
        results.append({**finding, "locations": locations})
    return results


def finding_objects(plan):
    yield from ((item["kind"], item) for item in plan["objects"])
    yield from (("fb", item) for module in plan.get("feedback_modules", []) for item in module["inputs"]
                if "Panel switch" in item["types"])


def finding_text(finding):
    actual = ("not found" if finding["actual"] is None else
              ", ".join(f"{key}={value}" for key, value in finding["actual"].items()) or "not configured")
    if finding.get("decoder"):
        actual += ", " + ", ".join(f"{key}={value}" for key, value in finding["decoder"].items())
    expected = ", ".join(map(str, finding["expected"]))
    return f'XML: {actual}; documented addresses: {expected}.'


def fixit_anchor(finding):
    return f'fix-{finding["kind"]}-{finding["id"]}'


def fixit_link(finding):
    return f'fixit.html#{quote(fixit_anchor(finding), safe="")}'


def finding_marker():
    return ('<g class="finding-marker" aria-hidden="true">'
            '<rect x="3" y="3" width="50" height="50" rx="3"/>'
            '<path class="finding-triangle" d="M 46 34 L 56 53 H 36 Z"/>'
            '<path class="finding-exclamation" d="M 46 40 V 46 M 46 49 V 50"/>'
            '</g>')


def extract_control_level(root, xml_path):
    level = next((level for level in root.findall("./zlevel")
                  if level.get("title", "").casefold() == "control"), None)
    if level is None:
        return None
    objects = []
    for kind in ("sg", "bk", "fb", "co"):
        for element in root.findall(f"./{kind}list/{kind}"):
            if element.get("z", "0") != level.get("z"):
                continue
            item = {"kind": kind, "id": element.get("id"),
                    **{axis: int(element.get(axis, "0")) for axis in ("x", "y", "z")}}
            for attr in ("type", "ori", "blockid", "desc"):
                if element.get(attr):
                    item[attr] = element.get(attr)
            if kind != "co":
                item["address"] = address_for(element)
            objects.append(item)
    return {"station": "Control level", "source_xml": xml_path.name, "objects": objects}


def extract_plan(root, xml_path, report_text, key):
    name, letter, regions = STATIONS[key]
    objects = []
    for tag in ("tk", "sw", "sg", "fb", "bk", "co"):
        for element in root.findall(f"./{tag}list/{tag}"):
            if not any(in_region(element, bounds) for bounds in regions):
                continue
            if tag == "fb" and element.get("id") in PANEL_INPUTS:
                continue
            if tag == "co" and (element.get("svgtype") not in TRACK_OUTPUT_TYPES or element.get("show") == "false"):
                continue
            item = {"kind": tag, "id": element.get("id"),
                    **{axis: int(element.get(axis, "0")) for axis in ("x", "y", "z")}}
            for attr in ("type", "ori", "state", "blockid", "signal", "dwarf", "smallsymbol", "desc", "tknr", "svgtype"):
                if element.get(attr):
                    item[attr] = element.get(attr)
            if tag in ("sg", "sw", "fb", "bk", "co"):
                item["address"] = address_for(element)
            objects.append(item)
    heading = f"## {name} ({letter})"
    section = report_text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in report_text else ""
    known = {element.get("id") for tag in ("sg", "sw") for element in root.findall(f"./{tag}list/{tag}")}
    references = sorted(set(re.findall(r"\b(?:[a-z]s\d+|[a-z]v\d+|[a-z]x\d*)\b", section)) & known)
    found = {item["id"] for item in objects}
    for item in objects:
        if item["kind"] in ("sg", "sw"):
            item["referenced"] = item["id"] in references
    by_id = {item["id"]: item for item in objects}
    connectors = {}
    for element in root.findall("./tklist/tk"):
        if element.get("type") == "connector" and element.get("z", "0") == "0":
            connectors.setdefault(element.get("tknr"), []).append(element)
    destinations = []
    unresolved = []
    for anchor, target, side, dx, dy, number in DESTINATIONS[key]:
        item = by_id.get(anchor)
        if not item or (number and not connector_matches(item, number, target, connectors)):
            unresolved.append(f"{target} ({anchor})")
            continue
        destinations.append({"anchor": anchor, "name": target, "side": side,
                             "x": item["x"], "y": item["y"], "dx": dx, "dy": dy,
                             "basis": f"paired connector {number}" if number else "adjacent layout / station label"})
    ls100 = ls100_modules(objects)
    signals = signal_modules(objects)
    mapped_turnouts = {item["id"] for module in ls100 for item in module["turnouts"]}
    mapped_signals = {item["id"] for module in signals for item in module["signals"]}
    return {
        "station": name,
        "source_xml": xml_path.name,
        "source_report": "signal_logic.md",
        "description": "Rocrail schematic grid, not a physical or live track plan.",
        "bounds": dict(zip(("min_x", "max_x", "min_y", "max_y"), regions[0])),
        "regions": [dict(zip(("min_x", "max_x", "min_y", "max_y"), region)) for region in regions],
        "report_references": references,
        "references_outside_drawing": sorted(set(references) - found),
        "destinations": destinations,
        "unresolved_destinations": unresolved,
        "feedback_modules": feedback_modules(root, key),
        "ls100_modules": ls100,
        "signal_modules": signals,
        "signal_unmapped": sorted(item["id"] for item in objects
                                  if item["kind"] == "sg" and item["id"] not in mapped_signals),
        "ls100_unmapped_turnouts": sorted(item["id"] for item in objects
                                          if item["kind"] == "sw" and item["id"] not in mapped_turnouts),
        "objects": objects,
    }


def rotated_path(path, orientation, part="main"):
    angle = {"west": 0, "north": 270, "east": 180, "south": 90}.get(orientation, 0)
    return f'<path data-part="{part}" d="{path}" transform="rotate({angle} 16 16)"/>'


def track_shape(item):
    kind, typ = item["kind"], item.get("type", "")
    orientation = item.get("ori", "west")
    if kind == "tk" and typ == "curve":
        return rotated_path("M 0 16 L 16 32", orientation)
    if kind == "tk" and typ == "buffer":
        return rotated_path("M 0 16 H 26 M 26 9 V 23", orientation)
    if kind == "sw":
        if typ == "crossing":
            return '<path data-part="main" d="M 0 16 H 32"/><path data-part="cross" d="M 16 0 V 32"/>'
        if typ == "dcrossing":
            return ('<path data-part="main" d="M 0 16 H 32"/>'
                    '<path data-part="cross" d="M 16 0 V 32"/>'
                    '<path data-part="slip" d="M 0 16 Q 16 16 16 0 M 16 32 Q 16 16 32 16"/>')
        if typ in ("left", "right"):
            branch = "M 32 16 L 16 32" if typ == "left" else "M 0 16 L 16 32"
            straight = "M 16 0 V 32" if orientation in ("north", "south") else "M 0 16 H 32"
            return f'<path data-part="main" d="{straight}"/>' + rotated_path(branch, orientation, "branch")
    if kind == "bk":
        midpoint = 64 if item.get("smallsymbol") == "false" else 32
        end = midpoint * 2
        if orientation in ("north", "south"):
            return (f'<path data-part="left" d="M 16 0 V {midpoint}"/>'
                    f'<path data-part="right" d="M 16 {midpoint} V {end}"/>')
        return (f'<path data-part="left" d="M 0 16 H {midpoint}"/>'
                f'<path data-part="right" d="M {midpoint} 16 H {end}"/>')
    if orientation in ("north", "south"):
        return '<path data-part="main" d="M 16 0 V 32"/>'
    return '<path data-part="main" d="M 0 16 H 32"/>'


def object_title(item):
    parts = [f"{'XML state' if key == 'state' else key}: {value}"
             for key, value in item.items() if key not in ("address", "findings")]
    if "address" in item:
        address = item["address"]
        details = ", ".join(f"{key}={value}" for key, value in address.items()) if address else "not configured"
        parts.append(f"Rocrail address: {details}")
    parts.extend(f"WARNING: {finding_text(finding)}" for finding in item.get("findings", [])
                 if finding["status"] != "match")
    if item.get("kind") == "sg":
        parts.append("XML symbol orientation only; signal facing and train direction are not verified")
    return " · ".join(parts)


def signal_orientation(item, x, y):
    arrow = {"west": "←", "east": "→", "north": "↑", "south": "↓"}.get(item.get("ori"))
    return f'<text class="signal-orientation" x="{x}" y="{y}">{arrow}</text>' if arrow else ""


def render_object(item, bounds, interactive=False):
    x = (item["x"] - bounds["min_x"]) * CELL
    y = (item["y"] - bounds["min_y"]) * CELL
    kind = item["kind"]
    findings = item.get("findings", [])
    anchor = (f' id="finding-{html.escape(kind, quote=True)}-{html.escape(item["id"], quote=True)}"'
              if findings else "")
    controls = ' class="turnout" role="button" tabindex="0"' if (
        interactive and kind == "sw" and item.get("type") in ("left", "right")) else ""
    if kind == "fb":
        controls = (f' class="feedback-detector" role="button" tabindex="0" aria-pressed="false"'
                    f' aria-label="Locate {html.escape(item["id"], quote=True)}"')
    parts = [f'<g{anchor} data-id="{html.escape(item["id"], quote=True)}" data-kind="{kind}"{controls} transform="translate({x} {y})"><title>{html.escape(object_title(item))}</title>',
             f'<g class="track" transform="scale({CELL / 32})">{track_shape(item)}</g>']
    if kind in ("sg", "sw", "bk", "fb", "co"):
        name = html.escape(item["id"])
        if kind == "bk":
            center = 112 if item.get("smallsymbol") == "false" else 56
            x_label, y_label = (45, center) if item.get("ori") in ("north", "south") else (center, 23)
        cx, cy = (x_label, y_label) if kind == "bk" else (28, 36 if kind in ("sw", "fb", "co") else 28)
        parts.append(f'<circle class="feedback-ring" cx="{cx}" cy="{cy}" r="18"/>')
        if kind == "sg":
            parts.append('<circle class="signal" cx="28" cy="28" r="5"/>')
            parts.append(f'<text class="signal-label" x="28" y="15">{name}</text>')
            parts.append(signal_orientation(item, 10, 43))
        elif kind == "sw":
            parts.append(f'<text class="turnout-label" x="28" y="48">{name}</text>')
        elif kind == "bk":
            parts.append(f'<text class="block-label" x="{x_label}" y="{y_label}">{name}</text>')
        elif kind == "fb":
            parts.append(f'<circle class="sensor" cx="28" cy="28" r="3"/><text class="sensor-label" x="28" y="48">{name}</text>')
        else:
            parts.append(f'<rect class="output" x="24" y="24" width="8" height="8"/>'
                         f'<text class="output-label" x="28" y="48">{name}</text>')
    if any(finding["status"] != "match" for finding in findings):
        parts.append(finding_marker())
    parts.append("</g>")
    return "".join(parts)


STYLE = """
body { margin: 0; background: #f3f5f7; color: #17212b; font: 16px system-ui, sans-serif; }
main { max-width: 1500px; margin: auto; padding: 1.5rem; }
h1 { margin: 0 0 .4rem; } p { line-height: 1.45; }
.legend { display: flex; flex-wrap: wrap; gap: 1rem; font-size: .9rem; }
.canvas { overflow: auto; background: white; border: 1px solid #cbd5df; border-radius: 8px; margin: 1rem 0; }
svg { display: block; }
.track { fill: none; stroke: #34495e; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
text { text-anchor: middle; font: bold 12px system-ui, sans-serif; paint-order: stroke; stroke: white; stroke-width: 3px; stroke-linejoin: round; }
.signal { fill: #394eaf; stroke: white; stroke-width: 2; }
.signal-orientation { fill: #293d9e; font-size: 15px; }
.signal-label { fill: #293d9e; } .turnout-label { fill: #a44c12; }
.block-label { fill: #16634c; } .sensor-label { fill: #657280; font-size: 10px; }
.output { fill: #7a4d95; stroke: white; stroke-width: 1; }
.output-label { fill: #7a4d95; font-size: 10px; }
.finding-marker { pointer-events: none; }
.finding-marker rect { fill: none; stroke: #c4161c; stroke-width: 3; }
.finding-triangle { fill: #c4161c; stroke: white; stroke-width: 1; }
.finding-exclamation { fill: none; stroke: white; stroke-width: 2; stroke-linecap: round; }
.finding-summary { color: #a00000; font-weight: bold; }
.sensor { fill: #657280; stroke: white; stroke-width: 1; }
.destination { fill: #273f54; font: bold 14px system-ui, sans-serif; }
.module-groups { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 12px 0; }
.module-group-button { cursor: pointer; background: white; border: 1px solid #8797a6;
                       border-radius: 4px; padding: 5px 8px; font: inherit; }
.module-group-button[aria-expanded="true"] { background: #e3edff; border-color: #185abc; }
.module-note { margin: 8px 12px; font-size: 13px; }
.feedback-modules { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 12px 0; }
.feedback-module { border: 1px solid #8797a6; border-radius: 4px; padding: 5px 8px;
                   font-size: 13px; line-height: 1.4; width: max-content; position: relative; }
.feedback-module:hover, .feedback-module:focus-within { z-index: 2; }
.feedback-module:focus-visible { outline: 2px solid #185abc; }
.feedback-tooltip { display: none; position: absolute; top: 100%; left: 0; background: white;
                    border: 1px solid #8797a6; box-shadow: 0 3px 8px #0003; padding: 8px;
                    width: max-content; max-width: min(600px, calc(100vw - 3rem));
                    box-sizing: border-box; overflow-x: auto; }
.feedback-module:hover .feedback-tooltip, .feedback-module:focus-within .feedback-tooltip { display: block; }
.feedback-module.tooltip-dismissed .feedback-tooltip { display: none; }
.feedback-tooltip table { border-collapse: collapse; text-align: left; }
.feedback-tooltip th, .feedback-tooltip td { border-bottom: 1px solid #dce2e8; padding: 3px 6px; white-space: nowrap; }
.feedback-tooltip caption { text-align: left; font-weight: bold; }
.feedback-detector { cursor: pointer; }
.feedback-detector:focus { outline: 2px solid #185abc; }
.feedback-ring { display: none; fill: none; stroke: #0059e8; stroke-width: 4; pointer-events: none; }
.feedback-highlight .feedback-ring { display: block; }
.feedback-module { cursor: pointer; }
.feedback-panel-highlight { outline: 3px solid #0059e8; outline-offset: 2px; }
.feedback-selection-status:not(:empty) { margin: 8px 12px; }
.station-panel { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 10px 12px 0; font-size: 13px; }
.panel-marker { border: 1px solid #8797a6; border-radius: 4px; padding: 3px 6px; background: white; font: inherit; cursor: pointer; }
.panel-marker.has-finding { border: 3px solid #c4161c; }
.dependency-toolbar { margin: 1rem 0; }
.dependency-toolbar > button { cursor: pointer; background: white; border: 1px solid #8797a6;
                               border-radius: 4px; padding: 5px 8px; font: inherit; }
.dependency-toolbar > button[aria-pressed="true"] { background: #e3edff; border-color: #185abc; }
.dependency-inspector { background: white; border: 1px solid #8797a6; border-radius: 6px; padding: 8px;
                        margin-top: 8px; font-size: 13px; overflow-wrap: anywhere; }
.dependency-inspector p { margin: .25rem 0; line-height: 1.3; }
.dependency-select-label { display: grid; gap: .35rem; margin-top: .75rem; font-weight: bold; }
.dependency-select-label select { width: 100%; max-width: 100%; font: inherit; font-weight: normal;
                                 padding: .35rem; box-sizing: border-box; }
.dependency-action-details { margin-top: .75rem; padding: .75rem; border-left: 4px solid #185abc;
                             border-radius: 4px; background: #f0f5fc; }
.dependency-action-details h3 { margin: 0 0 .4rem; font-size: 13px; color: #233d60; }
.dependency-inspector .dependency-note { color: #445568; margin: .35rem 0 .6rem; }
.dependency-inspector .dependency-explanation { background: white; border: 1px solid #ccd9e9;
  border-radius: 4px; padding: .5rem .65rem; margin: .4rem 0; font-size: 14px; line-height: 1.4; }
.dependency-state-context { border-top: 1px solid #ccd9e9; margin-top: .5rem; padding-top: .5rem;
                            font-size: 13px; color: #445568; }
.dependency-action-details summary { cursor: pointer; margin-top: .4rem; font-weight: bold; }
.dependency-link { background: none; border: 0; color: #174eab; padding: 0; font: inherit; text-decoration: underline; cursor: pointer; }
.dependency-breadcrumbs { display: flex; flex-wrap: wrap; gap: .4rem; }
.dependency-inspector ul { margin: .2rem 0 .5rem; }
.dependency-inspector pre { white-space: pre-wrap; overflow-wrap: anywhere; }
body.dependency-mode g[data-kind="sw"], body.dependency-mode g[data-kind="sg"],
body.dependency-mode g[data-kind="fb"], body.dependency-mode g[data-kind="bk"],
body.dependency-mode g[data-kind="co"] { cursor: pointer; }
body.dependency-mode .feedback-highlight .feedback-ring { display: none; }
body.dependency-mode .feedback-panel-highlight { outline: none; }
body.dependency-mode .dependency-reference .feedback-ring { display: block; stroke: #8d32b4; }
body.dependency-mode .dependency-selected .feedback-ring { display: block; stroke: #d54b00; }
body.dependency-mode .panel-marker.dependency-reference { outline: 3px solid #8d32b4; outline-offset: 2px; }
body.dependency-mode .panel-marker.dependency-selected { outline: 3px solid #d54b00; outline-offset: 2px; }
"""


def render_panel_inputs(plan):
    inputs = [item for module in plan["feedback_modules"] for item in module["inputs"]
              if "Panel switch" in item["types"]]
    if not inputs:
        return ""
    markers = []
    for item in inputs:
        findings = item.get("findings", [])
        active = [finding for finding in findings if finding["status"] != "match"]
        anchor = f' id="finding-fb-{html.escape(item["id"], quote=True)}"' if findings else ""
        warning = " has-finding" if active else ""
        title = f'Rocrail: {item["id"]} · XML: {item["description"]}'
        if active:
            title += " · WARNING: " + " ".join(finding_text(finding) for finding in active)
        label = f'{item["display_name"]} (Rocrail: {item["id"]})'
        if active:
            label += " — address finding"
        markers.append(
            f'<button type="button"{anchor} class="panel-marker{warning}" '
            f'data-panel-select="{html.escape(item["id"], quote=True)}" '
            f'data-feedback-ids="{html.escape(item["id"], quote=True)}" '
            f'data-display-name="{html.escape(item["display_name"], quote=True)}" '
            f'title="{html.escape(title, quote=True)}" aria-label="{html.escape(label, quote=True)}">'
            f'{"⚠ " if active else ""}{html.escape(item["display_name"])}</button>')
    return f'<div class="station-panel" aria-label="Station panel switches"><strong>Panel switches:</strong>{"".join(markers)}</div>'


def format_addresses(addresses):
    groups = []
    for _, values in groupby(enumerate(sorted(set(addresses))), lambda item: item[1] - item[0]):
        group = [value for _, value in values]
        groups.append(str(group[0]) if len(group) == 1 else f"{group[0]}–{group[-1]}")
    return ", ".join(groups)


def render_feedback_modules(plan):
    cards = []
    for index, module in enumerate(plan["feedback_modules"]):
        addresses = "–".join(str(address) for address in module["rs_addresses"])
        inputs = module["inputs"]
        count = len({item["port"] for item in inputs})
        types = sorted({kind for item in inputs for kind in item["types"]})
        rows = []
        for item in inputs:
            description = item["description"]
            if item["turnouts"]:
                description = " · ".join(filter(None, (description, "Turnouts: " + ", ".join(item["turnouts"]))))
            name = html.escape(item["display_name"])
            title = html.escape(item["id"], quote=True)
            cells = (item["address"], ", ".join(item["types"]), description or "—")
            rows.append(f'<tr><td>{item["port"]}</td><td title="Rocrail: {title}">{name}</td>' +
                        "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>")
        tooltip_id = f"feedback-tooltip-{index}"
        module_inputs = [{"id": item["id"], "related": item["blocks"] + item["turnouts"],
                          "action_turnouts": item["action_turnouts"], "turnout_feedback": item["turnouts"]}
                         for item in inputs]
        data = html.escape(json.dumps(module_inputs, ensure_ascii=False), quote=True)
        cards.append(f'<div class="feedback-module" role="button" tabindex="0" aria-pressed="false" '
                     f'data-module-name="{html.escape(module["name"], quote=True)}" data-module-inputs="{data}" '
                     f'aria-describedby="{tooltip_id}">'
                     f'<strong>{html.escape(module["type"])} {html.escape(module["name"])}</strong><br>'
                     f'RS {addresses} · {count} configured input{"s" if count != 1 else ""}<br>'
                     f'{html.escape(", ".join(types))}'
                     f'<div class="feedback-tooltip" id="{tooltip_id}" role="region" aria-label="Feedback inputs"><table>'
                     f'<caption>{html.escape(module["name"])} inputs for {html.escape(plan["station"])}</caption>'
                     '<thead><tr><th>Input</th><th>Name / ID</th><th>Address</th><th>Type</th><th>Details</th></tr></thead>'
                     f'<tbody>{"".join(rows)}</tbody></table></div></div>')
    rs_cards, cards = cards, []
    for index, module in enumerate(plan["ls100_modules"]):
        turnouts = module["turnouts"]
        rows = []
        for item in turnouts:
            address = item["rocrail_address"]
            xml_address = ", ".join(f"{key}={value}" for key, value in address.items()) or "not configured"
            cells = (item["port"], item["id"], item["dcc_address"], xml_address)
            rows.append("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>")
        module_inputs = [{"id": item["id"], "related": [], "turnout_feedback": [],
                          "action_turnouts": {"checked": [], "commanded": []}} for item in turnouts]
        data = html.escape(json.dumps(module_inputs, ensure_ascii=False), quote=True)
        name = f'LS100 {module["name"]}'
        tooltip_id = f"ls100-tooltip-{index}"
        count = len(turnouts)
        cards.append(f'<div class="feedback-module" role="button" tabindex="0" aria-pressed="false" '
                     f'data-module-name="{html.escape(name, quote=True)}" data-module-inputs="{data}" '
                     f'aria-describedby="{tooltip_id}">'
                     f'<strong>{html.escape(name)}</strong><br>RS {module["rs_address"]} · '
                     f'{count} shown turnout{"s" if count != 1 else ""}<br>Turnouts'
                     f'<div class="feedback-tooltip" id="{tooltip_id}" role="region" aria-label="LS100 turnouts"><table>'
                     f'<caption>{html.escape(name)}: PDF assignments for {html.escape(plan["station"])}</caption>'
                     '<thead><tr><th>Port</th><th>Turnout</th><th>DCC (PDF)</th><th>Rocrail address (XML)</th></tr></thead>'
                     f'<tbody>{"".join(rows)}</tbody></table></div></div>')
    ls_cards, cards = cards, []
    unmapped = plan["ls100_unmapped_turnouts"]
    note = (f'<p class="module-note">No documented LS100 assignment: {html.escape(", ".join(unmapped))}.</p>'
            if unmapped else "")
    for index, module in enumerate(plan["signal_modules"]):
        signals = module["signals"]
        rows = []
        for item in signals:
            address = item["rocrail_address"]
            xml_address = ", ".join(f"{key}={value}" for key, value in address.items()) or "not configured"
            cells = (item["id"], item["ports"], ", ".join(map(str, item["dcc_addresses"])), xml_address)
            rows.append("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>")
        module_inputs = [{"id": item["id"], "related": [], "turnout_feedback": [],
                          "action_turnouts": {"checked": [], "commanded": []}} for item in signals]
        data = html.escape(json.dumps(module_inputs, ensure_ascii=False), quote=True)
        name = f'OD-2 {module["name"]}'
        tooltip_id = f"signal-tooltip-{index}"
        count = len(signals)
        addresses = format_addresses(address for item in signals for address in item["dcc_addresses"])
        cards.append(f'<div class="feedback-module" role="button" tabindex="0" aria-pressed="false" '
                     f'data-module-name="{html.escape(name, quote=True)}" data-module-inputs="{data}" '
                     f'aria-describedby="{tooltip_id}">'
                     f'<strong>{html.escape(name)}</strong><br>DCC {html.escape(addresses)}<br>'
                     f'{count} shown signal{"s" if count != 1 else ""}<br>Signals'
                     f'<div class="feedback-tooltip" id="{tooltip_id}" role="region" aria-label="OD-2 signals"><table>'
                     f'<caption>{html.escape(name)}: PDF assignments for {html.escape(plan["station"])}</caption>'
                     '<thead><tr><th>Signal</th><th>Ports (PDF)</th><th>DCC (PDF)</th><th>Rocrail address (XML)</th></tr></thead>'
                     f'<tbody>{"".join(rows)}</tbody></table></div></div>')
    signal_note = (f'<p class="module-note">No documented OD-2 assignment: '
                   f'{html.escape(", ".join(plan["signal_unmapped"]))}.</p>'
                   if plan["signal_unmapped"] else "")
    categories = [("rs", "RS feedback", rs_cards, ""),
                  ("ls", "LS100 turnouts", ls_cards, note),
                  ("dcc", "DCC signal decoders", cards, signal_note)]
    buttons = "".join(
        f'<button type="button" class="module-group-button" aria-expanded="false" aria-controls="modules-{key}">'
        f'{label} ({len(items)})</button>' for key, label, items, _ in categories)
    sections = "".join(
        f'<div id="modules-{key}" hidden><div class="feedback-modules" '
        f'aria-label="{("Feedback modules for this station" if key == "rs" else label)}">'
        f'{"".join(items) if items else "No modules shown for this drawing."}</div>{extra}</div>'
        for key, label, items, extra in categories)
    return (f'<div class="module-groups" aria-label="Module types">{buttons}</div>{sections}'
            '<div class="feedback-selection-status" role="status" aria-live="polite"></div>')


def render_destination(destination, bounds):
    x = destination["x"] - bounds["min_x"] + destination["dx"]
    y = destination["y"] - bounds["min_y"] + destination["dy"]
    side = destination["side"]
    if side == "left":
        px, py, anchor, arrow = x * CELL - 10, (y + 0.5) * CELL + 5, "end", "← "
    elif side == "above-left":
        px, py, anchor, arrow = (x + 0.5) * CELL, y * CELL - 10, "middle", "← "
    elif side == "right":
        px, py, anchor, arrow = (x + 1) * CELL + 10, (y + 0.5) * CELL + 5, "start", ""
    elif side == "top":
        px, py, anchor, arrow = (x + 0.5) * CELL, y * CELL - 10, "middle", "↑ "
    else:
        px, py, anchor, arrow = (x + 0.5) * CELL, (y + 1) * CELL + 20, "middle", "↓ "
    label = arrow + destination["name"] + (" →" if side == "right" else "")
    return (f'<text class="destination" x="{px}" y="{py}" style="text-anchor:{anchor}">'
            f'<title>{html.escape(destination["basis"])}</title>{html.escape(label)}</text>')


def render_svg(plan, bounds, interactive=False, show_modules=True):
    margin_x, margin_y = 190, 32
    width = (bounds["max_x"] - bounds["min_x"] + 1) * CELL + 2 * margin_x
    height = (bounds["max_y"] - bounds["min_y"] + 1) * CELL + 2 * margin_y
    region = (bounds["min_x"], bounds["max_x"], bounds["min_y"], bounds["max_y"])
    objects = (item for item in plan["objects"] if region[0] <= item["x"] <= region[1]
               and region[2] <= item["y"] <= region[3])
    drawing = "\n".join(render_object(item, bounds, interactive) for item in objects)
    labels = "\n".join(render_destination(item, bounds) for item in plan["destinations"]
                       if region[0] <= item["x"] <= region[1] and region[2] <= item["y"] <= region[3])
    role = "group"
    modules = render_feedback_modules(plan) if show_modules else ""
    panels = render_panel_inputs(plan) if show_modules and not interactive else ""
    return (f'<div class="canvas">{modules}{panels}<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="{role}" aria-label="{html.escape(plan["station"])} station schematic">'
            f'<g transform="translate({margin_x} {margin_y})">{drawing}{labels}</g></svg></div>')


def dependency_data(plan):
    return json.dumps({"actions": plan["dependency_actions"], "block_detectors": plan["block_detectors"],
                       "drawing_locations": plan["drawing_locations"], "objects": plan["dependency_objects"]},
                      ensure_ascii=False).replace("<", "\\u003c")


def finding_summary(plan, control=False):
    items = [(kind, item) for kind, item in finding_objects(plan)
             if any(finding["status"] != "match" for finding in item.get("findings", []))]
    if not items:
        return ""
    links = []
    for kind, item in items:
        prefix = "control" if control else "finding"
        anchor = html.escape(f'{prefix}-{kind}-{item["id"]}', quote=True)
        links.append(f'<a href="#{anchor}">{html.escape(item["id"])}</a>')
    return (f'<p class="finding-summary">⚠ {len(items)} object(s) with address findings: '
            f'{", ".join(links)}. <a href="errors.html">View findings</a>.</p>')


def render_findings_html(findings, analysis, xml_path):
    sections = []
    for finding in findings:
        status = {"mismatch": "Mismatch", "match": "Matches documented value",
                  "unverified": "Cannot verify: missing object, invalid address or changed addressing mode"}[finding["status"]]
        links = [f'<a href="{html.escape(place["file"], quote=True)}">{html.escape(place["name"])}</a>'
                 for place in finding["locations"]]
        location = ", ".join(links) if links else "Not shown in a drawing."
        sections.append(
            f'<section><h2>{html.escape(finding["id"])} ({html.escape(finding["kind"])})</h2>'
            f'<p><strong>{status}</strong> — {html.escape(finding["category"])} address.</p>'
            f'<p>{html.escape(finding_text(finding))}</p>'
            f'<p>Drawing: {location} · <a href="{html.escape(fixit_link(finding), quote=True)}">FixIt guidance</a></p></section>')
    stale = (f'<p class="finding-summary">⚠ XML has changed since the analysis of '
             f'{html.escape(analysis["source_xml"])}. Rerun the PDF analysis to discover new findings.</p>'
             if analysis["source_xml_sha256"] != hashlib.sha256(xml_path.read_bytes()).hexdigest() else "")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Address findings</title><style>{STYLE}</style></head>
<body><main><p><a href="index.html">All station drawings</a> · <a href="fixit.html">FixIt guide</a></p><h1>Address findings</h1>
<p>Compared with XML <strong>{html.escape(xml_path.name)}</strong>. Source: {html.escape(analysis["source_pdf"])}.</p>{stale}
<p>A red box and warning triangle identify a mismatch or an unverified value, not a confirmed physical crash.
These are comparisons with the documented addresses, not a live check of decoder settings. Verify the hardware
and current specification before changing the layout. Only recorded address mismatches are rechecked here; rerun
the analysis to discover new ones. Virtual-interface switches, nonzero decoder-address modes and PDF entries
without matching XML objects are excluded.</p>
<p>Address collisions and other analysis findings are not included in this overview.</p>
{"".join(sections) if sections else "<p>No findings configured.</p>"}</main></body></html>
"""


def render_fixit_html(findings, analysis, xml_path, root):
    stale = analysis["source_xml_sha256"] != hashlib.sha256(xml_path.read_bytes()).hexdigest()
    sections = []
    for finding in findings:
        object_id = finding["id"]
        kind = finding["kind"]
        anchor = html.escape(fixit_anchor(finding), quote=True)
        name = html.escape(object_id)
        locations = ", ".join(
            f'<a href="{html.escape(place["file"], quote=True)}">{html.escape(place["name"])}</a>'
            for place in finding["locations"]) or "Not shown in a drawing."
        status = finding["status"]
        if stale:
            advice = "<p>The analysis is out of date. Rerun it before deciding on a change.</p>"
        elif status == "match":
            advice = "<p>The current XML matches the recorded PDF addresses; no change is needed for this finding.</p>"
        elif status == "unverified":
            advice = "<p>The object, address or addressing mode could not be verified.</p>"
        elif kind == "sg" and object_id == "is03" and finding["actual"] == {"port1": "1005", "port2": "1005"} and finding["expected"] == [1005, 1006]:
            advice = ("<p><strong>Rocrail steps:</strong></p><ol>"
                      "<li>Open <strong>Tables → Signals</strong> and select <strong>is03</strong>.</li>"
                      "<li>Open the <strong>Interface</strong> tab.</li>"
                      "<li>Change the second <strong>Port</strong> field (<code>port2</code>) from "
                      "<strong>1005</strong> to <strong>1006</strong>. It may be under Yellow or Green, depending "
                      "on the Rocrail version. Leave the first Port at 1005.</li>"
                      "<li>Click <strong>OK</strong>, then <strong>File → Save</strong>.</li></ol>")
        elif kind == "co" and object_id in ("moP1", "yoP1") and set(finding["actual"]) == {"port"} and len(finding["expected"]) == 1:
            target = html.escape(str(finding["expected"][0]))
            current = html.escape(finding["actual"]["port"])
            advice = (f"<p><strong>Rocrail steps:</strong></p><ol>"
                      f"<li>Open <strong>Tables → Outputs</strong> and select <strong>{name}</strong>.</li>"
                      f"<li>Open the <strong>Interface</strong> tab.</li>"
                      f"<li>Change <strong>Port</strong> from <strong>{current}</strong> to <strong>{target}</strong>.</li>"
                      "<li>Click <strong>OK</strong>, then <strong>File → Save</strong>.</li></ol>")
        else:
            advice = "<p>No specific Rocrail field change is available for this finding.</p>"
        sections.append(
            f'<section id="{anchor}"><h2>{name} ({html.escape(kind)})</h2>'
            f'<p><strong>{html.escape(status.capitalize())}</strong> — {html.escape(finding_text(finding))}</p>'
            f'<p>Drawing: {locations}</p>{advice}</section>')
    notice = ('<p class="finding-summary">⚠ The XML has changed since the PDF analysis. Rerun the analysis before following finding-specific advice.</p>'
              if stale else "")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FixIt — address findings</title><style>{STYLE}
main {{ max-width: 1000px; }} section {{ background: white; border: 1px solid #cbd5df; border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
section h2 {{ margin-top: 0; }} li {{ margin: .45rem 0; }}</style></head>
<body><main><p><a href="index.html">All station drawings</a> · <a href="errors.html">Address findings</a> · <a href="bruksanvisning.html">Bruksanvisning</a></p>
<h1>FixIt: address findings</h1>
<p>Comparing <strong>{html.escape(xml_path.name)}</strong> with <strong>{html.escape(analysis["source_pdf"])}</strong>.
Physical decoder settings have not been checked.</p>{notice}
<p>Before editing: stop trains and automatic operation, and back up the Rocrail workspace and plan.
Change the specified <strong>Port</strong>, not Address or gate.</p>
<p>The saved XML reports Rocrail {html.escape(root.get("rocrailversion", "not recorded"))} and Rocview
{html.escape(root.get("rocguiversion", "not recorded"))}. Dialog labels can vary by version.</p>
<h2>Finding-specific guidance</h2>
{"".join(sections) if sections else "<p>No findings are currently recorded.</p>"}
<h2>Alternatives</h2>
<h3>Hardware agrees with Rocrail</h3>
<p>Leave Rocrail unchanged and update the address document instead.</p>
<h3>Planned or unused output</h3>
<p>Leave the output unchanged until it is needed.</p>
<h3>Change the decoder instead</h3>
<p>Decoder programming is separate from changing Rocrail.</p>
<h2>After a change</h2>
<ol><li>Test the affected signal or output with the tracks clear.</li>
<li>Obtain a fresh copy or export of the saved plan XML. From the project folder run
<code>python pdfcheck.py "DMJK-Adresser.pdf" "PLAN.xml"</code>, replacing PLAN.xml with that file.
This requires <code>pdftotext</code> on PATH and overwrites <code>pdfcheck.txt</code> and <code>drawings\\error.json</code>.</li>
<li>Run <code>python drawings\\stations.py "PLAN.xml"</code> with the same plan to regenerate the drawings and this guide.</li></ol>
<h2>Alternative: import an edited XML plan</h2>
<p>Upload transfers the whole plan but does not activate it. These steps use the older Rocview workflow.</p>
<ol>
<li>Edit a current copy of the active plan. Save it with a filename that does not already exist in the
server's working directory, such as <code>DMJK-fixed.xml</code>.</li>
<li>Connect Rocview to the Rocrail server. Select <strong>File → Upload</strong> and choose the edited XML file.</li>
<li>Check that the uploaded file exists in the server's Rocrail working directory.</li>
<li>In <strong>File → Rocrail Properties → General</strong>, note the current <strong>Track plan file</strong>.
Change it to the uploaded filename on the server and click <strong>OK</strong>.</li>
<li>Restart the Rocrail server and reconnect Rocview. Check the changed fields and test the affected equipment
with the tracks clear.</li>
<li>To undo the import, restore the previous <strong>Track plan file</strong> setting and restart the server.</li>
</ol>
</main></body></html>
"""


DEPENDENCY_TOOLBAR = """<div class="dependency-toolbar">
<button id="dependency-toggle" type="button" aria-pressed="false" aria-controls="dependency-inspector">Inspect dependencies</button>
<section id="dependency-inspector" class="dependency-inspector" aria-label="Dependency inspector" hidden>
<p>Click a signal, turnout, detector, block, output or panel switch. Choose a relationship, then click its objects to follow the chain. Orange marks the selected item; purple marks related objects.</p>
<p>Configured action controls and route commands are shown; conditions are not evaluated. Route locking and other implicit Rocrail rules are not included.</p>
<div id="dependency-breadcrumbs" class="dependency-breadcrumbs"></div>
<p id="dependency-status" role="status">Select an item in the drawing.</p>
<div id="dependency-details"></div>
</section></div>"""

FINDING_NAVIGATION = """<script>
function showDrawingTarget() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id.startsWith("finding-") && !id.startsWith("control-")) return;
  document.getElementById(id)?.scrollIntoView({block: "center", inline: "center"});
}
window.addEventListener("load", showDrawingTarget);
window.addEventListener("hashchange", showDrawingTarget);
</script>"""


def render_control_html(plan):
    objects = plan["objects"]
    min_x = min((item["x"] for item in objects), default=0)
    min_y = min((item["y"] for item in objects), default=0)
    width = (max((item["x"] for item in objects), default=0) - min_x + 1) * 90 + 40
    height = (max((item["y"] for item in objects), default=0) - min_y + 1) * 64 + 40
    symbols = []
    for item in objects:
        kind, object_id = item["kind"], item["id"]
        x, y = (item["x"] - min_x) * 90 + 45, (item["y"] - min_y) * 64 + 25
        shape = ('<circle class="signal" r="6"/>' if kind == "sg" else
                 '<circle class="sensor" r="5"/>' if kind == "fb" else
                 f'<rect x="-7" y="-6" width="14" height="12" fill="{("#16634c" if kind == "bk" else "#7a4d95")}"/>')
        warning = (f'<g transform="translate(-28 -28)">{finding_marker()}</g>'
                   if any(finding["status"] != "match" for finding in item.get("findings", [])) else "")
        orientation = signal_orientation(item, -22, 5) if kind == "sg" else ""
        symbols.append(f'<g id="control-{html.escape(kind, quote=True)}-{html.escape(object_id, quote=True)}" '
                       f'data-kind="{kind}" data-id="{html.escape(object_id, quote=True)}" transform="translate({x} {y})">'
                       f'<title>{html.escape(object_title(item))}</title>'
                       f'<circle class="feedback-ring" r="18"/>{shape}{orientation}'
                       f'<text x="0" y="24">{html.escape(object_id)}</text>{warning}</g>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Control level — Rocrail schematic</title><style>{STYLE}</style></head>
<body><main><p><a href="index.html">All station drawings</a> · <a href="errors.html">Address findings</a></p><h1>Control level</h1>
<p>Signals, blocks, feedback inputs and outputs on the Rocrail Control level, from {html.escape(plan["source_xml"])}.
Positions are XML screen coordinates, not physical locations or track connections. Route and text symbols are not shown.
Scroll to see the full level; use Inspect dependencies to follow relationships.</p>
<div class="legend"><span>🔵 Signal</span><span>← Signal XML symbol orientation (not verified facing or train direction)</span><span style="color:#16634c">■ Block</span>
<span style="color:#657280">● Feedback input</span><span style="color:#7a4d95">■ Output</span></div>
{analysis_notice(plan)}{finding_summary(plan, control=True)}{DEPENDENCY_TOOLBAR}<div class="canvas"><svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
viewBox="0 0 {width} {height}" role="group" aria-label="Rocrail control level">{"".join(symbols)}</svg></div></main>
<script id="dependency-data" type="application/json">{dependency_data(plan)}</script>
<script>{(OUTPUT / "dependency_inspector.js").read_text(encoding="utf-8")}</script>{FINDING_NAVIGATION}</body></html>
"""


def analysis_notice(plan):
    return ('<p class="finding-summary">⚠ The XML has changed since the address analysis; '
            '<a href="errors.html">rerun the analysis</a> to discover new findings.</p>'
            if plan.get("analysis_stale") else "")


def render_html(plan):
    drawings = [render_svg(plan, bounds, show_modules=index == 0)
                for index, bounds in enumerate(plan["regions"])]
    if len(drawings) > 1:
        drawings[1] = "<h2>Approach signals near Kobbarvik</h2>" + drawings[1]
    note = ("<p>Havna is shown as a connection only: its block h1 is on the separate control level, not the main layout level.</p>"
            if plan["station"] == "Havna" else "")
    missing = ", ".join(plan["references_outside_drawing"]) or "none"
    unresolved = ", ".join(plan["unresolved_destinations"]) or "none"
    name = html.escape(plan["station"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Rocrail schematic</title><style>{STYLE}</style></head>
<body><main><p><a href="index.html">All station drawings</a> · <a href="errors.html">Address findings</a></p><h1>{name}</h1>
<p>Rocrail schematic from <strong>{html.escape(plan["source_xml"])}</strong>. This is not a scale drawing or live railway status. LS100 and OD-2 assignments are from DMJK-Adresser.pdf; XML addresses are shown separately. Open a module type and click a module to locate its objects, or click a panel switch to highlight associated turnouts. Action conditions are not evaluated. Scroll horizontally to see the full plan.</p>
{note}{analysis_notice(plan)}{finding_summary(plan)}<div class="legend"><span>🔵 Signal</span><span>← Signal XML symbol orientation (not verified facing or train direction)</span><span style="color:#a44c12">Turnout / crossing</span><span style="color:#16634c">Block</span><span style="color:#657280">● Detector</span><span style="color:#7a4d95">■ Track output</span><span style="color:#a00000">⚠ Address finding</span></div>
{DEPENDENCY_TOOLBAR}
{"".join(drawings)}
<p>Connection names are based on paired Rocrail connectors and the adjoining layout. Unresolved connection labels: {html.escape(unresolved)}.</p>
<p>Report references outside the drawing: {html.escape(missing)}.</p></main>
<script id="dependency-data" type="application/json">{dependency_data(plan)}</script>
<script>{(OUTPUT / "feedback_selection.js").read_text(encoding="utf-8")}</script>
<script>{(OUTPUT / "dependency_inspector.js").read_text(encoding="utf-8")}</script>{FINDING_NAVIGATION}</body></html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true", help="check the generated station data")
    args = parser.parse_args()
    xml_path = args.xml or max(ROOT.glob("*-DMJK-Layout.xml"), key=lambda path: path.name)
    root = ET.parse(xml_path).getroot()
    report = (ROOT / "signal_logic.md").read_text(encoding="utf-8")
    plans = {key: extract_plan(root, xml_path, report, key) for key in STATIONS}
    control = extract_control_level(root, xml_path)
    all_plans = {**plans, **({"control": control} if control is not None else {})}
    findings_path = OUTPUT / "error.json"
    if not findings_path.is_file():
        raise SystemExit("drawings\\error.json is missing; run python pdfcheck.py PDF XML first.")
    analysis = json.loads(findings_path.read_text(encoding="utf-8"))
    findings = check_address_findings(root, analysis["findings"], all_plans)
    analysis_stale = analysis["source_xml_sha256"] != hashlib.sha256(xml_path.read_bytes()).hexdigest()
    action_records = dependency_actions(root)
    detectors = block_detectors(root)
    locations = drawing_locations(all_plans)
    panel_names = {element.get("id"): panel_input_name(element) for element in root.findall("./fblist/fb")
                   if element.get("id") in PANEL_INPUTS}
    descriptions = dependency_objects(root)
    for plan in all_plans.values():
        plan["dependency_actions"] = action_records
        plan["block_detectors"] = detectors
        plan["drawing_locations"] = locations
        plan["panel_names"] = panel_names
        plan["dependency_objects"] = descriptions
        plan["analysis_stale"] = analysis_stale
    if args.check:
        report_html = render_findings_html(findings, analysis, xml_path)
        fixit_html = render_fixit_html(findings, analysis, xml_path, root)
        for finding in findings:
            assert f'href="{html.escape(fixit_link(finding), quote=True)}"' in report_html
            assert f'id="{html.escape(fixit_anchor(finding), quote=True)}"' in fixit_html
            for location in finding["locations"]:
                assert html.escape(location["file"], quote=True) in report_html
                assert html.escape(location["file"], quote=True) in fixit_html
                filename, anchor = location["file"].split("#", 1)
                plan = all_plans[filename.removesuffix(".html")]
                drawing = render_control_html(plan) if filename == "control.html" else render_html(plan)
                assert f'id="{anchor}"' in drawing
            assert html.escape(finding_text(finding)) in report_html
        assert "XML has changed since the analysis" in render_findings_html(
            findings, {**analysis, "source_xml_sha256": "stale"}, xml_path)
        examples = [
            {"kind": "sg", "id": "is03", "actual": {"port1": "1005", "port2": "1005"},
             "expected": [1005, 1006], "status": "mismatch", "locations": []},
            {"kind": "co", "id": "moP1", "actual": {"port": "1026"},
             "expected": [1018], "status": "mismatch", "locations": []},
            {"kind": "co", "id": "yoP1", "actual": {"port": "1025"},
             "expected": [1017], "status": "mismatch", "locations": []},
        ]
        examples_html = render_fixit_html(examples, analysis, xml_path, root)
        assert "from <strong>1005</strong> to <strong>1006</strong>" in examples_html
        assert "from <strong>1025</strong> to <strong>1017</strong>" in examples_html
        assert "from <strong>1026</strong> to <strong>1018</strong>" in examples_html
        stale_fixit = render_fixit_html(examples, {**analysis, "source_xml_sha256": "stale"}, xml_path, root)
        assert "XML has changed since the PDF analysis" in stale_fixit
        assert "Rocrail steps" not in stale_fixit
        for status in ("match", "unverified"):
            altered = [{**finding, "status": status} for finding in examples]
            page = render_fixit_html(altered, analysis, xml_path, root)
            assert "Rocrail steps" not in page
        escaped = {**examples[0], "id": 'x"&<#', "locations": [{"file": "x.html#&", "name": "<Test>"}]}
        escaped_page = render_fixit_html([escaped], analysis, xml_path, root)
        assert 'id="fix-sg-x&quot;&amp;&lt;#"' in escaped_page
        assert '&lt;Test&gt;' in escaped_page and 'href="x.html#&amp;"' in escaped_page
        assert fixit_link(escaped) == "fixit.html#fix-sg-x%22%26%3C%23"
        assert "No findings are currently recorded." in render_fixit_html([], analysis, xml_path, root)
        finding_fixture = ET.fromstring('<plan><sglist><sg id="s" port1="5" port2="5"/></sglist></plan>')
        entry = {"kind": "sg", "id": "s", "category": "signal",
                 "attributes": ["port1", "port2"], "decoder_attributes": ["addr"], "expected": [5, 6]}
        def fixture_plan():
            return {"test": {"station": "Test", "objects": [{"kind": "sg", "id": "s", "x": 0, "y": 0}]}}
        original = fixture_plan()
        assert check_address_findings(finding_fixture, [entry], original)[0]["status"] == "mismatch"
        assert 'class="finding-marker"' in render_object(original["test"]["objects"][0], {"min_x": 0, "min_y": 0})
        finding_fixture.find("./sglist/sg").set("port2", "6")
        corrected = fixture_plan()
        assert check_address_findings(finding_fixture, [entry], corrected)[0]["status"] == "match"
        assert 'class="finding-marker"' not in render_object(corrected["test"]["objects"][0], {"min_x": 0, "min_y": 0})
        finding_fixture.find("./sglist/sg").set("addr", "3")
        assert check_address_findings(finding_fixture, [entry], fixture_plan())[0]["status"] == "unverified"
        assert check_address_findings(ET.fromstring("<plan/>"), [entry], {})[0]["status"] == "unverified"
        panel_root = ET.fromstring('<plan><fblist><fb id="p" addr="9"/></fblist></plan>')
        panel = {"id": "p", "types": ["Panel switch"], "description": "inn y", "display_name": "Inn fra Myra"}
        panel_plans = {"test": {"station": "Test", "objects": [], "feedback_modules": [{"inputs": [panel]}]}}
        panel_entry = {"kind": "fb", "id": "p", "category": "detector", "attributes": ["addr"], "expected": [8]}
        panel_findings = check_address_findings(panel_root, [panel_entry], panel_plans)
        assert panel_findings[0]["locations"] == [{"name": "Test", "file": "test.html#finding-fb-p"}]
        assert 'id="finding-fb-p" class="panel-marker has-finding"' in render_panel_inputs(panel_plans["test"])
        assert 'addr=9' in render_panel_inputs(panel_plans["test"])
        solberg = {item["id"]: item for item in plans["solberg"]["objects"]}
        assert solberg["ss01"]["address"]["port1"] == "516"
        assert solberg["sv01"]["address"]["port1"] == "1"
        assert solberg["sd09"]["address"]["addr"] == "520"
        def module(key, name):
            return next(item for item in plans[key]["feedback_modules"] if item["name"] == name)
        assert module("solberg", "s#3")["rs_addresses"] == [67, 68]
        assert {(item["id"], item["port"]) for item in module("solberg", "s#3")["inputs"]} >= {
            ("sd06", 10), ("sd18", 7)}
        assert len(module("solberg", "s#3")["inputs"]) == 7
        assert len(module("skiftegaard", "s#3")["inputs"]) == 4
        assert len(module("mjondalen", "m#2")["inputs"]) == 6
        assert len(module("havna", "m#2")["inputs"]) == 2
        assert len(module("havna", "n#3")["inputs"]) == 1
        assert len(module("sigdal", "i#5 test")["inputs"]) == 3
        assert next(item for item in module("norbotten", "n#2")["inputs"] if item["id"] == "nd15")["blocks"] == ["n7"]
        assert not next(item for item in module("solberg", "s#2")["inputs"] if item["id"] == "sd10")["blocks"]
        assert module("solberg", "s#3")["inputs"][3]["types"] == ["Panel switch"]
        assert module("solberg", "s#2")["inputs"][0]["types"] == ["Track / block detector"]
        assert module("sigdal", "i#5 test")["inputs"][0]["types"] == ["Test input"]
        assert len(LS100_MODULES) == 22
        def ls100(key, name):
            return next(item for item in plans[key]["ls100_modules"] if item["name"] == name)
        assert ls100("solberg", "g#2")["rs_address"] == 10
        assert [(item["id"], item["port"], item["dcc_address"]) for item in ls100("solberg", "g#2")["turnouts"]] == [
            ("sv06", 4, 40)]
        paired = [item for item in ls100("kobbarvik", "k#1")["turnouts"] if item["port"] == 1]
        assert [(item["id"], item["dcc_address"], item["rocrail_address"]["port1"]) for item in paired] == [
            ("kv01", 65, "65"), ("kv02", 65, "402")]
        assert any(item["name"] == "s#3" for item in plans["skiftegaard"]["ls100_modules"])
        assert any(item["name"] == "y#3" for item in plans["sigdal"]["ls100_modules"])
        assert not plans["havna"]["ls100_modules"]
        assert {"mv05", "mv07", "mv09", "mv10"} <= set(plans["mjondalen"]["ls100_unmapped_turnouts"])
        assert "No documented LS100 assignment: mv05, mv07, mv09, mv10." in render_html(plans["mjondalen"])
        assert ls100_modules([{"kind": "sw", "id": "not-in-pdf", "address": {"port1": "1"}}]) == []
        assert 'data-module-name="LS100 k#1"' in render_html(plans["kobbarvik"])
        assert '<td>kv02</td><td>65</td><td>addr1=0, port1=402' in render_html(plans["kobbarvik"])
        def signal_module(key, name):
            return next(item for item in plans[key]["signal_modules"] if item["name"] == name)
        assert len(SIGNAL_MODULES) == 16
        is13 = next(item for item in signal_module("sigdal", "s#1")["signals"] if item["id"] == "is13")
        assert is13["ports"] == "7-8" and is13["dcc_addresses"] == [518, 519]
        is03 = next(item for item in signal_module("sigdal", "i#1")["signals"] if item["id"] == "is03")
        assert is03["dcc_addresses"] == [1005, 1006] and is03["rocrail_address"]["port1"] == "1005"
        assert "is04" in plans["sigdal"]["signal_unmapped"]
        assert signal_modules([{"kind": "sg", "id": "not-in-pdf", "address": {"port1": "513"}}]) == []
        assert format_addresses([519, 513, 518, 513]) == "513, 518–519"
        drawing = render_html(plans["solberg"])
        assert 'data-module-name="OD-2 s#1"' in drawing
        assert 'id="modules-rs" hidden' in drawing and 'id="modules-ls" hidden' in drawing
        assert 'id="modules-dcc" hidden' in drawing
        assert 'aria-controls="modules-dcc">DCC signal decoders' in drawing
        assert 'data-kind="sg"' in drawing and 'class="feedback-ring"' in render_object(solberg["ss01"], plans["solberg"]["bounds"])
        for kind, label in (("sg", "signal-label"), ("sw", "turnout-label"), ("bk", "block-label"), ("fb", "sensor-label")):
            item = next(item for item in plans["solberg"]["objects"] if item["kind"] == kind)
            rendered = render_object(item, plans["solberg"]["bounds"])
            assert rendered.index('class="feedback-ring"') < rendered.index(f'class="{label}"')
            if kind in ("sw", "fb"):
                assert 'class="feedback-ring" cx="28" cy="36"' in rendered
        assert "No documented OD-2 assignment: is04" in render_html(plans["sigdal"])
        turnout = root.find("./swlist/sw")
        previous = turnout.get("fbG")
        turnout.set("fbG", "sd06")
        assigned = next(item for item in feedback_modules(root, "solberg") if item["name"] == "s#3")
        sd06 = next(item for item in assigned["inputs"] if item["id"] == "sd06")
        assert sd06["types"] == ["Panel switch", "Turnout feedback"]
        assert sd06["turnouts"] == [turnout.get("id")]
        if previous is None:
            turnout.attrib.pop("fbG")
        else:
            turnout.set("fbG", previous)
        assert 'RS 67–68 · 7 configured inputs' in render_html(plans["solberg"])
        assert '<th>Input</th><th>Name / ID</th><th>Address</th><th>Type</th><th>Details</th>' in render_html(plans["solberg"])
        assert 'data-module-name="s#3"' in render_html(plans["solberg"])
        assert 'class="panel-marker" data-panel-select="sd06"' in render_html(plans["solberg"])
        assert panel_names["id16"] == "Til Myra Ut" and panel_names["id17"] == "Inn fra Myra"
        assert panel_names["sd05"] == "Til Sigdal / Rognmo Ut"
        assert panel_names["sd06"] == "Inn fra Sigdal / Rognmo"
        assert panel_names["sd18"] == "Fra Solberg (bit 0)"
        assert panel_input_name(ET.fromstring('<fb id="p" desc="ut y/g"/>')) == "Til Myra / Solberg Skiftegård Ut"
        assert panel_input_name(ET.fromstring('<fb id="p" desc="ut x"/>')) == "Ut x"
        assert panel_input_name(ET.fromstring('<fb id="p"/>')) == "p"
        sigdal_html = render_html(plans["sigdal"])
        assert 'title="Rocrail: id16 · XML: ut y"' in sigdal_html
        assert 'aria-label="Til Myra Ut (Rocrail: id16)">Til Myra Ut</button>' in sigdal_html
        assert '<td title="Rocrail: id17">Inn fra Myra</td>' in sigdal_html
        panel_sd06 = next(item for item in module("solberg", "s#3")["inputs"] if item["id"] == "sd06")
        assert {"sv01", "sv02", "sv03"} <= set(panel_sd06["action_turnouts"]["checked"])
        assert not panel_sd06["action_turnouts"]["commanded"]
        panel_sd18 = next(item for item in module("solberg", "s#3")["inputs"] if item["id"] == "sd18")
        assert {"sv08", "sv09"} <= set(panel_sd18["action_turnouts"]["checked"])
        assert next(item for item in module("solberg", "s#3")["inputs"] if item["id"] == "sd21")["action_turnouts"] == {
            "checked": [], "commanded": []}
        example = ET.fromstring("""<plan>
          <fblist><fb id="p"><actionctrl id="start" state="true"/></fb></fblist>
          <colist><co id="relay">
            <actionctrl id="route" state="on"><actioncond type="sw" id="s1"/></actionctrl>
            <actionctrl id="direct" state="on"/><actionctrl id="start" state="on"/>
            <actionctrl id="wrong" state="off"/>
          </co></colist>
          <stlist><st id="r"><swcmd type="sw" id="s2"/><swcmd type="sw" id="s3" atfree="true"/></st></stlist>
          <aclist><ac id="start" type="co" oid="relay" cmd="on"/>
            <ac id="route" type="st" oid="r" cmd="lockset"/>
            <ac id="direct" type="sw" oid="s4" cmd="turnout"/>
            <ac id="wrong" type="sw" oid="unreachable" cmd="straight"/>
          </aclist></plan>""")
        assert panel_action_turnouts(example, ["p"])["p"] == {
            "checked": ["s1"], "commanded": ["s2", "s4"]}
        direct = next(action for action in plans["solberg"]["dependency_actions"]
                      if action["id"] == "soINiOn" and action["trigger"]["id"] == "sd06")
        assert direct["result"] == {"type": "co", "id": "soINi", "command": "on"}
        green = next(action for action in plans["solberg"]["dependency_actions"]
                     if action["id"] == "ss01green" and action["trigger"]["id"] == "soINi"
                     and {condition["id"] for condition in action["conditions"]}
                     == {"sv01", "sv02", "sv03", "sd09", "sd13"})
        assert green["all_conditions"] and green["result"]["id"] == "ss01"
        fixture = ET.fromstring("""<plan><aclist><ac id="a" type="sg" oid="s" cmd="green"/></aclist>
          <swlist><sw id="w"><actionctrl id="a" state="straight" allconditions="false" auto="false">
            <actioncond type="sw" id="w" state="straight" mustbetrue="true"/>
            <actioncond type="fb" id="d" state="false" mustbetrue="false"/>
          </actionctrl><actionctrl id="missing"/></sw></swlist>
          <bklist><bk id="b"><fbevent id="d"/></bk></bklist><fblist><fb id="d2" blockid="b"/></fblist>
        </plan>""")
        actions = dependency_actions(fixture)
        assert len(actions) == 2 and not actions[0]["all_conditions"]
        assert actions[0]["conditions"][0]["mustbetrue"] == "true" and actions[0]["settings"]["auto"] == "false"
        assert actions[1]["result"] is None
        assert block_detectors(fixture) == {"b": ["d", "d2"]}
        assert descriptions["fb:yd05"] == {"name": "Myra block 05", "role": "track"}
        assert descriptions["fb:id16"] == {"name": "Sigdal Til Myra Ut panel switch", "role": "panel"}
        assert descriptions["fb:id17"] == {"name": "Sigdal Inn fra Myra panel switch", "role": "panel"}
        assert descriptions["sw:yv03"]["name"] == "Myra turnout 03"
        assert descriptions["co:yoP1"]["name"] == "Myra Planovergang 1 output"
        assert not descriptions["co:yoP1"].get("internal")
        assert descriptions["co:ys01ctl"]["internal"]
        assert descriptions["co:ioUTy"]["name"] == "Sigdal exit towards Myra selection"
        crossing_action = next(action for action in action_records
                               if action["id"] == "yoP1on" and action["trigger"]["id"] == "yd05")
        assert crossing_action["trigger"]["state"] == "true"
        assert crossing_action["result"] == {"type": "co", "id": "yoP1", "command": "on"}
        assert [(condition["id"], condition["state"]) for condition in crossing_action["conditions"]] == [("yv03", "straight")]
        feedback_fixture = ET.fromstring('<plan><swlist><sw fbG="yd05"/></swlist>'
                                         '<fblist><fb id="yd05"/><fb id="fb26"/></fblist></plan>')
        assert dependency_objects(feedback_fixture)["fb:yd05"]["role"] == "feedback"
        assert dependency_objects(feedback_fixture)["fb:fb26"]["role"] == "feedback"
        for orientation, arrow in (("west", "←"), ("east", "→"), ("north", "↑"), ("south", "↓")):
            signal = {"kind": "sg", "id": "test", "x": 0, "y": 0, "ori": orientation}
            assert f'class="signal-orientation" x="10" y="43">{arrow}' in render_object(signal, {"min_x": 0, "min_y": 0})
        signal.pop("ori")
        assert 'class="signal-orientation"' not in render_object(signal, {"min_x": 0, "min_y": 0})
        route_command = next(action for action in plans["norbotten"]["dependency_actions"]
                             if action["kind"] == "route_command" and action["trigger"]["id"] == "nrt-i2-n7"
                             and action["result"]["id"] == "nv01")
        assert route_command["result"]["command"] == "straight" and route_command["settings"]["atfree"] == "false"
        assert locations["fb"]["gd08"] == [{"name": "Solberg Skiftegård", "file": "skiftegaard.html"}]
        assert {place["file"] for place in locations["fb"]["gd06"]} == {"skiftegaard.html", "kobbarvik.html"}
        assert locations["co"]["soINi"] == [{"name": "Control level", "file": "control.html#control-co-soINi"}]
        assert locations["fb"]["sd06"] == [{"name": "Solberg", "file": "solberg.html"}]
        assert locations["sg"]["is07"] == [{"name": "Control level", "file": "control.html#control-sg-is07"}]
        assert locations["co"]["ib18"] == [{"name": "Sigdal", "file": "sigdal.html"}]
        sigdal_outputs = {item["id"]: item for item in plans["sigdal"]["objects"] if item["kind"] == "co"}
        assert {"ib11", "ib12", "ib14", "ib18", "ib19", "ib22"} <= sigdal_outputs.keys()
        assert (sigdal_outputs["ib18"]["x"], sigdal_outputs["ib18"]["y"], sigdal_outputs["ib18"]["svgtype"]) == (44, 18, "7")
        for name in ("ib18", "ib19"):
            output = render_object(sigdal_outputs[name], plans["sigdal"]["bounds"])
            assert f'data-id="{name}" data-kind="co"' in output
            assert 'd="M 0 16 H 32"' in output and 'class="output-label"' in output
        assert 'd="M 16 0 V 32"' in render_object(sigdal_outputs["ib14"], plans["sigdal"]["bounds"])
        assert {"nb-n1", "nb-n7"} <= {item["id"] for item in plans["norbotten"]["objects"] if item["kind"] == "co"}
        crossing = next(item for item in plans["myra"]["objects"] if item["id"] == "yoP1")
        assert crossing["svgtype"] == "12"
        assert "yoP1" in {item["id"] for item in plans["mjondalen"]["objects"] if item["kind"] == "co"}
        assert "koCtl" not in {item["id"] for item in plans["kobbarvik"]["objects"]}
        output_element = next(element for element in root.findall("./colist/co") if element.get("id") == "ib18")
        for attribute, value in (("show", "false"), ("svgtype", "0")):
            previous = output_element.get(attribute)
            output_element.set(attribute, value)
            assert "ib18" not in {item["id"] for item in extract_plan(root, xml_path, report, "sigdal")["objects"]}
            output_element.set(attribute, previous)
        is07 = next(item for item in control["objects"] if item["kind"] == "sg" and item["id"] == "is07")
        assert is07["z"] == 1 and is07["blockid"] == "id03" and is07["address"] == {}
        control_html = render_control_html(control)
        assert 'id="control-sg-is07" data-kind="sg" data-id="is07"' in control_html
        is08 = next(item for item in control["objects"] if item["id"] == "is08")
        assert is08["ori"] == "east" and signal_orientation(is08, -22, 5).endswith(">→</text>")
        assert 'id="control-co-ioUTy"' in control_html and 'id="control-bk-h1"' in control_html
        assert 'class="track"' not in control_html
        assert extract_control_level(ET.fromstring("<plan/>"), xml_path) is None
        assert 'id="dependency-data" type="application/json"' in render_html(plans["solberg"])
        assert render_html(plans["mjondalen"]).count('aria-label="Feedback modules for this station"') == 1
        assert "Rocrail address:" in render_html(plans["solberg"])
        assert {item["id"] for item in plans["mjondalen"]["objects"]} >= {
            "ms01", "ms02", "ms03", "m1", "tk20131116223055816"}
        assert "kd02" in {item["id"] for item in plans["kobbarvik"]["objects"]}
        assert "tk20141111205947188" in {item["id"] for item in plans["sigdal"]["objects"]}
        assert 'M 16 0 V 32' in track_shape({"kind": "sw", "type": "left", "ori": "north"})
        assert 'M 16 32 V 64' in track_shape({"kind": "bk", "ori": "north"})
        assert 'M 64 16 H 128' in track_shape({"kind": "bk", "smallsymbol": "false"})
        assert 'data-part="slip"' in track_shape({"kind": "sw", "type": "dcrossing"})
        for key, (_, letter, _) in STATIONS.items():
            found = {item["id"] for item in plans[key]["objects"]}
            own = {element.get("id") for tag in ("sg", "sw")
                   for element in root.findall(f"./{tag}list/{tag}")
                   if element.get("id", "").startswith(letter) and element.get("z", "0") == "0"}
            assert own <= found, (key, own - found)
            assert not plans[key]["unresolved_destinations"], (key, plans[key]["unresolved_destinations"])
        assert any(item["name"] == "Sigdal" and item["basis"] == "paired connector 1"
                   for item in plans["solberg"]["destinations"])
        connector_one = [element for element in root.findall("./tklist/tk")
                         if element.get("type") == "connector" and element.get("tknr") == "1"
                         and element.get("z", "0") == "0"]
        assert not connector_matches(solberg["tk20131116001925260"], "1", "Myra", {"1": connector_one})
        assert not connector_matches(solberg["tk20131116001925260"], "1", "Sigdal", {"1": connector_one[:1]})
        assert render_html(plans["solberg"]).count("Skiftegård / Kobbarvik →") == 1
        assert all(plan["objects"] for plan in plans.values())
        print("Station drawing checks passed.")
        return
    for key, plan in plans.items():
        (OUTPUT / f"{key}.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (OUTPUT / f"{key}.html").write_text(render_html(plan), encoding="utf-8")
    links = "".join(f'<li><a href="{key}.html">{html.escape(name)}</a></li>' for key, (name, _, _) in STATIONS.items())
    if control is not None:
        (OUTPUT / "control.json").write_text(json.dumps(control, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (OUTPUT / "control.html").write_text(render_control_html(control), encoding="utf-8")
        links += '<li><a href="control.html">Control level</a></li>'
    (OUTPUT / "errors.html").write_text(render_findings_html(findings, analysis, xml_path), encoding="utf-8")
    (OUTPUT / "fixit.html").write_text(render_fixit_html(findings, analysis, xml_path, root), encoding="utf-8")
    open_count = sum(finding["status"] != "match" for finding in findings)
    (OUTPUT / "index.html").write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Station drawings</title>'
        f'<style>{STYLE}</style></head><body><main><h1>Station drawings</h1>'
        f'<p><a href="bruksanvisning.html">Bruksanvisning (norsk)</a> · '
        f'<a href="errors.html">⚠ Address findings ({open_count})</a> · <a href="fixit.html">FixIt guide</a></p>'
        f'{analysis_notice({"analysis_stale": analysis_stale})}<ul>{links}</ul>'
        f'<p>Regenerate with <code>python drawings\\stations.py</code>.</p></main></body></html>',
        encoding="utf-8")
    print(f"Wrote {len(plans)} station drawings and {int(control is not None)} control drawing from {xml_path.name}.")


if __name__ == "__main__":
    main()

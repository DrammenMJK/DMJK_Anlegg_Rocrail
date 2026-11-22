/* Experimental action replay and geometric track highlighting. */
class SolbergSimulator {
  constructor(plan) {
    this.plan = plan;
    this.reset();
  }

  reset() {
    this.states = Object.fromEntries(Object.entries(this.plan.states).map(([type, values]) =>
      [type, { ...values }]
    ));
    this.turnouts = this.states.sw;
    this.signals = this.states.sg;
    this.warning = "";
    for (const item of this.plan.objects) {
      if (item.kind === "sw" && ["left", "right"].includes(item.type)) {
        this.turnouts[item.id] = "straight";
      }
    }
    for (const id of Object.keys(this.signals)) this.signals[id] = "red";
    for (const id of Object.keys(this.states.co)) {
      if (id.startsWith("so")) this.states.co[id] = "off";
    }
    for (const id of ["sd05", "sd06", "sd07", "sd08"]) this.states.fb[id] = "false";
  }

  toggleTurnout(id) {
    if (!["straight", "turnout"].includes(this.turnouts[id])) return;
    this.warning = "";
    this.changeState("sw", id, this.turnouts[id] === "straight" ? "turnout" : "straight");
  }

  pressPanel(id) {
    if (!["sd05", "sd06", "sd07", "sd08"].includes(id)) return;
    this.warning = "";
    this.changeState("fb", id, "true");
    this.changeState("fb", id, "false");
  }

  setDirection(value) {
    this.warning = "";
    this.changeState("fb", "sd18", value & 1 ? "true" : "false");
    this.changeState("fb", "sd19", value & 2 ? "true" : "false");
  }

  conditionMatches(condition) {
    return condition.state !== undefined &&
      this.states[condition.type]?.[condition.id] === condition.state;
  }

  actionMatches(action) {
    const required = action.conditions.filter(c => action.all_conditions || c.mustbetrue === "true");
    const optional = action.conditions.filter(c => !action.all_conditions && c.mustbetrue !== "true");
    return required.every(c => this.conditionMatches(c)) &&
      (!optional.length || optional.some(c => this.conditionMatches(c)));
  }

  changeState(type, id, state) {
    if (!this.states[type] || !(id in this.states[type]) || this.states[type][id] === state) return;
    this.states[type][id] = state;
    const queue = [{ type, id, state }];
    let processed = 0;
    while (queue.length && processed < 1000) {
      const event = queue.shift();
      processed++;
      for (const action of this.plan.actions) {
        if (action.caller_type !== event.type || action.caller_id !== event.id ||
            !["any", event.state].includes(action.caller_state) || !this.actionMatches(action)) continue;
        const values = this.states[action.target_type];
        if (!values || !(action.target in values)) continue;
        let next = action.command;
        if (action.target_type === "fb") next = { on: "true", off: "false" }[next];
        if (action.target_type === "co" && next === "flip") next = values[action.target] === "on" ? "off" : "on";
        const allowed = {
          co: ["on", "off"], sg: ["red", "green", "yellow", "white"],
          sw: ["straight", "turnout"], fb: ["true", "false"]
        };
        if (!allowed[action.target_type]?.includes(next)) continue;
        const repeatedPanelRequest = event.type === "fb" && event.state === "true" &&
          action.target_type === "co" && next === "on";
        if (values[action.target] === next && !repeatedPanelRequest) continue;
        values[action.target] = next;
        queue.push({ type: action.target_type, id: action.target, state: next });
      }
    }
    if (queue.length) this.warning = "Action cycle detected; results may be incomplete.";
  }

  rotate(point, orientation) {
    const [x, y] = point;
    switch (orientation) {
      case "north": return [y, 32 - x];
      case "east": return [32 - x, 32 - y];
      case "south": return [32 - y, x];
      default: return point;
    }
  }

  edgesFor(item) {
    const point = ([x, y]) => `${item.x * 32 + x},${item.y * 32 + y}`;
    const edge = (part, a, b) => ({ id: item.id, part, a: point(a), b: point(b), item });
    const oriented = (part, a, b) =>
      edge(part, this.rotate(a, item.ori), this.rotate(b, item.ori));
    if (item.kind === "sw") {
      if (item.type === "crossing") {
        return [edge("main", [0, 16], [32, 16]), edge("cross", [16, 0], [16, 32])];
      }
      if (["left", "right"].includes(item.type)) {
        if (this.turnouts[item.id] === "turnout") {
          return [oriented("branch", item.type === "left" ? [32, 16] : [0, 16], [16, 32])];
        }
        return [edge("main", [0, 16], [32, 16])];
      }
      return [];
    }
    if (item.kind === "tk" && item.type === "curve") {
      return [oriented("main", [0, 16], [16, 32])];
    }
    if (item.kind === "tk" && item.type === "buffer") {
      return [oriented("main", [0, 16], [26, 16])];
    }
    if (item.kind === "bk") {
      return [edge("left", [0, 16], [32, 16]), edge("right", [32, 16], [64, 16])];
    }
    if (["north", "south"].includes(item.ori)) return [edge("main", [16, 0], [16, 32])];
    return [edge("main", [0, 16], [32, 16])];
  }

  highlightedTracks() {
    const edges = this.plan.objects.flatMap(item => this.edgesFor(item));
    const at = new Map();
    for (const edge of edges) {
      for (const point of [edge.a, edge.b]) {
        if (!at.has(point)) at.set(point, []);
        at.get(point).push(edge);
      }
    }
    const bounds = this.plan.bounds;
    const isBoundary = (point, edge) => {
      const [x, y] = point.split(",").map(Number);
      return x === bounds.min_x * 32 || x === (bounds.max_x + 1) * 32 ||
        y === bounds.min_y * 32 || y === (bounds.max_y + 1) * 32 ||
        (edge.item.kind === "tk" && edge.item.type === "buffer" && edge.b === point);
    };
    const terminals = new Set();
    for (const [point, neighbours] of at) {
      if (neighbours.length === 1 && isBoundary(point, neighbours[0])) terminals.add(point);
      if (neighbours.some(edge => edge.item.kind === "bk" &&
        /^s(?:[1-5]|50)$/.test(edge.id) &&
        point === `${(edge.item.x + 1) * 32},${edge.item.y * 32 + 16}`)) terminals.add(point);
    }
    const highlighted = new Set();
    for (const start of terminals) {
      const queue = [start];
      const previous = new Map([[start, null]]);
      while (queue.length) {
        const point = queue.shift();
        for (const edge of at.get(point)) {
          const next = point === edge.a ? edge.b : edge.a;
          if (previous.has(next)) continue;
          previous.set(next, { point, edge });
          queue.push(next);
        }
      }
      for (const end of terminals) {
        if (end === start || !previous.has(end)) continue;
        let point = end;
        while (point !== start) {
          const step = previous.get(point);
          highlighted.add(`${step.edge.id}:${step.edge.part}`);
          point = step.point;
        }
      }
    }
    return highlighted;
  }
}

function startSolberg(plan, document) {
  const simulator = new SolbergSimulator(plan);
  const direction = document.getElementById("direction");

  function refresh() {
    const tracks = simulator.highlightedTracks();
    for (const group of document.querySelectorAll("g[data-id][data-kind]")) {
      const { id, kind } = group.dataset;
      const title = group.querySelector("title");
      if (!group.dataset.sourceTitle) group.dataset.sourceTitle = title.textContent;
      if (kind === "sg") {
        const circle = group.querySelector(".signal");
        circle.setAttribute("class", `signal ${simulator.signals[id] || "red"}`);
        title.textContent = `${group.dataset.sourceTitle} · Simulated state: ${simulator.signals[id] || "red"}`;
      }
      if (kind === "sw" && group.classList.contains("turnout")) {
        group.setAttribute("aria-label", `${id}: ${simulator.turnouts[id]}. Activate to toggle.`);
        title.textContent = `${group.dataset.sourceTitle} · Simulated state: ${simulator.turnouts[id]}`;
      }
      for (const path of group.querySelectorAll(".track path")) {
        path.classList.toggle("selected", tracks.has(`${id}:${path.dataset.part}`));
        const inactive = kind === "sw" && group.classList.contains("turnout") &&
          ((path.dataset.part === "branch") !== (simulator.turnouts[id] === "turnout"));
        path.classList.toggle("inactive", inactive);
      }
    }
    const active = ["soINi", "soUTi", "soINg", "soUTg", "soUTm"]
      .filter(id => simulator.states.co[id] === "on");
    document.getElementById("status").textContent =
      `Active requests: ${active.join(", ") || "none"}. ${simulator.warning}`;
  }

  direction.addEventListener("change", () => {
    simulator.setDirection(Number(direction.value));
    refresh();
  });
  document.getElementById("reset").addEventListener("click", () => {
    simulator.reset();
    direction.value = String((simulator.states.fb.sd18 === "true" ? 1 : 0) +
      (simulator.states.fb.sd19 === "true" ? 2 : 0));
    refresh();
  });
  for (const button of document.querySelectorAll("button[data-panel]")) {
    button.addEventListener("click", () => {
      simulator.pressPanel(button.dataset.panel);
      refresh();
    });
  }
  for (const group of document.querySelectorAll("g.turnout")) {
    const toggle = () => {
      simulator.toggleTurnout(group.dataset.id);
      refresh();
    };
    group.addEventListener("click", toggle);
    group.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    });
  }
  direction.value = String((simulator.states.fb.sd18 === "true" ? 1 : 0) +
    (simulator.states.fb.sd19 === "true" ? 2 : 0));
  refresh();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { SolbergSimulator };
  if (process.argv.includes("--check")) {
    const assert = require("node:assert/strict");
    const plan = require("./solberg.json");
    const sim = new SolbergSimulator(plan);
    assert.equal(sim.signals.ss01, "red");
    sim.pressPanel("sd06");
    assert.equal(sim.signals.ss01, "green");
    assert.equal(sim.states.co.soINi, "on");
    assert(sim.highlightedTracks().has("sv03:main"));
    sim.toggleTurnout("sv03");
    assert.equal(sim.states.co.soINi, "off");
    assert.equal(sim.signals.ss01, "red");
    sim.pressPanel("sd06");
    assert.equal(sim.signals.ss01, "yellow");
    assert(sim.highlightedTracks().has("sv03:branch"));
    assert(!sim.highlightedTracks().has("sv03:main"));
    sim.toggleTurnout("sv01");
    assert.equal(sim.signals.ss01, "red");
    assert(!sim.highlightedTracks().has("ss01:main"));
    sim.reset();
    sim.pressPanel("sd06");
    assert.equal(sim.signals.ss01, "green");
    sim.pressPanel("sd05");
    assert.equal(sim.states.co.soINi, "off");
    assert.equal(sim.states.co.soUTi, "on");
    assert.equal(sim.signals.ss01, "red");
    assert.equal(sim.signals.ss06, "green");
    sim.reset();
    sim.pressPanel("sd07");
    assert.equal(sim.states.co.soINg, "on");
    assert.equal(sim.signals.ss16, "green");
    sim.toggleTurnout("sv13");
    assert.equal(sim.states.co.soINg, "off");
    assert.equal(sim.signals.ss16, "red");
    sim.pressPanel("sd07");
    assert.equal(sim.states.co.soINg, "off");
    sim.reset();
    for (let value = 0; value < 4; value++) {
      sim.setDirection(value);
      assert.equal(sim.states.fb.sd18, value & 1 ? "true" : "false");
      assert.equal(sim.states.fb.sd19, value & 2 ? "true" : "false");
    }
    sim.setDirection(1);
    sim.toggleTurnout("sv13");
    sim.pressPanel("sd08");
    assert.equal(sim.states.fb.sd18, "true");
    assert.equal(sim.states.fb.sd19, "false");
    assert.equal(sim.states.co.soUTg, "on");
    assert.equal(sim.states.co.soUTm, "on");
    assert.equal(sim.signals.ss13, "green");
    sim.toggleTurnout("sv13");
    assert.equal(sim.states.co.soUTg, "off");
    assert.equal(sim.states.co.soUTm, "off");
    assert.equal(sim.signals.ss13, "red");
    sim.reset();
    for (const id of ["sv02", "sv04", "sv05", "sv06", "sv07"]) sim.toggleTurnout(id);
    sim.pressPanel("sd06");
    assert.equal(sim.signals.ss01, "yellow");
    assert(sim.highlightedTracks().has("ss01:main"));
    assert(sim.highlightedTracks().has("sv07:branch"));
    assert(sim.highlightedTracks().has("tk20120602014108974:main"));
    assert(sim.actionMatches({ all_conditions: false, conditions: [
      { type: "sw", id: "sv01", state: "straight", mustbetrue: "true" },
      { type: "sw", id: "sv02", state: "turnout" },
      { type: "sw", id: "sv03", state: "straight" }
    ] }));
    assert(!sim.conditionMatches({ type: "st", id: "unknown", state: "unlocked" }));
    const simplePlan = {
      states: { sw: {}, sg: {}, fb: {}, co: {} }, actions: [],
      bounds: { min_x: 0, max_x: 2, min_y: 0, max_y: 2 },
      objects: [
        { id: "a", kind: "tk", type: "straight", x: 0, y: 1 },
        { id: "b", kind: "tk", type: "straight", x: 1, y: 1 },
        { id: "stop", kind: "tk", type: "buffer", x: 2, y: 1, ori: "west" }
      ]
    };
    const simple = new SolbergSimulator(simplePlan);
    assert.deepEqual([...simple.highlightedTracks()].sort(), ["a:main", "b:main", "stop:main"]);
    simplePlan.objects[2].type = "curve";
    assert.equal(simple.highlightedTracks().size, 0);
    simplePlan.bounds.max_x = 5;
    for (const id of ["s1", "s2", "s3", "s4", "s5", "s50"]) {
      simplePlan.objects = [
        { id: "a", kind: "tk", type: "straight", x: 0, y: 1 },
        { id, kind: "bk", x: 1, y: 1 },
        { id: "dead", kind: "tk", type: "straight", x: 3, y: 1 }
      ];
      const tracks = simple.highlightedTracks();
      assert(tracks.has("a:main") && tracks.has(`${id}:left`));
      assert(!tracks.has(`${id}:right`) && !tracks.has("dead:main"));
    }
    simplePlan.objects = [{ id: "s1", kind: "bk", x: 1, y: 1 }];
    assert.equal(simple.highlightedTracks().size, 0);
    simplePlan.objects.push({ id: "s2", kind: "bk", x: 3, y: 1 });
    assert.deepEqual([...simple.highlightedTracks()].sort(), ["s1:right", "s2:left"]);
    console.log("Solberg simulator checks passed.");
  }
} else if (typeof document !== "undefined") {
  startSolberg(JSON.parse(document.getElementById("plan-data").textContent), document);
}

(() => {
  function sameObject(left, right) {
    return !!left && !!right && left.type === right.type && left.id === right.id;
  }

  function relatedActions(actions, item) {
    return actions.filter(action => sameObject(action.trigger, item) || sameObject(action.result, item) ||
      action.conditions.some(condition => sameObject(condition, item)));
  }

  function conditionGroups(action) {
    return {
      required: action.conditions.filter(condition => action.all_conditions || condition.mustbetrue === "true"),
      alternatives: action.conditions.filter(condition => !action.all_conditions && condition.mustbetrue !== "true")
    };
  }

  function conditionSummary(action, name = condition => `${condition.type}:${condition.id}`) {
    const groups = conditionGroups(action);
    const term = condition => `${name(condition)}=${condition.state || "?"}`;
    const parts = groups.required.map(term);
    if (groups.alternatives.length) parts.push(`(${groups.alternatives.map(term).join(" OR ")})`);
    return parts.join(" AND ");
  }

  function rocrailFormula(action) {
    const name = item => `${item.type || "unknown"}:${item.id || "(no ID)"}`;
    const source = action.kind === "route_command"
      ? `${name(action.trigger)} (route command)` : `${name(action.trigger)}=${action.trigger.state}`;
    const result = action.result
      ? `${name(action.result)}=${action.result.command || "?"}` : "missing action";
    const conditions = conditionSummary(action);
    return `${source} → ${result} [${action.id}]${conditions ? ` if ${conditions}` : ""}`;
  }

  function objectName(item, objects) {
    const kinds = {fb: "Feedback input", sw: "Switch", sg: "Signal", co: "Output",
      bk: "Block", st: "Route", vr: "Variable", tx: "Text", ext: "External action"};
    return objects[`${item.type}:${item.id}`]?.name ||
      `${kinds[item.type] || item.type || "Unknown"} ${item.id || "(no ID)"}`;
  }

  function describeState(item, objects, event = false) {
    const name = objectName(item, objects);
    const state = item.state || "?";
    const role = objects[`${item.type}:${item.id}`]?.role;
    let description;
    if (item.type === "fb" && role === "track" && ["true", "false"].includes(state)) {
      description = `${name} is ${state === "true" ? "occupied" : "free"}`;
    } else if (item.type === "fb" && role === "panel" && ["true", "false"].includes(state)) {
      description = `${name} is ${state === "true" ? "active" : "inactive"}`;
    } else if (item.type === "sw" && ["straight", "turnout"].includes(state)) {
      description = `${name} is ${state === "straight" ? "straight" : "diverging"}`;
    } else if (item.type === "sg" && ["red", "green", "yellow", "white"].includes(state)) {
      description = `${name} is set to ${state}`;
    } else if (item.type === "co" && role === "route_selection" && ["on", "off"].includes(state)) {
      description = `${name} is ${state === "on" ? "active" : "inactive"}`;
    } else if (item.type === "co" && ["on", "off"].includes(state)) {
      description = `${name} is ${state}`;
    } else if (item.type === "st" && ["locked", "unlocked"].includes(state)) {
      description = `${name} is ${state}`;
    } else {
      description = `${name} ${event && state === "any" ? "receives any event" : `has state "${state}"`}`;
    }
    return item.subid ? `${description} (sub-ID: ${item.subid})` : description;
  }

  function describedConditions(action, objects) {
    const groups = conditionGroups(action);
    const required = groups.required.map(item => describeState(item, objects));
    if (groups.alternatives.length) {
      required.push(`at least one of (${groups.alternatives.map(item => describeState(item, objects)).join(" OR ")})`);
    }
    return required;
  }

  function storedConditionSources(condition, actions, objects) {
    if (condition.type !== "co" || condition.subid || !objects[`co:${condition.id}`]?.internal ||
        !["on", "off"].includes(condition.state)) return [];
    return actions.filter(action => action.kind === "action" && sameObject(action.result, condition) &&
      action.result.command === condition.state &&
      (action.settings?.atcmd !== "false" || action.settings?.atevt !== "false"));
  }

  function describeSourceEvent(item, objects) {
    if (item.type === "fb" && objects[`fb:${item.id}`]?.role === "panel" &&
        ["true", "false"].includes(item.state)) {
      return `${objectName(item, objects)} was ${item.state === "true" ? "activated" : "deactivated"}`;
    }
    return describeState(item, objects, true);
  }

  function describeCommand(result, objects) {
    const name = objectName(result, objects);
    const command = result.command || "(no command)";
    return result.type === "sg" ? `set ${name} to ${command}` : `send command "${command}" to ${name}`;
  }

  function explainAction(action, objects) {
    const result = action.result
      ? describeCommand(action.result, objects)
      : `the action definition "${action.id || "(no ID)"}" is missing`;
    if (action.kind === "route_command") {
      return `${objectName(action.trigger, objects)} includes a route command to ${result}. Route locking and other rules are not shown.`;
    }
    const condition = [describeState(action.trigger, objects, true), ...describedConditions(action, objects)].join(" AND ");
    return `If ${condition}, ${result}.`;
  }

  function signalChains(action, actions, objects) {
    if (action.kind !== "action") return [];
    const internal = item => item?.type === "co" && objects[`co:${item.id}`]?.internal;
    const enabled = item => item.settings?.atcmd !== "false" || item.settings?.atevt !== "false";
    const connects = (first, second) => first.kind === "action" && second.kind === "action" &&
      enabled(first) && enabled(second) && internal(first.result) && sameObject(first.result, second.trigger) &&
      ["on", "off"].includes(first.result.command) &&
      [first.result.command, "any"].includes(second.trigger.state);
    let chains = [];
    if (internal(action.result)) {
      chains = actions.filter(next => next.result?.type === "sg" && connects(action, next)).map(next => [action, next]);
    } else if (internal(action.trigger) && action.result?.type === "sg") {
      chains = actions.filter(previous => connects(previous, action)).map(previous => [previous, action]);
    }
    // shortcut: stop after three internal outputs to bound branching; inspect original relationships for longer chains.
    function expand(chain, seen) {
      const first = chain[0];
      if (!internal(first.trigger) || chain.length >= 4) return [chain];
      const key = `${first.trigger.type}:${first.trigger.id}=${first.trigger.state}`;
      if (seen.has(key)) return [chain];
      const previous = actions.filter(candidate => connects(candidate, first));
      if (!previous.length) return [chain];
      return previous.flatMap(candidate => expand([candidate, ...chain], new Set([...seen, key])));
    }
    return chains.flatMap(chain => expand(chain, new Set()));
  }

  function explainChain(chain, objects) {
    const first = chain[0];
    const initial = [describeState(first.trigger, objects, true), ...describedConditions(first, objects)].join(" AND ");
    const conditions = chain.slice(1).map(step => describedConditions(step, objects)).filter(group => group.length);
    const later = conditions.map(group => `, then if ${group.join(" AND ")}`).join("");
    return `If ${initial}${later}, ${describeCommand(chain[chain.length - 1].result, objects)}.`;
  }

  function expandedFormula(chain) {
    const first = chain[0], last = chain[chain.length - 1];
    const source = `${first.trigger.type}:${first.trigger.id}=${first.trigger.state}`;
    const result = `${last.result.type}:${last.result.id}=${last.result.command || "?"}`;
    const conditions = chain.map((action, index) => {
      const summary = conditionSummary(action);
      return summary ? `(step ${index + 1}: ${summary})` : "";
    }).filter(Boolean);
    return `${source} → ${result} [${chain.map(action => action.id).join(" → ")}]${conditions.length ? ` if ${conditions.join(" AND ")}` : ""}`;
  }

  function relationshipTooltip(action, chains) {
    if (!chains.length) return rocrailFormula(action);
    return [`Original: ${rocrailFormula(action)}`,
      ...chains.map((chain, index) => `Expanded${chains.length > 1 ? ` ${index + 1}` : ""}: ${expandedFormula(chain)}`)].join("\n");
  }

  if (typeof document === "undefined") {
    if (process.argv.includes("--check")) {
      const assert = require("node:assert/strict");
      const action = {
        trigger: {type: "fb", id: "sd06"},
        result: {type: "co", id: "soINi"},
        all_conditions: false,
        conditions: [{type: "sw", id: "sv01", mustbetrue: "true"}, {type: "fb", id: "sd09"}]
      };
      assert.equal(relatedActions([action], {type: "fb", id: "sd06"}).length, 1);
      assert.equal(relatedActions([action], {type: "co", id: "soINi"}).length, 1);
      assert.equal(relatedActions([action], {type: "sw", id: "sv01"}).length, 1);
      assert.equal(relatedActions([action], {type: "sg", id: "sv01"}).length, 0);
      assert.deepEqual(conditionGroups(action), {
        required: [action.conditions[0]], alternatives: [action.conditions[1]]
      });
      assert.equal(conditionGroups({...action, all_conditions: true}).required.length, 2);
      assert.equal(conditionSummary({...action, conditions: [
        {type: "sw", id: "sv01", state: "straight", mustbetrue: "true"},
        {type: "fb", id: "sd09", state: "false"}, {type: "fb", id: "sd13", state: "false"}
      ]}), "sw:sv01=straight AND (fb:sd09=false OR fb:sd13=false)");
      assert.equal(conditionSummary({...action, all_conditions: true,
        conditions: [{type: "fb", id: "id16", state: "true"}]},
        item => item.id === "id16" ? "Til Myra Ut" : `${item.type}:${item.id}`), "Til Myra Ut=true");
      const objects = {
        "fb:yd05": {name: "Myra block 05", role: "track"},
        "fb:id16": {name: "Sigdal Til Myra Ut panel switch", role: "panel"},
        "sw:yv03": {name: "Myra turnout 03"},
        "co:yoP1": {name: "Myra Planovergang 1 output"}
      };
      const crossing = {id: "yoP1on", kind: "action", trigger: {type: "fb", id: "yd05", state: "true"},
        result: {type: "co", id: "yoP1", command: "on"}, all_conditions: true,
        conditions: [{type: "sw", id: "yv03", state: "straight"}]};
      assert.equal(explainAction(crossing, objects),
        'If Myra block 05 is occupied AND Myra turnout 03 is straight, send command "on" to Myra Planovergang 1 output.');
      assert.equal(rocrailFormula(crossing), "fb:yd05=true → co:yoP1=on [yoP1on] if sw:yv03=straight");
      assert.equal(describeState({type: "fb", id: "yd05", state: "false"}, objects), "Myra block 05 is free");
      assert.equal(describeState({type: "fb", id: "id16", state: "true"}, objects), "Sigdal Til Myra Ut panel switch is active");
      assert.equal(describeState({type: "fb", id: "other", state: "true"}, objects), 'Feedback input other has state "true"');
      assert.equal(describeState({type: "sw", id: "yv03", state: "turnout"}, objects), "Myra turnout 03 is diverging");
      assert.equal(describeState({type: "sw", id: "yv03", state: "unknown"}, objects), 'Myra turnout 03 has state "unknown"');
      const alternatives = {...crossing, all_conditions: false, conditions: [
        {type: "sw", id: "yv03", state: "straight", mustbetrue: "true"},
        {type: "fb", id: "yd05", state: "false"}, {type: "fb", id: "id16", state: "true"}
      ]};
      assert.match(explainAction(alternatives, objects), /Myra turnout 03 is straight AND at least one of \(Myra block 05 is free OR Sigdal Til Myra Ut panel switch is active\)/);
      assert.match(rocrailFormula(alternatives), /if sw:yv03=straight AND \(fb:yd05=false OR fb:id16=true\)/);
      const route = {...crossing, kind: "route_command", trigger: {type: "st", id: "r"}, conditions: []};
      assert.match(explainAction(route, objects),
        /^Route r includes a route command/);
      assert.equal(rocrailFormula(route), "st:r (route command) → co:yoP1=on [yoP1on]");
      const flag = {type: "co", id: "ys01ctl"};
      objects["co:ys01ctl"] = {internal: true};
      objects["sg:ys01"] = {name: "Myra signal 01"};
      const first = {id: "ys01ctlOn", kind: "action", trigger: {type: "co", id: "ioUTy", state: "on"},
        result: {...flag, command: "on"}, conditions: [{type: "fb", id: "yd05", state: "true"}], all_conditions: true};
      const second = {id: "ys01yellow", kind: "action", trigger: {...flag, state: "on"},
        result: {type: "sg", id: "ys01", command: "yellow"},
        conditions: [{type: "sw", id: "yv03", state: "straight"}], all_conditions: true};
      assert.equal(explainAction(second, objects),
        "If Output ys01ctl is on AND Myra turnout 03 is straight, set Myra signal 01 to yellow.");
      const off = {...second, id: "ys01red", trigger: {...flag, state: "off"}};
      const records = [first, second, off];
      assert.deepEqual(signalChains(first, records, objects), [[first, second]]);
      assert.deepEqual(signalChains(second, records, objects), [[first, second]]);
      assert.deepEqual(signalChains(off, records, objects), []);
      assert.deepEqual(signalChains({...first, result: {...flag, command: "off"}}, records, objects).map(chain => chain[1].id), ["ys01red"]);
      assert.deepEqual(signalChains(first, [first, {...second, settings: {atcmd: "false", atevt: "false"}}], objects), []);
      assert.equal(signalChains(first, [first, {...second, trigger: {...flag, state: "any"}}], objects).length, 1);
      assert.deepEqual(signalChains(first, records, {}), []);
      assert.deepEqual(signalChains({...first, kind: "route_command"}, records, objects), []);
      assert.equal(explainChain([first, second], objects),
        "If Output ioUTy is on AND Myra block 05 is occupied, then if Myra turnout 03 is straight, set Myra signal 01 to yellow.");
      assert.equal(expandedFormula([first, second]),
        "co:ioUTy=on → sg:ys01=yellow [ys01ctlOn → ys01yellow] if (step 1: fb:yd05=true) AND (step 2: sw:yv03=straight)");
      assert.equal(relationshipTooltip(first, [[first, second]]),
        `Original: ${rocrailFormula(first)}\nExpanded: ${expandedFormula([first, second])}`);
      const either = {...first, all_conditions: false, conditions: alternatives.conditions};
      assert.match(expandedFormula([either, second]), /\(step 1: sw:yv03=straight AND \(fb:yd05=false OR fb:id16=true\)\)/);
      objects["co:ioINy"] = {name: "Sigdal entry from Myra selection", role: "route_selection", internal: true};
      objects["co:ioUTy"] = {name: "Sigdal exit towards Myra selection", role: "route_selection", internal: true};
      objects["sw:iv01"] = {name: "Sigdal turnout 01"};
      const entryOff = {id: "ioINyOff", kind: "action", trigger: {type: "sw", id: "iv01", state: "any"},
        result: {type: "co", id: "ioINy", command: "off"}, conditions: [], all_conditions: true};
      const entryOffFromExit = {...entryOff, trigger: {type: "co", id: "ioUTy", state: "on"},
        conditions: [{type: "co", id: "ioINy", state: "on"}]};
      const exitOn = {id: "ioUTyOn", kind: "action", trigger: {type: "fb", id: "id16", state: "true"},
        result: {type: "co", id: "ioUTy", command: "on"}, conditions: [], all_conditions: true};
      const flagOff = {id: "ys01ctlOff", kind: "action", trigger: {type: "co", id: "ioINy", state: "off"},
        result: {...flag, command: "off"}, conditions: [], all_conditions: true};
      const red = {...off, result: {type: "sg", id: "ys01", command: "red"}, conditions: []};
      const extended = [entryOff, entryOffFromExit, exitOn, flagOff, red];
      const paths = signalChains(red, extended, objects);
      assert.deepEqual(paths, [[entryOff, flagOff, red], [exitOn, entryOffFromExit, flagOff, red]]);
      assert.equal(explainChain(paths[0], objects),
        "If Sigdal turnout 01 receives any event, set Myra signal 01 to red.");
      assert.equal(explainChain(paths[1], objects),
        "If Sigdal Til Myra Ut panel switch is active, then if Sigdal entry from Myra selection is active, set Myra signal 01 to red.");
      assert.equal(expandedFormula(paths[1]),
        "fb:id16=true → sg:ys01=red [ioUTyOn → ioINyOff → ys01ctlOff → ys01red] if (step 2: co:ioINy=on)");
      const cycle = {...entryOff, id: "cycle", trigger: {type: "co", id: "ioINy", state: "off"}};
      assert.ok(signalChains(red, [...extended, cycle], objects).every(path => path.length <= 4));
      objects["fb:id17"] = {name: "Sigdal Inn fra Myra panel switch", role: "panel"};
      const entryOn = {id: "ioINyOn", kind: "action", trigger: {type: "fb", id: "id17", state: "true"},
        result: {type: "co", id: "ioINy", command: "on"}, conditions: [], all_conditions: true};
      const stored = {type: "co", id: "ioINy", state: "on"};
      assert.deepEqual(storedConditionSources(stored, [...extended, entryOn], objects), [entryOn]);
      assert.equal(describeSourceEvent(entryOn.trigger, objects), "Sigdal Inn fra Myra panel switch was activated");
      assert.equal(describeSourceEvent({...entryOn.trigger, state: "false"}, objects), "Sigdal Inn fra Myra panel switch was deactivated");
      assert.deepEqual(storedConditionSources({...stored, state: "unknown"}, [...extended, entryOn], objects), []);
      assert.deepEqual(storedConditionSources({...stored, subid: "other"}, [...extended, entryOn], objects), []);
      assert.deepEqual(storedConditionSources(stored, [...extended, entryOn], {}), []);
      console.log("Dependency inspector checks passed.");
    }
    return;
  }

  const data = JSON.parse(document.getElementById("dependency-data").textContent);
  const toggle = document.getElementById("dependency-toggle");
  const inspector = document.getElementById("dependency-inspector");
  const breadcrumbs = document.getElementById("dependency-breadcrumbs");
  const status = document.getElementById("dependency-status");
  const details = document.getElementById("dependency-details");
  const groups = [...document.querySelectorAll('g[data-kind="sw"], g[data-kind="sg"], g[data-kind="fb"], g[data-kind="bk"], g[data-kind="co"]')];
  const panels = [...document.querySelectorAll("[data-panel-select]")];
  const originalAttributes = new WeakMap(groups.map(group => [group, {
    role: group.getAttribute("role"), tabindex: group.getAttribute("tabindex"),
    label: group.getAttribute("aria-label")
  }]));
  let history = [];
  let activeItem = null;
  let chosenAction = null;

  function rocrailName(item) {
    return `${item.type || "unknown"}:${item.id || "(no ID)"}`;
  }

  function shown(item) {
    return groups.some(group => sameObject({type: group.dataset.kind, id: group.dataset.id}, item)) ||
      (item.type === "fb" && panels.some(panel => panel.dataset.panelSelect === item.id));
  }

  function objectLink(item, select = () => inspect(item)) {
    const wrapper = document.createElement("span");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "dependency-link";
    button.textContent = objectName(item, data.objects);
    button.title = rocrailName(item);
    button.setAttribute("aria-label", `${objectName(item, data.objects)} (Rocrail: ${rocrailName(item)})`);
    button.disabled = !item.type || !item.id;
    button.addEventListener("click", select);
    wrapper.append(button);
    if (!shown(item)) {
      const locations = data.drawing_locations[item.type]?.[item.id] || [];
      if (locations.length) {
        wrapper.append(" (See ");
        locations.forEach((location, index) => {
          if (index) wrapper.append(", ");
          const link = document.createElement("a");
          link.href = location.file;
          link.textContent = location.name;
          wrapper.append(link);
        });
        wrapper.append(")");
      } else {
        wrapper.append(" (not shown in any drawing)");
      }
    }
    return wrapper;
  }

  function clearHighlights() {
    document.querySelectorAll(".dependency-selected, .dependency-reference").forEach(element =>
      element.classList.remove("dependency-selected", "dependency-reference"));
  }

  function highlight(items, className) {
    groups.forEach(group => {
      if (items.some(item => sameObject(item, {type: group.dataset.kind, id: group.dataset.id})))
        group.classList.add(className);
    });
    panels.forEach(panel => {
      if (items.some(item => sameObject(item, {type: "fb", id: panel.dataset.panelSelect})))
        panel.classList.add(className);
    });
  }

  function renderHighlights(action) {
    clearHighlights();
    if (action) {
      const linked = signalChains(action, data.actions, data.objects).flatMap(chain =>
        chain.flatMap(step => [step.trigger, step.result, ...step.conditions]));
      highlight([action.trigger, action.result, ...action.conditions, ...linked].filter(Boolean), "dependency-reference");
    }
    if (activeItem) highlight([activeItem], "dependency-selected");
  }

  function conditionText(condition) {
    const parts = [];
    if (condition.state) parts.push(` = ${condition.state}`);
    if (condition.subid) parts.push(` (subid: ${condition.subid})`);
    return parts.join("");
  }

  function addConditionList(parent, title, conditions) {
    if (!conditions.length) return;
    const heading = document.createElement("strong");
    heading.textContent = title;
    parent.append(heading);
    const list = document.createElement("ul");
    conditions.forEach(condition => {
      const row = document.createElement("li");
      row.append(objectLink(condition), document.createTextNode(conditionText(condition)));
      list.append(row);
    });
    parent.append(list);
  }

  function renderAction(action, container) {
    container.replaceChildren();
    container.hidden = !action;
    chosenAction = action;
    renderHighlights(action);
    if (!action) return;
    const chains = signalChains(action, data.actions, data.objects);
    const heading = document.createElement("h3");
    heading.textContent = chains.length ? "Possible explanations" : "Explanation";
    container.append(heading);
    if (chains.length) {
      const note = document.createElement("p");
      note.className = "dependency-note";
      note.textContent = "Possible signal effects through up to three internal outputs. Conditions are checked at each step; timing and other Rocrail rules may affect execution.";
      container.append(note);
    }
    const descriptions = chains.length ? chains.map(chain => explainChain(chain, data.objects)) : [explainAction(action, data.objects)];
    descriptions.forEach((text, index) => {
      const explanation = document.createElement("div");
      explanation.className = "dependency-explanation";
      explanation.title = relationshipTooltip(action, chains.length ? [chains[index]] : []);
      const sentence = document.createElement("p");
      sentence.textContent = text;
      explanation.append(sentence);
      const steps = chains.length ? chains[index] : [action];
      const seen = new Set();
      steps.flatMap(step => step.conditions).forEach(condition => {
        const key = `${condition.type}:${condition.id}=${condition.state}`;
        if (seen.has(key)) return;
        seen.add(key);
        const sources = storedConditionSources(condition, data.actions, data.objects);
        if (!sources.length) return;
        const context = document.createElement("details");
        context.className = "dependency-state-context";
        const label = document.createElement("summary");
        label.textContent = `Stored condition: ${describeState(condition, data.objects)}.`;
        const introduction = document.createElement("p");
        introduction.textContent = "Configured events that can set this state:";
        const list = document.createElement("ul");
        sources.forEach(source => {
          const item = document.createElement("li");
          item.textContent = [describeSourceEvent(source.trigger, data.objects),
            ...describedConditions(source, data.objects)].join(" AND ");
          item.title = rocrailFormula(source);
          list.append(item);
        });
        const note = document.createElement("p");
        note.textContent = "The state can remain set after the triggering event.";
        context.append(label, introduction, list, note);
        explanation.append(context);
      });
      container.append(explanation);
    });
    const original = chains.length ? document.createElement("details") : document.createElement("div");
    if (chains.length) {
      const summary = document.createElement("summary");
      summary.textContent = "Original relationship and code";
      original.append(summary);
      container.append(original);
      const expanded = document.createElement("details");
      const expandedTitle = document.createElement("summary");
      expandedTitle.textContent = "Expanded Rocrail formulas";
      const formulas = document.createElement("pre");
      formulas.textContent = relationshipTooltip(action, chains);
      expanded.append(expandedTitle, formulas);
      container.append(expanded);
    } else {
      container.append(original);
    }
    const trigger = document.createElement("p");
    const triggerLabel = document.createElement("strong");
    triggerLabel.textContent = action.kind === "route_command" ? "Route: " : "Trigger: ";
    trigger.append(triggerLabel, objectLink(action.trigger));
    if (action.kind !== "route_command") trigger.append(` = ${action.trigger.state}`);
    const result = document.createElement("p");
    const resultLabel = document.createElement("strong");
    resultLabel.textContent = "Result: ";
    result.append(resultLabel);
    if (action.result) {
      result.append(objectLink(action.result), ` → ${action.result.command || "(no command)"}`);
    } else {
      result.append(`Action definition ${action.id || "(no ID)"} is missing from the XML.`);
    }
    original.append(trigger, result);
    const conditions = conditionGroups(action);
    if (!action.conditions.length) {
      const none = document.createElement("p");
      none.textContent = action.kind === "route_command"
        ? "No conditions on this route command; route locking rules are not shown."
        : "Conditions: none.";
      original.append(none);
    } else {
      addConditionList(original, "All required:", conditions.required);
      addConditionList(original, "At least one of:", conditions.alternatives);
    }
    if (Object.keys(action.settings).length) {
      const settings = document.createElement("p");
      settings.textContent = "Additional XML settings: " +
        Object.entries(action.settings).map(([key, value]) => `${key}=${value}`).join(", ");
      original.append(settings);
    }
    const code = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Rocrail code details";
    const source = document.createElement("pre");
    source.textContent = JSON.stringify(chains.length ? {original: action, possible_chains: chains} : action, null, 2);
    code.append(summary, source);
    original.append(code);
  }

  function render() {
    breadcrumbs.replaceChildren();
    if (history.length) breadcrumbs.append("Navigation: ");
    history.forEach((item, index) => {
      if (index) breadcrumbs.append(" › ");
      breadcrumbs.append(objectLink(item, () => inspect(item, index)));
    });
    details.replaceChildren();
    const matches = relatedActions(data.actions, activeItem);
    status.textContent = `${objectName(activeItem, data.objects)}: ${matches.length} directly related relationship${matches.length === 1 ? "" : "s"}.`;
    status.title = rocrailName(activeItem);
    const sensors = activeItem.type === "bk" ? data.block_detectors[activeItem.id] || [] : [];
    if (sensors.length) {
      const block = document.createElement("p");
      block.append("Linked detectors: ");
      sensors.forEach((id, index) => {
        if (index) block.append(", ");
        block.append(objectLink({type: "fb", id}));
      });
      details.append(block);
    }
    if (matches.length) {
      const label = document.createElement("label");
      label.className = "dependency-select-label";
      const labelText = document.createElement("span");
      labelText.textContent = "Choose a relationship:";
      label.append(labelText);
      const select = document.createElement("select");
      select.setAttribute("aria-label", "Related actions and route commands");
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Select an action or route command";
      select.append(placeholder);
      matches.forEach((action, index) => {
        const option = document.createElement("option");
        option.value = String(index);
        const chains = signalChains(action, data.actions, data.objects);
        option.textContent = chains.length
          ? `${explainChain(chains[0], data.objects)}${chains.length > 1 ? ` (+${chains.length - 1} other possible effects)` : ""}`
          : explainAction(action, data.objects);
        option.title = relationshipTooltip(action, chains);
        select.append(option);
      });
      label.append(select);
      const actionDetails = document.createElement("div");
      actionDetails.className = "dependency-action-details";
      actionDetails.hidden = true;
      actionDetails.setAttribute("aria-live", "polite");
      select.addEventListener("change", () => {
        select.title = select.selectedOptions[0].title;
        renderAction(select.value === "" ? null : matches[Number(select.value)], actionDetails);
      });
      details.append(label, actionDetails);
    }
    chosenAction = null;
    renderHighlights(null);
  }

  function inspect(item, historyIndex) {
    if (historyIndex !== undefined) history = history.slice(0, historyIndex + 1);
    else if (!sameObject(history[history.length - 1], item)) history.push({type: item.type, id: item.id});
    activeItem = {type: item.type, id: item.id};
    render();
  }

  function restoreAttribute(element, name, value) {
    if (value === null) element.removeAttribute(name);
    else element.setAttribute(name, value);
  }

  toggle.addEventListener("click", () => {
    const active = toggle.getAttribute("aria-pressed") !== "true";
    toggle.setAttribute("aria-pressed", String(active));
    inspector.hidden = !active;
    document.body.classList.toggle("dependency-mode", active);
    groups.forEach(group => {
      if (active) {
        group.setAttribute("role", "button");
        group.setAttribute("tabindex", "0");
        group.setAttribute("aria-label", `Inspect ${group.dataset.id} dependencies`);
      } else {
        const original = originalAttributes.get(group);
        restoreAttribute(group, "role", original.role);
        restoreAttribute(group, "tabindex", original.tabindex);
        restoreAttribute(group, "aria-label", original.label);
      }
    });
    if (!active) clearHighlights();
    else renderHighlights(chosenAction);
  });

  function inspectEvent(event) {
    if (toggle.getAttribute("aria-pressed") !== "true") return;
    if (event.type === "keydown" && !["Enter", " "].includes(event.key)) return;
    const panel = event.target.closest("[data-panel-select]");
    const group = event.target.closest('g[data-kind="sw"], g[data-kind="sg"], g[data-kind="fb"], g[data-kind="bk"], g[data-kind="co"]');
    if (!panel && !group) return;
    event.preventDefault();
    event.stopPropagation();
    history = [];
    inspect(panel ? {type: "fb", id: panel.dataset.panelSelect} : {type: group.dataset.kind, id: group.dataset.id});
    const bounds = inspector.getBoundingClientRect();
    if (bounds.top < 0 || bounds.bottom > window.innerHeight)
      inspector.scrollIntoView({block: "nearest", inline: "nearest"});
  }

  document.addEventListener("click", inspectEvent, true);
  document.addEventListener("keydown", inspectEvent, true);
})();

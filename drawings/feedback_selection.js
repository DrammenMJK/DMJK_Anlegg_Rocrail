(() => {
  function feedbackTargets(inputs) {
    return new Set(inputs.flatMap(input => [input.id, ...input.related]));
  }

  function panelMatches(panel, ids) {
    return ids.has(panel.dataset.panel) || (panel.dataset.feedbackIds || "").split(" ").some(id => ids.has(id));
  }

  function panelInputs(ids, inputs) {
    return inputs.filter(input => ids.includes(input.id)).map(input => ({
      id: input.id,
      related: [...new Set([...input.turnout_feedback, ...input.action_turnouts.checked, ...input.action_turnouts.commanded])]
    }));
  }

  function panelName(id, panels) {
    const panel = panels.find(item => item.dataset.panelSelect === id || item.dataset.panel === id);
    return panel?.dataset.displayName || panel?.textContent || id;
  }

  function tooltipOffset(anchor, width, left, right) {
    return Math.max(left - anchor, Math.min(0, right - anchor - width));
  }

  if (typeof document === "undefined") {
    if (process.argv.includes("--check")) {
      const assert = require("node:assert/strict");
      const ids = feedbackTargets([{id: "sd06", related: ["s1", "sv01"]}, {id: "sd07", related: []}]);
      assert.deepEqual([...ids], ["sd06", "s1", "sv01", "sd07"]);
      assert(panelMatches({dataset: {panel: "sd06"}}, ids));
      assert(panelMatches({dataset: {feedbackIds: "sd05 sd06"}}, ids));
      assert(!panelMatches({dataset: {panel: "sd08"}}, ids));
      assert.deepEqual(panelInputs(["sd06"], [
        {id: "sd06", turnout_feedback: ["sv03"], action_turnouts: {checked: ["sv01"], commanded: ["sv01", "sv02"]}},
        {id: "sd07", turnout_feedback: [], action_turnouts: {checked: [], commanded: []}}
      ]), [{id: "sd06", related: ["sv03", "sv01", "sv02"]}]);
      assert.equal(panelName("id16", [{dataset: {panelSelect: "id16"}, textContent: "Til Myra Ut"}]), "Til Myra Ut");
      assert.equal(panelName("id16", [{dataset: {panelSelect: "id16", displayName: "Til Myra Ut"}, textContent: "⚠ Til Myra Ut"}]), "Til Myra Ut");
      assert.equal(panelName("id17", []), "id17");
      assert.equal(tooltipOffset(40, 300, 24, 700), 0);
      assert.equal(tooltipOffset(500, 300, 24, 700), -100);
      assert.equal(tooltipOffset(-20, 300, 24, 700), 44);
      assert.equal(tooltipOffset(40, 676, 24, 700), -16);
      console.log("Feedback selection checks passed.");
    }
    return;
  }

  const modules = [...document.querySelectorAll(".feedback-module")];
  const detectors = [...document.querySelectorAll("g.feedback-detector")];
  const groups = [...document.querySelectorAll("g[data-id][data-kind]")];
  const panels = [...document.querySelectorAll("[data-panel], [data-feedback-ids]")];
  const allInputs = modules.flatMap(module => JSON.parse(module.dataset.moduleInputs));
  const status = document.querySelector(".feedback-selection-status");
  let selected = null;

  function positionTooltip(module) {
    const tooltip = module.querySelector(".feedback-tooltip");
    const frame = module.closest(".canvas").getBoundingClientRect();
    const left = Math.max(0, frame.left) + 4;
    const right = Math.min(window.innerWidth, frame.right) - 4;
    tooltip.style.maxWidth = `${Math.max(0, Math.min(600, right - left))}px`;
    const anchor = module.getBoundingClientRect().left + module.clientLeft;
    tooltip.style.left = `${tooltipOffset(anchor, tooltip.getBoundingClientRect().width, left, right)}px`;
  }

  function positionVisibleTooltips() {
    modules.filter(module => module.matches(":hover, :focus-within") &&
      !module.classList.contains("tooltip-dismissed")).forEach(positionTooltip);
  }

  window.addEventListener("resize", positionVisibleTooltips);
  window.addEventListener("scroll", positionVisibleTooltips);
  document.querySelectorAll(".canvas").forEach(frame => frame.addEventListener("scroll", positionVisibleTooltips));

  document.querySelectorAll(".module-group-button").forEach(button => {
    button.addEventListener("click", () => {
      const open = button.getAttribute("aria-expanded") !== "true";
      document.querySelectorAll(".module-group-button").forEach(other => {
        const active = open && other === button;
        other.setAttribute("aria-expanded", String(active));
        document.getElementById(other.getAttribute("aria-controls")).hidden = !active;
      });
      if (selected && selected.startsWith("module:")) selectFeedback(selected, []);
    });
  });

  function selectFeedback(key, inputs, scrollToObject = false) {
    const next = selected === key ? null : key;
    if (status) status.title = "";
    document.querySelectorAll(".feedback-highlight, .feedback-panel-highlight").forEach(element => {
      element.classList.remove("feedback-highlight", "feedback-panel-highlight");
    });
    modules.forEach(module => module.setAttribute("aria-pressed", String(`module:${module.dataset.moduleName}` === next)));
    detectors.forEach(detector => detector.setAttribute("aria-pressed", String(`detector:${detector.dataset.id}` === next)));
    selected = next;
    if (!selected) {
      if (status) status.textContent = "";
      return;
    }

    const ids = feedbackTargets(inputs);
    const matchingGroups = groups.filter(group => ids.has(group.dataset.id));
    const matchingPanels = panels.filter(panel => panelMatches(panel, ids));
    matchingGroups.forEach(group => group.classList.add("feedback-highlight"));
    matchingPanels.forEach(panel => panel.classList.add("feedback-panel-highlight"));
    if (status) {
      const count = matchingGroups.length + matchingPanels.length;
      const missing = inputs.filter(input => {
        const targets = feedbackTargets([input]);
        return !matchingGroups.some(group => targets.has(group.dataset.id)) &&
          !matchingPanels.some(panel => panelMatches(panel, targets));
      }).length;
      const note = missing ? ` ${missing} input${missing === 1 ? "" : "s"} not shown in this drawing.` : "";
      status.textContent = count
        ? `${key.split(":").slice(1).join(":")}: ${count} shown in blue.${note}`
        : `${key.split(":").slice(1).join(":")}: no matching objects are shown in this drawing.`;
    }
    if (scrollToObject && matchingGroups.length) {
      const target = matchingGroups.find(group => group.dataset.kind === "fb") || matchingGroups[0];
      target.scrollIntoView({block: "nearest", inline: "nearest"});
    }
  }

  modules.forEach(module => {
    const select = () => selectFeedback(`module:${module.dataset.moduleName}`, JSON.parse(module.dataset.moduleInputs), true);
    module.addEventListener("click", event => {
      module.classList.add("tooltip-dismissed");
      if (!event.target.closest(".feedback-tooltip")) select();
      module.blur();
    });
    module.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        module.classList.add("tooltip-dismissed");
        select();
      }
    });
    module.addEventListener("mouseleave", () => module.classList.remove("tooltip-dismissed"));
    module.addEventListener("mouseenter", () => positionTooltip(module));
    module.addEventListener("focus", () => {
      module.classList.remove("tooltip-dismissed");
      positionTooltip(module);
    });
  });
  function selectPanel(ids) {
    const key = `panel:${ids.join(", ")}`;
    const inputs = panelInputs(ids, allInputs);
    selectFeedback(key, inputs, true);
    if (selected !== key || !status) return;
    const turnouts = new Set(inputs.flatMap(input => input.related));
    const shown = groups.filter(group => group.dataset.kind === "sw" && turnouts.has(group.dataset.id)).length;
    const names = ids.map(id => panelName(id, panels)).join(", ");
    status.title = ids.map(id => `fb:${id}`).join(", ");
    status.textContent = turnouts.size
      ? `${names}: ${shown} of ${turnouts.size} possible turnouts shown (feedback, checks or commands; conditions not evaluated).`
      : `${names}: no related turnout feedback, checks or commands found in the XML.`;
  }

  document.querySelectorAll("[data-panel-select], [data-panel]").forEach(panel => {
    panel.addEventListener("click", () => selectPanel([panel.dataset.panelSelect || panel.dataset.panel]));
  });
  const direction = document.querySelector("#direction[data-feedback-ids]");
  if (direction) {
    direction.addEventListener("change", () => selectPanel(direction.dataset.feedbackIds.split(" ")));
  }
  detectors.forEach(detector => {
    const select = () => {
      const id = detector.dataset.id;
      selectFeedback(`detector:${id}`, [allInputs.find(input => input.id === id) || {id, related: []}]);
    };
    detector.addEventListener("click", select);
    detector.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  });
})();

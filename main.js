// Browser entry point. Collection keys identify species and regional forms.
import { decodeCollection as decodeOwnership, encodeCollection, assignCapture } from "./collection-codec.js";
const $ = (selector) => document.querySelector(selector);

async function read(file) {
  const response = await fetch(file);
  if (!response.ok) throw Error(`Cannot load ${file}`);
  return response.json();
}

const data = await read("./data.json");
const homeData = data.filter(p => !p.formUnspecified);
const hunts = await read("./hunts.json");
const byKey = new Map(data.map((pokemon) => [pokemon.key, pokemon]));
const bySpecies = new Map();
for (const p of data) {
  if (!bySpecies.has(p.id)) bySpecies.set(p.id, []);
  bySpecies.get(p.id).push(p);
}
const chosenForms = new Map();
const openForms = new Set();
let assigningForm = false;

// Save captures and shinies separately; every shiny must also be captured.
const storageKey = "shinydex-collection-v2";
let captured = new Set();
let shinies = new Set();
let futureCaptured = new Set();
let futureShinies = new Set();
let selected = null;
let mode = "auto";
let view = "dex";
let box = 1;

function valid(ids) {
  if (!Array.isArray(ids)) throw Error("Invalid collection");
  return new Set(ids.filter((id) => Number.isInteger(id) && byKey.has(id)));
}

// Validate the whole record before replacing either part of the collection.
// This keeps malformed saved data from leaving a partially applied state.
function decodeCollection(collection) {
  return decodeOwnership(collection, byKey);
}

function collectionRecord() {
  return encodeCollection({ captured, shinies, futureCaptured, futureShinies });
}

try {
  const saved = window.shinydexDesktop
    ? await window.shinydexDesktop.loadCollection()
    : localStorage.getItem(storageKey);
  if (saved) {
    const collection = JSON.parse(saved);
    ({ captured, shinies, futureCaptured, futureShinies } = decodeCollection(collection));
  } else {
    // The previous format tracked only shinies; those are also normal captures.
    shinies = valid(
      JSON.parse(localStorage.getItem("shinydex-caught-v1") || "[]"),
    );
    captured = new Set(shinies);
  }
  shinies.forEach((id) => captured.add(id));
} catch {
  $("#save").textContent = "Storage unavailable — export a backup";
}

const num = (id) => String(id).padStart(4, "0"),
  name = (p) => p.displayName;
const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
// HOME and collection views show owned forms; preview mode affects the Pokédex only.
const isShiny = (p) =>
  view === "home" || view === "collection"
    ? shinies.has(p.key)
    : mode === "shiny" || (mode === "auto" && shinies.has(p.key));
const image = (p, eager = false) => {
  const shinyArt = isShiny(p) && p.shinyArtworkAvailable !== false;
  return `<img loading="${eager ? "eager" : "lazy"}" src="${shinyArt ? p.shiny : p.normal}" alt="${shinyArt ? "Shiny" : "Normal"} ${esc(name(p))}${isShiny(p) && !shinyArt ? ' · separate shiny artwork unavailable' : ''}" data-image>`;
};
function check(p, kind) {
  const shiny = kind === "shiny",
    checked = (shiny ? shinies : captured).has(p.key);
  const blocked = !checked && (p.formUnspecified || (shiny && p.shinyLocked));
  return `<label class="catch ${shiny ? "shiny-check" : "captured-check"}" title="${p.formUnspecified && !checked ? "Choose a concrete form to record a new capture" : shiny && p.shinyLocked ? "This form is shiny-locked" : shiny ? "Shiny captured" : "Captured"}"><input type="checkbox" data-kind="${kind}" data-catch="${p.key}" aria-label="${esc(name(p))} ${shiny ? "shiny captured" : "captured"}" ${checked ? "checked" : ""} ${blocked ? "disabled" : ""}><span>${shiny ? "✧" : "✓"}</span></label>`;
}
function matches(p) {
  const q = $("#search").value.toLowerCase().trim().replace(/^#/, ""),
    s = $("#status").value;
  return (
    (!q || name(p).toLowerCase().includes(q) || num(p.id).includes(q)) &&
    (!$("#generation").value ||
      p.generation === Number($("#generation").value)) &&
    (s === "all" ||
      (s === "captured" && captured.has(p.key)) ||
      (s === "missing-captured" && !captured.has(p.key)) ||
      (s === "shiny" && shinies.has(p.key)) ||
      (s === "missing-shiny" && !shinies.has(p.key)))
  );
}
// Positions come from the full catalog, so filtering never shifts HOME slots.
function position(p) {
  if (p.formUnspecified) return null;
  const slot = p.position % 30;
  return {
    box: Math.floor(p.position / 30) + 1,
    row: Math.floor(slot / 6) + 1,
    column: (slot % 6) + 1,
  };
}
[
  "Kanto",
  "Johto",
  "Hoenn",
  "Sinnoh",
  "Unova",
  "Kalos",
  "Alola",
  "Galar / Hisui",
  "Paldea",
].forEach((r, i) =>
  $("#generation").add(new Option(`Gen ${i + 1} · ${r}`, i + 1)),
);
for (let b = 1; b <= Math.ceil(homeData.length / 30); b++) {
  const first = homeData[(b - 1) * 30],
    last = homeData[Math.min(b * 30 - 1, homeData.length - 1)];
  $("#box-select").add(
    new Option(
      `Box ${String(b).padStart(2, "0")} · #${num(first.id)}–${num(last.id)}`,
      b,
    ),
  );
}
function stats() {
  const caughtTotal = homeData.filter(p => captured.has(p.key)).length;
  const shinyTotal = homeData.filter(p => shinies.has(p.key)).length;
  const pending = data.filter(p => p.formUnspecified && captured.has(p.key)).length;
  $("#unassigned-summary").textContent = pending ? `${pending} saved captures need a form assignment. Choose a form in the Pokédex to assign them; they are preserved in your backup.` : "";
  $("#captured-total").innerHTML =
    `${caughtTotal.toLocaleString()} <em>/ ${homeData.length.toLocaleString()}</em>`;
  $("#total").innerHTML =
    `${shinyTotal} <em>/ ${homeData.length.toLocaleString()}</em>`;
  const pc = (shinyTotal / homeData.length) * 100;
  const capturedPc = (caughtTotal / homeData.length) * 100;
  $("#captured-progress").style.width = capturedPc + "%";
  $("#captured-percent").textContent =
    `${capturedPc.toFixed(1)}% captured complete`;
  $("#progress").style.width = pc + "%";
  $("#percent").textContent =
    `${pc.toFixed(1)}% shiny complete`;
  $("#collection-count").textContent = shinies.size;
}
function detail() {
  if (selected === null) {
    $("#detail").innerHTML = '<div class="detail-top">POKÉMON DATA</div><div class="selection-prompt"><h2>Choose a Pokémon</h2><p>Select a Pokémon to see its data and hunting methods.</p></div>';
    return;
  }
  const p = byKey.get(selected),
    loc = position(p) || { box: "—", row: "—", column: "—" };
  $("#detail").innerHTML =
    `<div class="detail-top"><span>POKÉMON DATA</span><button id="close-selection" aria-label="Close Pokémon details">✕</button></div><div class="hero-image">${isShiny(p) ? '<span class="shiny-badge">✧ SHINY FORM</span>' : ""}${image(p, true)}<div class="orbit"></div></div><div class="detail-info"><div class="eyebrow">NATIONAL № ${num(p.id)}${p.formLabel ? " · " + esc(p.formLabel) : ""}</div><h2>${esc(p.speciesName)}</h2><div class="types">${p.types.map((t) => `<span class="type ${t}">${t}</span>`).join("")}</div><div class="measure"><div><small>HEIGHT</small><strong>${(p.height / 10).toFixed(1)} <em>m</em></strong></div><div><small>WEIGHT</small><strong>${(p.weight / 10).toFixed(1)} <em>kg</em></strong></div><div><small>GENERATION</small><strong>${p.generation}</strong></div></div><div class="detail-checks"><div>${check(p, "captured")}<span>Captured</span></div><div>${check(p, "shiny")}<span>Shiny captured</span></div></div><p class="auto-note">Each change saves automatically. Shiny captured also marks Captured.</p><button id="locate" class="location">▦ &nbsp; Box ${loc.box} · Row ${loc.row}, Column ${loc.column} <span>↗</span></button><a class="source-link" target="_blank" rel="noreferrer" href="${p.source}">View on Bulbapedia ↗</a></div>`;
}
function formGallery(p) {
  const forms = bySpecies.get(p.id).filter(f => f.formLabel !== "Gender unspecified");
  if (forms.length === 1 && (forms[0].formLabel || "Standard") === "Standard") return "";
  const open = openForms.has(p.id);
  return `<div class="form-gallery ${open ? "is-open" : ""}" id="forms-${p.id}" ${open ? "" : 'inert aria-hidden="true"'}><div class="form-gallery-clip"><div class="form-grid">${open ? forms.map(f => `<button class="form-choice ${f.key === p.key ? "active" : ""}" data-choose-form="${f.key}" aria-label="${esc(name(f))}" aria-pressed="${f.key === p.key}">${image(f)}<strong>${esc(f.formLabel || "Standard")}</strong><span class="form-ownership">${captured.has(f.key) ? "✓ Captured" : ""}${shinies.has(f.key) ? " · ✧ Shiny" : ""}</span></button>`).join("") : ""}</div></div></div>`;
}
function list() {
  const items = listItems();
  $("#result-count").textContent = `${items.length.toLocaleString()} entries`;
  $("#list").innerHTML = items.length
    ? items.map(p => {
      const forms = bySpecies.get(p.id).filter(f => f.formLabel !== "Gender unspecified");
      const hasForms = forms.length > 1 || (forms[0].formLabel || "Standard") !== "Standard";
      return `<div class="species-entry"><div class="row ${p.key === selected ? "selected" : ""} ${captured.has(p.key) ? "is-captured" : ""}" data-row="${p.key}"><button class="row-select" data-select="${p.key}"><span class="number">${num(p.id)}</span>${image(p)}<strong>${esc(p.speciesName)}</strong></button>${hasForms ? `<button class="form-toggle" data-toggle-forms="${p.id}" aria-label="${esc(p.speciesName)} forms" aria-expanded="${openForms.has(p.id)}" aria-controls="forms-${p.id}"><span aria-hidden="true">↳</span></button>` : ""}<div class="row-checks">${check(p, "captured")}${check(p, "shiny")}</div></div>${formGallery(p)}</div>`;
    }).join("")
    : '<div class="empty">No Pokémon found. Try another name or filter.</div>';
}
function assignmentControl() {
  const p = byKey.get(selected);
  if (!p) return;
  if (p.shinyLocked) {
    $("#detail .detail-info").insertAdjacentHTML("beforeend", `<p class="auto-note">This form is shiny-locked. <a href="${esc(p.shinyLockSource)}" target="_blank" rel="noreferrer">Source</a></p>`);
  }
  if (p.shinyArtworkAvailable === false && isShiny(p)) {
    $("#detail .detail-info").insertAdjacentHTML("beforeend", '<p class="auto-note">Separate shiny artwork is unavailable for this form. Its normal artwork is shown; ownership remains recorded separately.</p>');
  }
  if (p.formUnspecified) {
    $("#locate").outerHTML = '<p class="auto-note">Select a concrete form to find its HOME slot. This unspecified record preserves your earlier capture.</p>';
  }
  if (p.livingForm && p.legacyKey && captured.has(p.legacyKey)) {
    $("#detail .detail-info").insertAdjacentHTML("beforeend",
      `<p class="auto-note">A saved capture has an unspecified form. Assign it to ${esc(p.formLabel)} after saving a backup.</p><button id="assign-form" ${assigningForm ? "disabled" : ""}>Assign saved capture to this form</button>`);
  }
}
async function assignSelectedForm() {
  if (assigningForm) return;
  const p = byKey.get(selected);
  if (!p.livingForm || !p.legacyKey) return;
  if (p.shinyLocked && shinies.has(p.legacyKey)) {
    $("#save").textContent = "Cannot assign a shiny capture to a shiny-locked form. Choose another form or correct the old shiny record first.";
    return;
  }
  assigningForm = true;
  document.querySelectorAll("input[data-catch], .form-choice, #assign-form").forEach(el => el.disabled = true);
  try {
    const previous = collectionRecord();
    const next = assignCapture(previous, p.legacyKey, p.key);
    if (window.shinydexDesktop) {
      await window.shinydexDesktop.backupCollection();
      await window.shinydexDesktop.saveCollection(next);
    } else {
      const backupKey = `shinydex-before-form-assignment-v2-${Date.now()}-${crypto.randomUUID()}`;
      localStorage.setItem(backupKey, JSON.stringify(previous));
      localStorage.setItem(storageKey, JSON.stringify(next));
    }
    ({ captured, shinies, futureCaptured, futureShinies } = decodeCollection(next));
    $("#save").textContent = "✓ Form assigned · backup saved";
  } catch {
    $("#save").textContent = "Form not assigned — backup or save failed";
  } finally {
    assigningForm = false;
    render();
    refreshAssignmentBackups();
  }
}
function refreshAssignmentBackups() {
  if (window.shinydexDesktop) return;
  const panel = $("#assignment-backups");
  if (!panel) return;
  const select = panel.querySelector("select");
  select.replaceChildren();
  try {
    const keys = Array.from({ length: localStorage.length }, (_, i) => localStorage.key(i))
      .filter(key => key?.startsWith("shinydex-before-form-assignment-v2-"))
      .sort().reverse();
    for (const key of keys) {
      try {
        const record = JSON.parse(localStorage.getItem(key));
        decodeCollection(record);
        const timestamp = Number(key.slice("shinydex-before-form-assignment-v2-".length).split("-")[0]);
        select.add(new Option(`${new Date(timestamp).toLocaleString()} · ${record.captured.length} captures`, key));
      } catch { /* A malformed backup never becomes a restore choice. */ }
    }
    panel.hidden = !select.options.length;
  } catch {
    panel.hidden = true;
  }
}
function restoreAssignmentBackup() {
  if (assigningForm || window.shinydexDesktop) return;
  try {
    const key = $("#assignment-backups select").value;
    if (!key.startsWith("shinydex-before-form-assignment-v2-")) throw Error("Invalid backup selection");
    const record = JSON.parse(localStorage.getItem(key));
    const restored = decodeCollection(record);
    const current = collectionRecord();
    // Preserve the current collection before replacing it with the selected backup.
    localStorage.setItem(`shinydex-before-form-assignment-v2-${Date.now()}-${crypto.randomUUID()}`, JSON.stringify(current));
    localStorage.setItem(storageKey, JSON.stringify(encodeCollection(restored)));
    ({ captured, shinies, futureCaptured, futureShinies } = restored);
    render();
    refreshAssignmentBackups();
    $("#save").textContent = "✓ Assignment backup restored · current collection backed up";
  } catch {
    $("#save").textContent = "Backup not restored — invalid backup or storage unavailable";
  }
}
function listItems() {
  return [...bySpecies.values()].map(forms => {
    const matching = forms.filter(matches);
    return matching.find(p => p.key === chosenForms.get(forms[0].id)) ||
      matching.find(p => p.formUnspecified && captured.has(p.key)) ||
      matching.find(p => p.gender === "Male" && !p.region && !p.formUnspecified) ||
      matching.find(p => !p.formUnspecified) || matching[0];
  }).filter(Boolean);
}
function boxes() {
  const start = (box - 1) * 30,
    first = homeData[start],
    last = homeData[Math.min(start + 29, homeData.length - 1)];
  $("#boxes").innerHTML =
    `<div class="box-heading"><button id="prev" ${box === 1 ? "disabled" : ""} aria-label="Previous box">←</button><div><small>NATIONAL POKÉDEX STORAGE</small><h3>Box ${String(box).padStart(2, "0")} <span>#${num(first.id)} — #${num(last.id)}</span></h3></div><button id="next" ${box === Math.ceil(homeData.length / 30) ? "disabled" : ""} aria-label="Next box">→</button></div><div class="box-grid">${Array.from(
      { length: 30 },
      (_, i) => {
        const p = homeData[start + i];
        if (!p) return '<div class="slot vacant"><span>Empty slot</span></div>';
        const loc = position(p),
          tooltip = `${name(p)} · #${num(p.id)} · Box ${loc.box}, Row ${loc.row}, Column ${loc.column} · ${shinies.has(p.key) ? "Shiny captured" : captured.has(p.key) ? "Captured" : "Not captured"}`;
        return `<div class="slot ${matches(p) ? "" : "dim"} ${captured.has(p.key) ? "is-captured" : ""} ${shinies.has(p.key) ? "is-shiny" : ""}"><span class="slot-num">${num(p.id)}</span><div class="slot-checks">${check(p, "captured")}${check(p, "shiny")}</div><button data-select="${p.key}" title="${esc(tooltip)}" aria-label="${esc(tooltip)}">${image(p)}<strong>${esc(name(p))}</strong><span class="hover-name">${esc(name(p))}</span></button><small>R${loc.row} · C${loc.column}</small></div>`;
      },
    ).join("")}</div>`;
  $("#box-select").value = box;
}
function collection() {
  const all = data.filter((p) => shinies.has(p.key)),
    items = all.filter(matches);
  $("#collection-summary").textContent =
    `${all.length} shiny Pokémon captured · ${items.length} shown`;
  $("#collection-grid").innerHTML = items.length
    ? items
        .map((p) => {
          const loc = position(p);
          return `<article class="collection-card"><div class="collection-card-head"><span>#${num(p.id)}</span><div class="row-checks">${check(p, "captured")}${check(p, "shiny")}</div></div><button data-select="${p.key}">${image(p)}<h3>${esc(name(p))}</h3></button><small>${loc ? `Box ${loc.box} · R${loc.row} · C${loc.column}` : "Choose a form to assign a HOME slot"}</small></article>`;
        })
        .join("")
    : `<div class="empty">${all.length ? "No captured shinies match these filters." : "Your shiny journey starts here. Check Shiny captured on a Pokémon to add it to this collection."}</div>`;
}
function hunting() {
  const p = byKey.get(selected),
    h = hunts[p.key] || { locked: false, entries: [] },
    games = [...new Set(h.entries.map((e) => e.game))];
  $("#hunt-panel").innerHTML =
    `<div class="hunt-header"><div><div class="eyebrow">PLAN YOUR NEXT HUNT</div><h2>${esc(name(p))} · Hunting methods</h2></div>${games.length ? `<select id="hunt-game" aria-label="Hunting game"><option value="">All recorded games</option>${games.map((g) => `<option>${esc(g)}</option>`).join("")}</select>` : ""}</div><div id="hunt-entries"></div><p class="hunt-note">Game-specific encounters and shiny restrictions. Coverage is still being audited; this guide does not yet include every game or event. Unverified gift restrictions are labeled. Shiny locks apply to the selected form and game. References checked October 3, 2026.</p><div class="hunt-links"><a target="_blank" rel="noreferrer" href="${p.source}#Game_locations">Bulbapedia game locations ↗</a><a target="_blank" rel="noreferrer" href="https://bulbapedia.bulbagarden.net/wiki/List_of_unobtainable_Shiny_Pok%C3%A9mon">Shiny lock reference ↗</a></div>`;
  huntEntries();
}
// Only validated HTTP(S) source links are inserted into the hunting panel.
function methodSources(entry) {
  const references = [
    ...new Set(
      [entry.source, ...(entry.sourceReferences || [])].filter(Boolean),
    ),
  ];
  return references
    .map((reference, index) => {
      let url;
      try {
        url = new URL(reference);
      } catch {
        return "";
      }
      if (!["https:", "http:"].includes(url.protocol)) return "";
      const label =
        index === 0
          ? "Source"
          : url.hostname === "bulbapedia.bulbagarden.net"
            ? decodeURIComponent(url.pathname.split("/").pop()).replaceAll(
                "_",
                " ",
              )
            : "Supporting reference";
      return `<a class="method-source" target="_blank" rel="noreferrer" href="${esc(url.href)}">${esc(label)} ↗</a>`;
    })
    .join(" ");
}
function huntEntries() {
  const p = byKey.get(selected),
    h = hunts[p.key] || { locked: false, entries: [] },
    game = $("#hunt-game")?.value;
  $("#hunt-entries").innerHTML = h.locked
    ? '<div class="locked-message">🔒 <strong>Shiny Locked</strong><p>No legitimate shiny hunting or acquisition method is currently documented for this form.</p></div>'
    : h.entries.length
      ? `<div class="hunt-table"><div class="hunt-row heading"><span>GAME</span><span>METHOD / LOCATION</span><span>SHINY STATUS</span></div>${h.entries
          .filter((e) => !game || e.game === game)
          .map(
            (e) =>
              `<div class="hunt-row"><strong>${esc(e.game)}</strong><div>${e.status === "Shiny Locked" ? "<strong>Shiny Locked</strong><br>" : ""}${esc(e.method)}${e.locations?.length ? `<details><summary>${e.locations.length} recorded location${e.locations.length === 1 ? "" : "s"}</summary><p>${e.locations.map(esc).join(" · ")}</p></details>` : ""}${methodSources(e)}</div><span class="hunt-status ${e.status === "Shiny Locked" ? "locked" : ["Huntable", "Guaranteed shiny"].includes(e.status) ? "available" : "unverified"}">${esc(e.status)}</span></div>`,
          )
          .join("")}</div>`
      : '<div class="empty">Methods are being verified for this form. Missing records are not proof of a shiny lock.</div>';
}
function imageErrors() {
  document.querySelectorAll("[data-image]").forEach(
    (img) =>
      (img.onerror = () => {
        img.onerror = null;
        img.classList.add("image-missing");
        img.alt = "Image unavailable";
      }),
  );
}
function render() {
  stats();
  detail();
  assignmentControl();
  if (view === "dex") list();
  if (view === "home") boxes();
  if (view === "collection") collection();
  selectionLayout();
  if (view === "dex" && selected !== null) hunting();
  imageErrors();
}
function selectionLayout() {
  $("main").classList.toggle("dex-workspace", view === "dex");
  $("#dex").classList.toggle("has-selection", selected !== null);
  $("main").classList.toggle("selection-open", selected !== null && view === "dex");
  $("#hunt-panel").hidden = selected === null;
  fitWorkspace();
}
function setView(next) {
  view = next;
  $("#dex").hidden = view !== "dex";
  $("#home").hidden = view !== "home";
  $("#collection").hidden = view !== "collection";
  document.querySelectorAll("[data-tab]").forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === view);
    b.setAttribute("aria-selected", b.dataset.tab === view);
  });
  render();
}
// Write immediately after each checkbox change, before repainting the views.
async function save() {
  try {
    const collection = collectionRecord();
    if (window.shinydexDesktop) await window.shinydexDesktop.saveCollection(collection);
    else localStorage.setItem(storageKey, JSON.stringify(collection));
    $("#save").textContent = "";
  } catch {
    $("#save").textContent = "Not saved — export a backup";
  }
}

// A single delegated handler supports checkboxes in every collection view.
document.addEventListener("change", (event) => {
  const control = event.target;
  if (assigningForm) return;
  if (control.dataset.catch) {
    const id = Number(control.dataset.catch);
    const isShinyCheckbox = control.dataset.kind === "shiny";
    if (isShinyCheckbox) {
      control.checked ? shinies.add(id) : shinies.delete(id);
      if (control.checked) captured.add(id);
    } else {
      control.checked ? captured.add(id) : captured.delete(id);
      // Removing a capture also removes its shiny ownership.
      if (!control.checked) shinies.delete(id);
    }
    save();
    const scroll = $("#list").scrollTop;
    render();
    $("#list").scrollTop = scroll;
  } else if (control.id === "box-select") {
    box = Number(control.value);
    render();
  } else if (["generation", "status"].includes(control.id)) {
    render();
  } else if (control.id === "hunt-game") {
    huntEntries();
  }
});

document.addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  if (b.dataset.toggleForms) {
    const id = Number(b.dataset.toggleForms);
    const panel = document.querySelector(`#forms-${id}`);
    const open = !openForms.has(id);
    if (open) openForms.add(id); else openForms.delete(id);
    b.setAttribute("aria-expanded", String(open));
    if (open) {
      const rowKey = Number(b.closest("[data-row]").dataset.row);
      panel.innerHTML = new DOMParser().parseFromString(formGallery(byKey.get(rowKey)), "text/html").body.firstElementChild.innerHTML;
      panel.inert = false;
      panel.removeAttribute("aria-hidden");
      imageErrors();
    } else {
      panel.inert = true;
      panel.setAttribute("aria-hidden", "true");
    }
    panel.classList.toggle("is-open", open);
    return;
  }
  if (b.dataset.chooseForm) {
    selected = Number(b.dataset.chooseForm);
    chosenForms.set(byKey.get(selected).id, selected);
    const scroll = $("#list").scrollTop;
    render();
    $("#list").scrollTop = scroll;
    document.querySelector(`[data-choose-form="${selected}"]`)?.focus({ preventScroll: true });
    return;
  }
  if (b.id === "close-selection") {
    selected = null;
    render();
    $("#list").focus({ preventScroll: true });
    return;
  }
  if (b.id === "assign-form") { assignSelectedForm(); return; }
  if (b.dataset.tab) setView(b.dataset.tab);
  if (b.dataset.mode) {
    mode = b.dataset.mode;
    document
      .querySelectorAll("[data-mode]")
      .forEach((x) => x.classList.toggle("active", x === b));
    render();
  }
  if (b.dataset.select) {
    selected = Number(b.dataset.select);
    chosenForms.set(byKey.get(selected).id, selected);
    selectionLayout();
    if (view !== "dex") setView("dex");
    else {
      detail();
      assignmentControl();
      hunting();
      document
        .querySelectorAll("[data-row]")
        .forEach((r) =>
          r.classList.toggle("selected", Number(r.dataset.row) === selected),
        );
      imageErrors();
    }
  }
  if (b.id === "locate") {
    box = position(byKey.get(selected)).box;
    setView("home");
  }
  if (b.id === "prev") {
    box--;
    render();
  }
  if (b.id === "next") {
    box++;
    render();
  }
  if (b.id === "export") {
    const payload = {
        ...collectionRecord(),
        entries: data
          .filter((p) => captured.has(p.key))
          .map((p) => ({
            key: p.key,
            nationalId: p.id,
            name: name(p),
            shiny: shinies.has(p.key),
          })),
        exportedAt: new Date().toISOString(),
      },
      a = document.createElement("a");
    a.href = URL.createObjectURL(
      new Blob([JSON.stringify(payload, null, 2)], {
        type: "application/json",
      }),
    );
    a.download = "shinydex-backup.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
});
$("#search").addEventListener("input", render);
$("#list").addEventListener("keydown", (e) => {
  if (!["ArrowUp", "ArrowDown"].includes(e.key) || ["INPUT", "SELECT"].includes(e.target.tagName))
    return;
  e.preventDefault();
  const items = listItems(),
    index = items.findIndex((p) => p.key === selected),
    p =
      items[
        Math.max(
          0,
          Math.min(items.length - 1, index + (e.key === "ArrowDown" ? 1 : -1)),
        )
      ];
  if (p) {
    selected = p.key;
    render();
    document
      .querySelector(`[data-row="${selected}"]`)
      ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
});
// Synchronize collection changes made in another tab on the same origin.
window.addEventListener("storage", (event) => {
  if (event.key !== storageKey) return;
  try {
    const collection = JSON.parse(
      event.newValue || '{"version":2,"captured":[],"shinies":[]}',
    );
    ({ captured, shinies, futureCaptured, futureShinies } = decodeCollection(collection));
    render();
    // A later valid update recovers the collection and clears stale warnings.
    $("#save").textContent = "";
  } catch {
    $("#save").textContent = "Collection changed — reload to recover";
  }
});

if (window.shinydexDesktop) {
  const button = document.createElement("button");
  button.textContent = "Import backup";
  button.addEventListener("click", async () => {
    if (assigningForm) return;
    try {
      const record = await window.shinydexDesktop.importCollection();
      if (record) {
        ({ captured, shinies, futureCaptured, futureShinies } = decodeCollection(record));
        render();
        $("#save").textContent = "✓ Backup imported";
      }
    } catch {
      $("#save").textContent = "Backup could not be imported — check the JSON file";
    }
  });
  $(".header-right").append(button);
} else {
  const panel = document.createElement("details");
  panel.id = "assignment-backups";
  panel.className = "assignment-backups";
  panel.innerHTML = '<summary>Recover a form-assignment backup</summary><p>Restoring saves a backup of your current collection first.</p><label>Saved collection <select aria-label="Form-assignment backup"></select></label><button type="button">Restore selected backup</button>';
  panel.querySelector("button").addEventListener("click", restoreAssignmentBackup);
  $("header").after(panel);
  refreshAssignmentBackups();
}

// Measure the actual space below the controls, including wrapped toolbars and
// native update controls. CSS pixels also account for monitor DPI and app zoom.
let workspaceFrame;
function fitWorkspace() {
  cancelAnimationFrame(workspaceFrame);
  workspaceFrame = requestAnimationFrame(() => {
    if (view !== "dex") return;
    const top = $("#dex").getBoundingClientRect().top + window.scrollY;
    const footerHeight = $("main > footer").getBoundingClientRect().height;
    $("#dex").style.setProperty("--workspace-height", `${Math.max(260, window.innerHeight - top - footerHeight - 40)}px`);
  });
}
const workspaceObserver = new ResizeObserver(fitWorkspace);
for (const element of document.querySelectorAll("header, .intro, nav, .toolbar, #unassigned-summary, main > footer")) workspaceObserver.observe(element);
window.addEventListener("resize", fitWorkspace);
fitWorkspace();

render();

// Browser entry point. Collection keys identify species and regional forms.
const $ = (selector) => document.querySelector(selector);

async function read(file) {
  const response = await fetch(file);
  if (!response.ok) throw Error(`Cannot load ${file}`);
  return response.json();
}

const data = await read("./data.json");
const hunts = await read("./hunts.json");
const byKey = new Map(data.map((pokemon) => [pokemon.key, pokemon]));

// Save captures and shinies separately; every shiny must also be captured.
const storageKey = "shinydex-collection-v2";
let captured = new Set();
let shinies = new Set();
let selected = 1;
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
  const nextCaptured = valid(collection.captured);
  const nextShinies = valid(collection.shinies);
  nextShinies.forEach((id) => nextCaptured.add(id));
  return { captured: nextCaptured, shinies: nextShinies };
}

try {
  const saved = window.shinydexDesktop
    ? await window.shinydexDesktop.loadCollection()
    : localStorage.getItem(storageKey);
  if (saved) {
    const collection = JSON.parse(saved);
    ({ captured, shinies } = decodeCollection(collection));
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
const image = (p, eager = false) =>
  `<img loading="${eager ? "eager" : "lazy"}" src="${isShiny(p) ? p.shiny : p.normal}" alt="${isShiny(p) ? "Shiny" : "Normal"} ${esc(name(p))}" data-image>`;
function check(p, kind) {
  const shiny = kind === "shiny",
    checked = (shiny ? shinies : captured).has(p.key);
  return `<label class="catch ${shiny ? "shiny-check" : "captured-check"}" title="${shiny ? "Shiny captured" : "Captured"}"><input type="checkbox" data-kind="${kind}" data-catch="${p.key}" aria-label="${esc(name(p))} ${shiny ? "shiny captured" : "captured"}" ${checked ? "checked" : ""}><span>${shiny ? "✧" : "✓"}</span></label>`;
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
for (let b = 1; b <= Math.ceil(data.length / 30); b++) {
  const first = data[(b - 1) * 30],
    last = data[Math.min(b * 30 - 1, data.length - 1)];
  $("#box-select").add(
    new Option(
      `Box ${String(b).padStart(2, "0")} · #${num(first.id)}–${num(last.id)}`,
      b,
    ),
  );
}
function stats() {
  $("#total").innerHTML =
    `${shinies.size} <em>/ ${data.length.toLocaleString()}</em>`;
  const pc = (shinies.size / data.length) * 100;
  $("#progress").style.width = pc + "%";
  $("#percent").textContent =
    `${pc.toFixed(1)}% shiny complete · ${captured.size.toLocaleString()} captured`;
  $("#collection-count").textContent = shinies.size;
}
function detail() {
  const p = byKey.get(selected),
    loc = position(p);
  $("#detail").innerHTML =
    `<div class="detail-top"><span>POKÉMON DATA</span><span class="dot">● ● ●</span></div><div class="hero-image">${isShiny(p) ? '<span class="shiny-badge">✧ SHINY FORM</span>' : ""}${image(p, true)}<div class="orbit"></div></div><div class="detail-info"><div class="eyebrow">NATIONAL № ${num(p.id)}${p.formLabel ? " · " + esc(p.formLabel) : ""}</div><h2>${esc(p.speciesName)}</h2><div class="types">${p.types.map((t) => `<span class="type ${t}">${t}</span>`).join("")}</div><div class="measure"><div><small>HEIGHT</small><strong>${(p.height / 10).toFixed(1)} <em>m</em></strong></div><div><small>WEIGHT</small><strong>${(p.weight / 10).toFixed(1)} <em>kg</em></strong></div><div><small>GENERATION</small><strong>${p.generation}</strong></div></div><div class="detail-checks"><div>${check(p, "captured")}<span>Captured</span></div><div>${check(p, "shiny")}<span>Shiny captured</span></div></div><p class="auto-note">Each change saves automatically. Shiny captured also marks Captured.</p><button id="locate" class="location">▦ &nbsp; Box ${loc.box} · Row ${loc.row}, Column ${loc.column} <span>↗</span></button><a class="source-link" target="_blank" rel="noreferrer" href="${p.source}">View on Bulbapedia ↗</a></div>`;
}
function list() {
  const items = data.filter(matches);
  $("#result-count").textContent = `${items.length.toLocaleString()} entries`;
  $("#list").innerHTML = items.length
    ? items
        .map(
          (p) =>
            `<div class="row ${p.key === selected ? "selected" : ""} ${captured.has(p.key) ? "is-captured" : ""}" data-row="${p.key}"><button class="row-select" data-select="${p.key}"><span class="number">${num(p.id)}</span>${image(p)}<strong>${esc(name(p))}</strong><span class="row-types">${p.types.map((t) => `<i class="type ${t}">${t}</i>`).join("")}</span></button><div class="row-checks">${check(p, "captured")}${check(p, "shiny")}</div></div>`,
        )
        .join("")
    : '<div class="empty">No Pokémon found. Try another name or filter.</div>';
}
function boxes() {
  const start = (box - 1) * 30,
    first = data[start],
    last = data[Math.min(start + 29, data.length - 1)];
  $("#boxes").innerHTML =
    `<div class="box-heading"><button id="prev" ${box === 1 ? "disabled" : ""} aria-label="Previous box">←</button><div><small>NATIONAL POKÉDEX STORAGE</small><h3>Box ${String(box).padStart(2, "0")} <span>#${num(first.id)} — #${num(last.id)}</span></h3></div><button id="next" ${box === Math.ceil(data.length / 30) ? "disabled" : ""} aria-label="Next box">→</button></div><div class="box-grid">${Array.from(
      { length: 30 },
      (_, i) => {
        const p = data[start + i];
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
          return `<article class="collection-card"><div class="collection-card-head"><span>#${num(p.id)}</span><div class="row-checks">${check(p, "captured")}${check(p, "shiny")}</div></div><button data-select="${p.key}">${image(p)}<h3>${esc(name(p))}</h3></button><small>Box ${loc.box} · R${loc.row} · C${loc.column}</small></article>`;
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
  if (view === "dex") list();
  if (view === "home") boxes();
  if (view === "collection") collection();
  $("#hunt-panel").hidden = view !== "dex";
  if (view === "dex") hunting();
  imageErrors();
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
    const collection = {
      version: 2,
      captured: [...captured],
      shinies: [...shinies],
    };
    if (window.shinydexDesktop) await window.shinydexDesktop.saveCollection(collection);
    else localStorage.setItem(storageKey, JSON.stringify(collection));
    $("#save").textContent = "✓ Saved just now";
  } catch {
    $("#save").textContent = "Not saved — export a backup";
  }
}

// A single delegated handler supports checkboxes in every collection view.
document.addEventListener("change", (event) => {
  const control = event.target;
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
    if (view !== "dex") setView("dex");
    else {
      detail();
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
        version: 2,
        captured: [...captured],
        shinies: [...shinies],
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
  if (!["ArrowUp", "ArrowDown"].includes(e.key) || e.target.tagName === "INPUT")
    return;
  e.preventDefault();
  const items = data.filter(matches),
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
      event.newValue || '{"captured":[],"shinies":[]}',
    );
    ({ captured, shinies } = decodeCollection(collection));
    render();
    // A later valid update recovers the collection and clears stale warnings.
    $("#save").textContent = "Saved on this device";
  } catch {
    $("#save").textContent = "Collection changed — reload to recover";
  }
});

if (window.shinydexDesktop) {
  const button = document.createElement("button");
  button.textContent = "Import backup";
  button.addEventListener("click", async () => {
    try {
      const record = await window.shinydexDesktop.importCollection();
      if (record) {
        ({ captured, shinies } = decodeCollection(record));
        render();
        $("#save").textContent = "✓ Backup imported";
      }
    } catch {
      $("#save").textContent = "Backup could not be imported — check the JSON file";
    }
  });
  $(".header-right").append(button);
}
render();

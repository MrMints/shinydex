// The Windows launcher supplies this controller even for older app versions.
// Browser ownership remains at the same origin and storage key on every switch.
(async () => {
  const endpoint = "/__updates/";
  let state;
  let installing = false;
  let dismissed = false;
  let originalVersion;
  let poll;
  let refreshing = false;
  let choiceMade = false;
  let versionsSignature = "";
  let installStarted;
  const status = async () => {
    const response = await fetch(endpoint + "status", { cache: "no-store" });
    if (!response.ok) throw Error("Update service unavailable");
    return response.json();
  };
  try { state = await status(); } catch { return; } // Source-only Node server has no native updater.
  originalVersion = state.currentVersion;

  const style = document.createElement("style");
  style.textContent = `
    #update-dialog { width:min(480px,calc(100vw - 32px)); padding:0; border:4px solid #70303a; border-radius:7px; background:#eff5f7; color:#243748; box-sizing:border-box; box-shadow:0 16px 60px #23131b66; }
    #update-dialog::backdrop { background:#24141d99; }
    #update-dialog .update-heading { padding:20px 24px 16px; background:#c2d3de; border-bottom:2px solid #9bafbd; }
    #update-dialog h2 { margin:0 0 8px; font:700 23px Trebuchet MS,Arial,sans-serif; }
    #update-dialog p { margin:0; line-height:1.5; color:#405d70; }
    #update-dialog .update-body { padding:20px 24px 24px; }
    #update-dialog .update-note { margin-bottom:18px; }
    #update-dialog .update-label { display:block; font-weight:700; font-size:13px; margin-bottom:7px; }
    #update-dialog .update-control { display:flex; border:2px solid #174764; border-radius:5px; overflow:hidden; }
    #update-install { padding:12px 14px; border:0; border-right:2px solid #174764; background:#23648a; color:white; font:700 14px Trebuchet MS,Arial,sans-serif; cursor:pointer; white-space:nowrap; }
    #update-version { min-width:0; flex:1; padding:11px 8px; border:0; background:#e0ecf2; color:#243748; font:13px Trebuchet MS,Arial,sans-serif; cursor:pointer; }
    #update-dialog button:disabled, #update-dialog select:disabled { opacity:.6; cursor:default; }
    #update-dialog .update-footer { display:flex; justify-content:space-between; align-items:center; margin-top:16px; gap:12px; }
    #update-later, #update-retry { border:1px solid #819eaf; border-radius:4px; padding:8px 12px; background:#eff5f7; color:#294e67; cursor:pointer; font:13px Trebuchet MS,Arial,sans-serif; }
    #update-message { margin-top:16px !important; font-size:13px; overflow-wrap:anywhere; }
    #update-progress { width:100%; height:12px; margin-top:14px; accent-color:#23648a; }
    #update-dialog [hidden] { display:none !important; }
    @media(max-width:440px) { #update-dialog .update-heading, #update-dialog .update-body { padding:18px; } #update-install { padding:12px 9px; } #update-version { font-size:12px; } }
  `;
  document.head.append(style);
  const openButton = document.createElement("button");
  openButton.id = "update-open";
  openButton.textContent = "Updates";
  openButton.title = "Check for updates or install another version";
  document.querySelector(".header-right").append(openButton);
  const dialog = document.createElement("dialog");
  dialog.id = "update-dialog";
  dialog.setAttribute("aria-labelledby", "update-title");
  dialog.innerHTML = `<div class="update-heading"><h2 id="update-title">ShinyDex updates</h2><p id="update-current"></p></div>
    <div class="update-body"><p class="update-note">Your collection stays saved. Choose the latest release or an older version.</p>
    <label class="update-label" for="update-version">Version to install</label><div class="update-control"><button id="update-install">Update now</button><select id="update-version" aria-label="Version to install"></select></div>
    <progress id="update-progress" max="100" value="0" hidden aria-label="Update download progress"></progress><p id="update-message" role="status" aria-live="polite"></p>
    <div class="update-footer"><button id="update-retry">Check again</button><button id="update-later">Later</button></div></div>`;
  document.body.append(dialog);
  const title = dialog.querySelector("#update-title");
  const current = dialog.querySelector("#update-current");
  const versions = dialog.querySelector("#update-version");
  const install = dialog.querySelector("#update-install");
  const message = dialog.querySelector("#update-message");
  const progress = dialog.querySelector("#update-progress");
  const later = dialog.querySelector("#update-later");
  const retry = dialog.querySelector("#update-retry");

  function render() {
    current.textContent = `Installed: ${state.currentVersion}`;
    title.textContent = installing ? "Installing ShinyDex…" : state.updateAvailable ? "A new update is available" : "ShinyDex versions";
    openButton.textContent = state.updateAvailable ? "Update available" : "Updates";
    const signature = JSON.stringify([state.releases, state.currentVersion, state.latestVersion]);
    if (signature !== versionsSignature) {
    const selected = choiceMade ? versions.value : null;
    versions.replaceChildren();
    for (const release of state.releases) {
      const option = document.createElement("option");
      option.value = release.tag;
      option.textContent = release.tag + (release.tag === state.currentVersion ? " (installed)" : release.tag === state.latestVersion ? " (latest)" : "");
      versions.append(option);
    }
    if (!state.releases.some((release) => release.tag === state.currentVersion)) {
      const option = document.createElement("option");
      option.value = state.currentVersion;
      option.textContent = state.currentVersion + " (installed)";
      versions.append(option);
    }
    versions.value = state.releases.some((release) => release.tag === selected) ? selected : state.updateAvailable ? state.latestVersion : state.currentVersion;
    versionsSignature = signature;
    }
    versions.disabled = installing || !state.releases.length;
    install.disabled = installing || versions.value === state.currentVersion || !state.releases.some((release) => release.tag === versions.value);
    install.textContent = installing ? "Installing…" : "Update now";
    later.disabled = installing;
    later.textContent = state.updateAvailable ? "Later" : "Close";
    retry.disabled = installing || state.status === "checking";
    progress.hidden = !installing;
    progress.value = state.progress;
    message.textContent = state.error || (installing ? state.status === "restarting" ? "Restarting ShinyDex. This page will reopen automatically." : `Downloading and verifying… ${state.progress}%` : state.status === "checking" ? "Checking for updates…" : state.updateAvailable ? "Update now to install, or use the dropdown to choose an older release." : "You can switch versions using the dropdown above.");
  }
  function show() { render(); if (!dialog.open) dialog.showModal(); }
  async function post(action, body = {}) {
    const response = await fetch(endpoint + action, { method: "POST", headers: { "Content-Type": "application/json", "X-ShinyDex-Token": state.token }, body: JSON.stringify(body), cache: "no-store" });
    const result = await response.json();
    if (!response.ok) throw Error(result.error || "The update could not start. Please try again.");
    return result;
  }
  async function refresh() {
    if (refreshing) return;
    refreshing = true;
    try {
      state = await status();
      if (installing && state.currentVersion !== originalVersion && !["downloading", "restarting"].includes(state.status)) {
        clearInterval(poll);
        location.reload();
        return;
      }
      if (installing && state.status === "error") installing = false;
      render();
      if (state.updateAvailable && !dismissed && !installing && state.status !== "checking") show();
    } catch {
      if (installing) message.textContent = Date.now() - installStarted > 45000
        ? "The launcher is taking longer to restart. Reopen ShinyDex.exe if this page does not return; your collection is still saved."
        : "Restarting ShinyDex… waiting for the app to reopen.";
    }
    finally { refreshing = false; }
  }
  async function check() {
    try { state = await post("check"); render(); } catch (error) { message.textContent = error.message; }
  }
  openButton.addEventListener("click", () => { dismissed = false; show(); check(); });
  retry.addEventListener("click", check);
  versions.addEventListener("change", () => {
    choiceMade = true;
    install.disabled = installing || versions.value === state.currentVersion;
    message.textContent = versions.value === state.currentVersion ? "This version is already installed." : `Install ${versions.value}. Your collection will stay saved.`;
  });
  later.addEventListener("click", () => { dismissed = true; dialog.close(); });
  dialog.addEventListener("cancel", (event) => { if (installing) event.preventDefault(); else dismissed = true; });
  install.addEventListener("click", async () => {
    try {
      // Snapshot browser storage before the native installer makes its local disk backup.
      // Never install over a collection that has unsaved changes or inaccessible storage.
      const saveWarning = document.querySelector("#save")?.textContent || "";
      if (/unavailable|not saved|recover/i.test(saveWarning)) throw Error("Export your collection backup before updating; browser storage is not saving reliably.");
      let collection = localStorage.getItem("shinydex-collection-v2");
      if (collection === null) {
        const legacy = JSON.parse(localStorage.getItem("shinydex-caught-v1") || "[]");
        collection = JSON.stringify({ version: 2, captured: legacy, shinies: legacy });
      }
      const parsed = JSON.parse(collection);
      if (!Array.isArray(parsed.captured) || !Array.isArray(parsed.shinies)) throw Error("Export your collection backup before updating; the saved record needs recovery.");
      originalVersion = state.currentVersion;
      installing = true;
      installStarted = Date.now();
      state = await post("install", { tag: versions.value, collection });
      render();
    } catch (error) { installing = false; render(); message.textContent = error.message; }
  });
  render();
  await check();
  await refresh();
  poll = setInterval(refresh, 1000);
})();

const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
async function run({window,store,profile,app}){
  const errors=[];
  window.webContents.on('console-message',event=>{if(event.level==='error')errors.push(event.message);});
  const evaluate=source=>{
    // CSS attribute quotes must survive the JavaScript source sent to Electron.
    const safeSource=source.replace(/data-(catch|select)="(\d+)"/g, 'data-$1=\\"$2\\"');
    return window.webContents.executeJavaScript(safeSource);
  };
  const wait=async predicate=>{for(let i=0;i<200;i++){if(await evaluate(predicate))return;await new Promise(resolve=>setTimeout(resolve,100));}throw Error('Renderer timed out');};
  const waitSaved=async key=>{for(let i=0;i<200;i++){const saved=JSON.parse(await store.load());if(saved.shinies.includes(key)){assert.equal(await evaluate('document.querySelector("#save").textContent'), '');return;}await new Promise(resolve=>setTimeout(resolve,100));}throw Error('Autosave timed out');};
  try{
    await wait('!!document.querySelector("[data-catch]") && !!document.querySelector("#update-open")');
    assert.equal(await evaluate('location.protocol'), 'shiny:');
    assert.equal(await evaluate('typeof require'), 'undefined');
    assert.equal(await evaluate('typeof window.shinydexDesktop.saveCollection'), 'function');
    await wait('document.querySelector("[data-image]")?.naturalWidth > 0');
    assert.equal(await evaluate('document.querySelector("[data-image]").naturalWidth > 0'),true);
    await evaluate('document.querySelector("button[data-select=\\"1\\"]").click()');
    await wait('!!document.querySelector("#pokedex-game")');
    assert.equal(await evaluate('document.querySelector("#pokedex-game").value'),'scarlet');
    assert.equal(await evaluate('document.querySelector(".pokedex-description p").textContent'),'For some time after its birth, it uses the nutrients that are packed into the seed on its back in order to grow.');
    assert.equal(await evaluate('fetch("shiny://app/pokedex-entries.json").then(r=>r.status)'),200);
    assert.equal(await evaluate('fetch("shiny://app/pokedex.js").then(r=>r.status)'),200);
    await evaluate('document.querySelector("#all-hunt-games").click()');
    const allHunts=await evaluate('document.querySelectorAll(".hunt-row:not(.heading)").length');
    await evaluate('document.querySelector("#all-hunt-games").click()');
    assert.ok(allHunts>await evaluate('document.querySelectorAll(".hunt-row:not(.heading)").length'));
    await evaluate('(()=>{const s=document.querySelector("#pokedex-game");s.value="red-japan";s.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await wait('document.querySelector(".pokedex-empty")?.textContent==="No description recorded for this game."');
    assert.ok(await evaluate('document.querySelectorAll(".hunt-row:not(.heading)").length')>0);
    await evaluate('(()=>{const s=document.querySelector("#pokedex-game");s.value="red";s.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await wait('document.querySelector(".pokedex-description p")?.textContent.startsWith("A strange seed")');
    await evaluate('document.querySelector("button[data-select=\\"4\\"]").click()');
    await wait('document.querySelector("#pokedex-game")?.value==="red" && document.querySelector("#pokedex-card h2")?.textContent.includes("Charmander")');
    await evaluate('document.querySelector("button[data-select=\\"1\\"]").click()');
    await wait('document.querySelector("#pokedex-card h2")?.textContent.includes("Bulbasaur")');
    await evaluate('(()=>{const s=document.querySelector("#pokedex-game");s.value="scarlet";s.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await wait('document.querySelector(".pokedex-description p")?.textContent.startsWith("For some time")');
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="Raichu";s.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector(".form-toggle").click();document.querySelector("button[data-choose-form=\\"10100\\"]").click();})()');
    await wait('document.querySelector("#pokedex-card h2")?.textContent.includes("Raichu")');
    await evaluate('(()=>{const s=document.querySelector("#pokedex-game");s.value="sun";s.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await wait('Array.from(document.querySelectorAll(".pokedex-form"),e=>e.textContent).includes("Alolan Form")');
    assert.equal(await evaluate('document.querySelector("#detail .eyebrow").textContent.includes("Alolan")'),true);
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="";s.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("button[data-select=\\"1\\"]").click();})()');
    await wait('document.querySelector("#pokedex-card h2")?.textContent.includes("Bulbasaur")');
    await evaluate('(()=>{const s=document.querySelector("#pokedex-game");s.value="scarlet";s.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await wait('document.querySelector(".pokedex-description p")?.textContent.startsWith("For some time")');
    for(const width of [1280,1920,420]){
      window.setSize(width,900);
      await new Promise(resolve=>setTimeout(resolve,550));
      assert.equal(await evaluate('(()=>{const r=document.querySelector("#pokedex-card").getBoundingClientRect();return r.width>0 && r.left>=0 && r.right<=innerWidth && document.documentElement.scrollWidth<=innerWidth;})()'),true);
      await evaluate('document.querySelector("#pokedex-card").scrollIntoView({block:"center"})');
      await fs.writeFile(path.join(profile,`pokedex-${width}.png`),(await window.webContents.capturePage()).toPNG());
    }
    window.setSize(1280,900);
    await evaluate('document.querySelector("#close-selection").click();window.scrollTo(0,0)');
    const counts=()=>evaluate('Array.from(document.querySelectorAll("#captured-total, #total"),el=>parseInt(el.textContent,10))');
    assert.deepEqual(await counts(),[0,0]);
    assert.equal(await evaluate('getComputedStyle(document.querySelector("#save")).display'), 'none');
    assert.equal(await evaluate('(()=>{const s=document.querySelector("#save");s.textContent="Not saved — export a backup";const visible=getComputedStyle(s).display!=="none";s.textContent="";return visible;})()'),true);
    await evaluate('document.querySelector("input[data-catch=\"1\"][data-kind=captured]").click()');
    assert.deepEqual(await counts(),[1,0]);
    await evaluate('document.querySelector("input[data-catch=" + JSON.stringify("1") + "][data-kind=shiny]").click()');
    await waitSaved(1);
    assert.deepEqual(JSON.parse(await store.load()).shinies,[1]);
    assert.deepEqual(await counts(),[1,1]);
    await window.loadURL('shiny://app/');
    await wait('!!document.querySelector("input[data-catch=" + JSON.stringify("1") + "][data-kind=shiny]:checked")');
    await wait('!!document.querySelector("#update-open")');
    assert.deepEqual(await counts(),[1,1]);
    for(const width of [1280,420]){
      window.setSize(width,900);
      await new Promise(resolve=>setTimeout(resolve,150));
      assert.equal(await evaluate('(()=>{const a=document.querySelector("#captured-total").getBoundingClientRect(),b=document.querySelector("#total").getBoundingClientRect();return a.right<=b.left && Math.abs(a.top-b.top)<2 && b.right<=innerWidth;})()'),true);
      await fs.writeFile(path.join(profile,`counters-${width}.png`),(await window.webContents.capturePage()).toPNG());
    }
    await evaluate('document.querySelector("input[data-catch=\"1\"][data-kind=captured]").click()');
    assert.deepEqual(await counts(),[0,0]);
    window.setSize(1280,900);
    // Use only the explicitly isolated QA profile for independent form captures.
    assert.equal(await evaluate('document.querySelectorAll(".form-toggle").length'),219);
    assert.equal(await evaluate('document.querySelector("[data-row=\\"1\\"] .form-toggle")'),null);
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="Pikachu";s.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector(".form-toggle").click();document.querySelector("button[data-choose-form=" + JSON.stringify("300051") + "]").click();})()');
    await evaluate('document.querySelector("input[data-catch=\"300051\"][data-kind=shiny]").click()');
    await waitSaved(300051);
    assert.deepEqual(await counts(),[1,1]);
    await evaluate('(()=>{document.querySelector("button[data-choose-form=" + JSON.stringify("300050") + "]").click();document.querySelector("input[data-catch=\"300050\"][data-kind=captured]").click();})()');
    for(let i=0;i<200;i++){if(JSON.parse(await store.load()).captured.includes(300050))break;await new Promise(resolve=>setTimeout(resolve,100));}
    assert.ok(JSON.parse(await store.load()).captured.includes(300050));
    assert.deepEqual(await counts(),[2,1]);
    await window.loadURL('shiny://app/');
    await wait('!!document.querySelector(".form-toggle") && !!document.querySelector("#update-open")');
    assert.deepEqual(await counts(),[2,1]);
    assert.deepEqual(JSON.parse(await store.load()).shinies,[300051]);
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="Pikachu";s.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector(".form-toggle").click();document.querySelector("button[data-choose-form=" + JSON.stringify("300051") + "]").click();document.querySelector("#locate").click();})()');
    assert.equal(await evaluate('document.querySelectorAll("#boxes .slot").length'),30);
    const location=await evaluate('document.querySelector("#boxes button[data-select=\"300051\"]").getAttribute("title")');
    await evaluate('document.querySelector("#status").value="shiny";document.querySelector("#status").dispatchEvent(new Event("change",{bubbles:true}))');
    assert.equal(await evaluate('document.querySelector("#boxes button[data-select=\"300051\"]").getAttribute("title")'),location);
    for(const width of [1280,420]){
      window.setSize(width,900);
      await new Promise(resolve=>setTimeout(resolve,150));
      assert.deepEqual(await evaluate('(()=>{const cells=[...document.querySelectorAll("#boxes .slot")].map(e=>e.getBoundingClientRect());return [new Set(cells.map(r=>Math.round(r.left))).size,new Set(cells.map(r=>Math.round(r.top))).size];})()'),[6,5]);
      await fs.writeFile(path.join(profile,`living-dex-${width}.png`),(await window.webContents.capturePage()).toPNG());
    }
    await store.save({version:2,captured:[],shinies:[]});
    window.setSize(1280,900);
    await window.loadURL('shiny://app/');
    await wait('!!document.querySelector("#update-open")');
    await evaluate('document.querySelector("#update-open").click()');
    await wait('document.querySelector("#update-dialog").open');
    assert.equal(await evaluate('fetch("shiny://app/package.json").then(response=>response.status)'),403);
    const image=await window.webContents.capturePage();
    await fs.writeFile(path.join(profile,'smoke.png'),image.toPNG());
    await fs.writeFile(path.join(profile,'smoke.json'),JSON.stringify({passed:true,version:app.getVersion(),packaged:app.isPackaged,url:window.webContents.getURL(),errors},null,2));
    app.exit(0);
  }catch(error){await fs.writeFile(path.join(profile,'smoke.json'),JSON.stringify({passed:false,error:error.stack,errors},null,2));app.exit(1);}
}
module.exports={run};

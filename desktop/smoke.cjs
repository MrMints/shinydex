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
  try{
    await wait('!!document.querySelector("[data-catch]") && !!document.querySelector("#update-open")');
    assert.equal(await evaluate('location.protocol'), 'shiny:');
    assert.equal(await evaluate('typeof require'), 'undefined');
    assert.equal(await evaluate('typeof window.shinydexDesktop.saveCollection'), 'function');
    assert.equal(await evaluate('document.querySelector("[data-image]").naturalWidth > 0'),true);
    const counts=()=>evaluate('Array.from(document.querySelectorAll("#captured-total, #total"),el=>parseInt(el.textContent,10))');
    assert.deepEqual(await counts(),[0,0]);
    await evaluate('document.querySelector("input[data-catch=\"1\"][data-kind=captured]").click()');
    assert.deepEqual(await counts(),[1,0]);
    await evaluate('document.querySelector("input[data-catch=" + JSON.stringify("1") + "][data-kind=shiny]").click()');
    await wait('document.querySelector("#save").textContent.includes("Saved")');
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
    assert.equal(await evaluate('document.querySelectorAll(".form-select").length'),1025);
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="Pikachu";s.dispatchEvent(new Event("input",{bubbles:true}));const f=document.querySelector(".form-select");f.value="300051";f.dispatchEvent(new Event("change",{bubbles:true}));})()');
    await evaluate('document.querySelector("input[data-catch=\"300051\"][data-kind=shiny]").click()');
    await wait('document.querySelector("#save").textContent.includes("Saved")');
    assert.deepEqual(await counts(),[1,1]);
    await evaluate('(()=>{const f=document.querySelector(".form-select");f.value="300050";f.dispatchEvent(new Event("change",{bubbles:true}));document.querySelector("input[data-catch=\"300050\"][data-kind=captured]").click();})()');
    await wait('document.querySelector("#save").textContent.includes("Saved")');
    assert.deepEqual(await counts(),[2,1]);
    await window.loadURL('shiny://app/');
    await wait('!!document.querySelector(".form-select") && !!document.querySelector("#update-open")');
    assert.deepEqual(await counts(),[2,1]);
    assert.deepEqual(JSON.parse(await store.load()).shinies,[300051]);
    await evaluate('(()=>{const s=document.querySelector("#search");s.value="Pikachu";s.dispatchEvent(new Event("input",{bubbles:true}));const f=document.querySelector(".form-select");f.value="300051";f.dispatchEvent(new Event("change",{bubbles:true}));document.querySelector("#locate").click();})()');
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

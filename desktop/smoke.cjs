const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
async function run({window,store,profile,app}){
  const errors=[];
  window.webContents.on('console-message',event=>{if(event.level==='error')errors.push(event.message);});
  const evaluate=source=>window.webContents.executeJavaScript(source);
  const wait=async predicate=>{for(let i=0;i<200;i++){if(await evaluate(predicate))return;await new Promise(resolve=>setTimeout(resolve,100));}throw Error('Renderer timed out');};
  try{
    await wait('!!document.querySelector("[data-catch]") && !!document.querySelector("#update-open")');
    assert.equal(await evaluate('location.protocol'), 'shiny:');
    assert.equal(await evaluate('typeof require'), 'undefined');
    assert.equal(await evaluate('typeof window.shinydexDesktop.saveCollection'), 'function');
    assert.equal(await evaluate('document.querySelector("[data-image]").naturalWidth > 0'),true);
    await evaluate('document.querySelector("input[data-catch=" + JSON.stringify("1") + "][data-kind=shiny]").click()');
    await wait('document.querySelector("#save").textContent.includes("Saved")');
    assert.deepEqual(JSON.parse(await store.load()).shinies,[1]);
    await window.loadURL('shiny://app/');
    await wait('!!document.querySelector("input[data-catch=" + JSON.stringify("1") + "][data-kind=shiny]:checked")');
    await wait('!!document.querySelector("#update-open")');
    await evaluate('document.querySelector("#update-open").click()');
    await wait('document.querySelector("#update-dialog").open');
    assert.equal(await evaluate('fetch("shiny://app/package.json").then(response=>response.status)'),403);
    const image=await window.webContents.capturePage();
    await fs.writeFile(path.join(profile,'smoke.png'),image.toPNG());
    await fs.writeFile(path.join(profile,'smoke.json'),JSON.stringify({passed:true,packaged:app.isPackaged,url:window.webContents.getURL(),errors},null,2));
    app.exit(0);
  }catch(error){await fs.writeFile(path.join(profile,'smoke.json'),JSON.stringify({passed:false,error:error.stack,errors},null,2));app.exit(1);}
}
module.exports={run};

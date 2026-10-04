const http=require('node:http');
const assert=require('node:assert/strict');
const handler=require('./server.cjs');
const server=http.createServer(handler);
server.listen(0,'127.0.0.1',async()=>{
 const request=p=>new Promise((resolve,reject)=>{
  http.get({hostname:'127.0.0.1',port:server.address().port,path:p},res=>{
   let body='';res.on('data',chunk=>body+=chunk);res.on('end',()=>resolve({status:res.statusCode,type:res.headers['content-type'],body}));
  }).on('error',reject);
 });
 try{
  assert.equal((await request('/%E0%A4%A')).status,400);
  assert.equal((await request('/%ZZ')).status,400);
  const page=await request('/');assert.equal(page.status,200);assert.match(page.body,/ShinyDex/);
  const script=await request('/main.js');assert.equal(script.status,200);assert.equal(script.type,'application/javascript');
  assert.equal((await request('/../outside-workspace')).status,403);
  console.log('Verified malformed URLs return 400 without stopping the server; pages/scripts still load and traversal is denied');
 }catch(error){console.error(error);process.exitCode=1;}
 finally{server.close();}
});

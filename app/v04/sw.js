'use strict';
const ROOT=new URL('./',self.location).href;
const META='oratorio-v04-registry:'+ROOT;
const SHELL='oratorio-v04-shell-0.4.0:'+ROOT;
const FILES=['./','index.html','app.js','styles.css','bundle.js','offline.js','boot.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','source-no01-03.txt'];
self.addEventListener('install',e=>e.waitUntil((async()=>{const c=await caches.open(SHELL);await c.addAll(FILES.map(p=>new URL(p,ROOT).href));})()));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
 const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin)return;
 e.respondWith((async()=>{
  const meta=await caches.open(META),res=await meta.match(ROOT+'__registry');let r=null;
  try{r=res?await res.json():null;}catch{}
  for(const rec of [r?.active,r?.previous]){if(rec){const c=await caches.open(rec.cache);const hit=await c.match(e.request);if(hit)return hit;}}
  const shell=await caches.open(SHELL);const hit=await shell.match(e.request);if(hit)return hit;
  try{return await fetch(e.request);}catch(err){
   if(e.request.mode==='navigate'&&u.href.startsWith(ROOT)){const home=await shell.match(ROOT);if(home)return home;}
   throw err;
  }
 })());
});

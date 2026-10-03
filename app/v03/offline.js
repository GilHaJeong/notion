/* Original-planned offline package workflow. Candidate content is never promoted here. */
(()=>{
'use strict';
const ROOT=new URL('./',location.href).href,META='oratorio-v03-registry:'+ROOT,REG=ROOT+'__registry',PREFIX='oratorio-v03-package:'+ROOT;
const $=s=>document.querySelector(s),esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const O={registry:{active:null,previous:null,staging:null},manifest:null,busy:false,supported:false,shellReady:false,activeValid:false,notice:'',error:'',progress:0,done:new Set(),installEvent:null,storage:null};
const names={content:'악보·서사·Cue·후보 시간축 데이터',tenor:'No.1 테너 후보 음원',piano:'No.1 피아노 후보 음원',no01page:'No.1 근거 악보 첫 페이지',no01crop:'No.1 첫 시스템 악보',laodicea:'라오디게아 149쪽 악보'};
const mb=n=>(n/1024/1024).toFixed(2)+' MB';
const same=(a,b)=>a?.id===b?.id&&a?.version===b?.version&&a?.items?.every((x,i)=>x.sha256===b.items?.[i]?.sha256&&x.key===b.items?.[i]?.key)&&a.items.length===b.items.length;
O.itemURL=i=>{const u=new URL(i.url,ROOT);u.searchParams.set('v',i.sha256);return u.href;};
async function readRegistry(){const c=await caches.open(META);const r=await c.match(REG);return r?await r.json():{active:null,previous:null,staging:null};}
async function writeRegistry(r){const c=await caches.open(META);await c.put(REG,new Response(JSON.stringify(r),{headers:{'Content-Type':'application/json'}}));O.registry=r;}
async function sha(buf){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buf)),x=>x.toString(16).padStart(2,'0')).join('');}
function validate(m){
 if(m?.schemaVersion!==1||m?.id!=='internal-no01-laodicea'||typeof m.version!=='string'||m.version.length>80||!Array.isArray(m.items)||m.items.length!==6||m.canonical!==false)throw Error('지원하지 않는 검증 자료 규격입니다.');
 const expected=Object.keys(names),keys=new Set();
 for(const i of m.items){const u=new URL(i.url,ROOT);if(!expected.includes(i.key)||keys.has(i.key)||u.origin!==location.origin||!u.href.startsWith(new URL('../',ROOT).href)||!Number.isSafeInteger(i.bytes)||i.bytes<=0||i.bytes>25*1024*1024||!/^[a-f0-9]{64}$/.test(i.sha256))throw Error('자료 목록·경로·무결성 정보를 확인할 수 없습니다.');keys.add(i.key);}
 return m;
}
O.cachedResponse=async(rec,item)=>{const c=await caches.open(rec.cache);const r=await c.match(O.itemURL(item));if(!r)throw Error('저장 자료가 없습니다.');return r;};
async function verified(response,item){if(!response?.ok)throw Error('파일 응답 오류');const data=await response.arrayBuffer();if(data.byteLength!==item.bytes||await sha(data)!==item.sha256)throw Error('파일 크기 또는 SHA-256 검증 실패');return new Response(data,{headers:{'Content-Type':item.mime||'application/octet-stream'}});}
async function estimate(){try{O.storage=await navigator.storage.estimate();}catch{O.storage=null;}}
O.setWarning=x=>{O.error=x;render();};
function status(){if(!O.supported)return '오프라인 저장 사용 불가';if(O.busy)return '저장 중';if(O.registry.active){if(!O.activeValid)return '저장 자료 확인 필요';if(O.manifest&&!same(O.registry.active.manifest,O.manifest))return '수정본 있음 · 기존 자료 유지';return O.shellReady?'오프라인 사용 가능':'자료 저장됨 · 앱 저장 확인 필요';}if(O.registry.staging)return '일부 저장됨 · 이어받기 가능';return O.error?'저장 실패 · 재시도 가능':'아직 저장하지 않음';}
O.refreshSummary=()=>document.querySelectorAll('[data-offline-summary]').forEach(el=>el.textContent=status());
function render(){
 O.refreshSummary();$('#library-state').textContent=status();$('#library-state').dataset.ready=String(!!O.registry.active&&O.activeValid&&O.shellReady);$('#network-state').textContent=navigator.onLine?'온라인':'오프라인';
 const a=O.registry.active,m=O.manifest||a?.manifest,s=O.registry.staging,total=(m?.items||[]).reduce((n,i)=>n+i.bytes,0);
 $('#library-version').textContent=a?'사용 중 '+a.manifest.version+(m&&!same(a.manifest,m)?' · 새 자료 '+m.version:''):'저장 대상 '+(m?.version||'온라인에서 확인');
 $('#library-space').textContent='필요 자료 '+mb(total)+(O.storage?.quota?' · 브라우저 사용 '+mb(O.storage.usage||0)+' / '+mb(O.storage.quota):' · 저장 공간 정보를 제공하지 않는 브라우저입니다.');
 $('#download-progress').value=!O.busy&&a&&O.activeValid&&same(a.manifest,m)?100:O.progress;$('#library-progress').textContent=O.notice&&!O.busy?O.notice:O.busy?'검증 후 저장 중 · '+O.done.size+'/'+(m?.items.length||6)+'개':a?'파일 검증 후 저장됐습니다. 인터넷을 끊고 재실행해 확인하세요.':s?'확인된 파일은 유지됩니다. 이어받기로 나머지를 저장하세요.':'Wi-Fi에서 자료를 저장하세요. 아직 오프라인 재생을 보장하지 않습니다.';
 $('#library-files').innerHTML=(m?.items||[]).map(i=>'<li><span>'+esc(names[i.key])+'</span><span>'+((O.done.has(i.key)&&(O.busy||s&&same(s.manifest,m)))?'검증 완료':a?.manifest.items.some(x=>x.key===i.key&&x.sha256===i.sha256)?'저장됨':mb(i.bytes))+'</span></li>').join('');
 $('#library-error').hidden=!O.error;$('#library-error').textContent=O.error;
 const blocked=O.busy||!O.supported;
 $('#package-save').disabled=blocked||!m||!navigator.onLine&& !s;
 $('#package-save').textContent=a?(m&&!same(a.manifest,m)?'수정본만 저장':'저장 자료 확인'):s?'중단된 자료 이어받기':'검증 자료 저장';
 $('#package-check').disabled=O.busy||!navigator.onLine;$('#package-rollback').disabled=blocked||!O.registry.previous;
 $('#package-delete').disabled=blocked||!a&&!s;$('#storage-persist').disabled=blocked||!navigator.storage?.persist;
 $('#install-app').hidden=!O.installEvent;const reload=$('#package-apply');reload.hidden=!a||a.manifest.version===window.ORATORIO_RUNTIME_VERSION;reload.disabled=O.busy;
}
O.check=async()=>{
 if(!navigator.onLine)throw Error('수정본 확인은 인터넷 연결이 필요합니다.');
 const r=await fetch(new URL('package.json',ROOT),{cache:'no-store'});if(!r.ok)throw Error('자료 목록을 받지 못했습니다.');
 O.manifest=validate(await r.json());O.error='';await estimate();render();return O.manifest;
};
async function retryFetch(item){let last;for(let n=0;n<3;n++){try{const r=await fetch(O.itemURL(item),{cache:'no-store'});return await verified(r,item);}catch(e){last=e;if(!navigator.onLine)break;await new Promise(r=>setTimeout(r,120*(n+1)));}}throw last;}
async function locked(fn){if(navigator.locks)return navigator.locks.request('oratorio-offline:'+ROOT,fn);return fn();}
function practiceGuard(){if(window.__oratorioReview?.playing)throw Error('연습을 정지한 뒤 자료를 변경해 주세요. 현재 재생 자료는 유지됩니다.');}
O.save=async()=>{
 if(O.busy)return;O.busy=true;O.error='';O.notice='';O.done.clear();O.progress=0;render();
 try{await locked(async()=>{
  practiceGuard();O.registry=await readRegistry();const m=validate(O.manifest||O.registry.staging?.manifest||O.registry.active?.manifest);
  const fingerprint=await sha(new TextEncoder().encode(JSON.stringify(m))),cacheName=PREFIX+fingerprint;
  if(O.registry.staging&&O.registry.staging.cache!==cacheName)await caches.delete(O.registry.staging.cache);
  const staging={cache:cacheName,manifest:m},target=await caches.open(cacheName);await writeRegistry({...O.registry,staging});
  const reusable=[];
  for(const item of m.items){let cached=await target.match(O.itemURL(item));
   if(cached){try{await verified(cached,item);O.done.add(item.key);continue;}catch{await target.delete(O.itemURL(item));}}
   for(const rec of [O.registry.active,O.registry.previous]){if(!rec)continue;const match=rec.manifest.items.find(x=>x.key===item.key&&x.sha256===item.sha256);if(match){try{const r=await verified(await O.cachedResponse(rec,match),item);await target.put(O.itemURL(item),r);O.done.add(item.key);break;}catch{}}}
   if(!O.done.has(item.key))reusable.push(item);
  }
  await estimate();const required=reusable.reduce((n,i)=>n+i.bytes,0);
  if(O.storage?.quota&&O.storage.quota-(O.storage.usage||0)<required*1.2+1024*1024)throw Error('저장 공간이 부족합니다. 브라우저의 불필요한 자료를 정리한 뒤 다시 시도하세요.');
  const total=m.items.reduce((n,i)=>n+i.bytes,0);let finished=m.items.filter(i=>O.done.has(i.key)).reduce((n,i)=>n+i.bytes,0);O.progress=finished/total*100;render();
  for(const item of reusable){const r=await retryFetch(item);await target.put(O.itemURL(item),r);O.done.add(item.key);finished+=item.bytes;O.progress=finished/total*100;render();}
  // Final full verification: pointer is changed only after every file is valid.
  for(const i of m.items)await verified(await target.match(O.itemURL(i)),i);
  const content=await (await target.match(O.itemURL(m.items.find(i=>i.key==='content')))).json();
  if(content.config?.canonical!==false||content.config?.productionApproved!==false||!content.config?.no01||!content.copy)throw Error('후보 자료 경계 또는 콘텐츠 구조 검증 실패');
  practiceGuard();const old=O.registry.active,oldPrevious=O.registry.previous;
  await writeRegistry({active:{cache:cacheName,manifest:m,savedAt:new Date().toISOString()},previous:old&&old.cache!==cacheName?old:oldPrevious,staging:null});
  if(oldPrevious&&oldPrevious.cache!==O.registry.previous?.cache&&oldPrevious.cache!==cacheName)await caches.delete(oldPrevious.cache);
  O.activeValid=true;O.progress=100;O.error='';
 });}catch(e){O.error=(O.registry.active?'새 자료 저장 실패. 기존 자료와 연습 기록을 유지했습니다. ':'')+e.message;}
 finally{O.busy=false;await estimate();render();}
};
O.rollback=async()=>{if(O.busy)return;try{await locked(async()=>{practiceGuard();O.registry=await readRegistry();const r=O.registry.previous;if(!r)return;for(const i of r.manifest.items)await verified(await O.cachedResponse(r,i),i);await writeRegistry({...O.registry,active:r,previous:O.registry.active});O.activeValid=true;O.error='';O.notice='이전 자료로 복구했습니다. 닫고 화면을 새로고침하면 적용됩니다.';});}catch(e){O.error=e.message;}render();};
O.remove=async()=>{if(O.busy)return;practiceGuard();if(!confirm('저장한 검증 자료를 삭제할까요? 연습 기록과 파트 선택은 유지됩니다.'))return;await locked(async()=>{O.registry=await readRegistry();const r=O.registry;await writeRegistry({active:null,previous:null,staging:null});for(const x of [r.active,r.previous,r.staging])if(x)await caches.delete(x.cache);});O.activeValid=false;O.error='';O.notice='자료를 삭제했습니다. 연습 기록은 유지됩니다.';O.progress=0;await estimate();render();};
O.open=async()=>{$('#offline-dialog').showModal();await estimate();render();};
O.init=async()=>{
 try{
  if(!isSecureContext||!('serviceWorker' in navigator)||!('caches' in window))throw Error('HTTPS 또는 localhost에서 열어야 오프라인 저장을 사용할 수 있습니다.');
  await caches.open(META);O.registry=await readRegistry();O.supported=true;
  if(O.registry.active){try{validate(O.registry.active.manifest);for(const i of O.registry.active.manifest.items)await verified(await O.cachedResponse(O.registry.active,i),i);O.activeValid=true;}catch{O.error='저장 자료가 불완전합니다. 온라인에서 다시 저장하세요. 기존 기록은 유지됩니다.';}}
  await navigator.serviceWorker.register('sw.js',{scope:'./'});
  const registration=await Promise.race([navigator.serviceWorker.ready,new Promise((_,reject)=>setTimeout(()=>reject(Error('앱 오프라인 저장 준비 시간이 초과됐습니다.')),10000))]);
  const shell=await caches.open('oratorio-v03-shell-0.3.0:'+ROOT);O.shellReady=!!registration.active;for(const f of ['./','index.html','app.js','styles.css','bundle.js','offline.js','boot.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','source-no01-03.txt'])if(!await shell.match(new URL(f,ROOT).href))O.shellReady=false;
 }catch(e){O.error=e.message;}
 try{await O.check();}catch(e){if(!O.registry.active&&!O.error)O.error=e.message;}
 if(O.registry.staging&&same(O.registry.staging.manifest,O.manifest||O.registry.staging.manifest)){const m=O.registry.staging.manifest;for(const i of m.items){try{await verified(await O.cachedResponse(O.registry.staging,i),i);O.done.add(i.key);}catch{}}O.progress=m.items.filter(i=>O.done.has(i.key)).reduce((n,i)=>n+i.bytes,0)/m.items.reduce((n,i)=>n+i.bytes,0)*100;}
 await estimate();render();
};
$('#library-close').onclick=()=>$('#offline-dialog').close();$('#offline-dialog').addEventListener('click',e=>{if(e.target===$('#offline-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
$('#package-apply').onclick=()=>{try{practiceGuard();location.reload();}catch(e){O.error=e.message;render();}};$('#package-save').onclick=()=>O.save();$('#package-check').onclick=async()=>{try{await O.check();}catch(e){O.error=e.message;render();}};
$('#package-rollback').onclick=()=>O.rollback();$('#package-delete').onclick=async()=>{try{await O.remove();}catch(e){O.error=e.message;render();}};
$('#storage-persist').onclick=async()=>{try{const granted=await navigator.storage.persist();$('#persistence-note').textContent=granted?'브라우저가 자료 보관을 허용했습니다. 사용자가 브라우저 데이터를 지우면 자료는 삭제됩니다.':'브라우저가 보관 요청을 허용하지 않았습니다. 기기 공간을 확인하고 중요한 기록은 별도 보관하세요.';}catch{$('#persistence-note').textContent='자료 보관 요청을 처리하지 못했습니다.';}};
window.addEventListener('online',render);window.addEventListener('offline',render);
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();O.installEvent=e;render();});$('#install-app').onclick=async()=>{if(O.installEvent){await O.installEvent.prompt();await O.installEvent.userChoice;O.installEvent=null;render();}};
window.OratorioOffline=O;
})();

(async()=>{
 await window.OratorioOffline.init();
 const baseline=window.ORATORIO_BASELINE;
 let content=baseline;
 const record=window.OratorioOffline.activeValid?window.OratorioOffline.registry.active:null;
 if(record){try{const item=record.manifest.items.find(i=>i.key==='content');content=await (await window.OratorioOffline.cachedResponse(record,item)).json();}catch{window.OratorioOffline.setWarning('저장 자료를 읽지 못했습니다. 온라인에서 다시 저장해 주세요.');}}
 const manifest=record?.manifest||window.OratorioOffline.manifest;
 const assets={};
 for(const [key,info] of Object.entries(content.config.assets)){
  const item=manifest?.items.find(i=>i.key===key);
  const path=item?window.OratorioOffline.itemURL(item):new URL('../'+info.path,location.href).href;
  assets[key]=path;
 }
 window.ORATORIO_RUNTIME_VERSION=record?.manifest.version||'0.3.0-data.1';window.ORATORIO_BUNDLE={...content,assets};
 const script=document.createElement('script');script.src='app.js';document.body.append(script);
})();

from pathlib import Path
import shutil,json,hashlib
B=Path(__file__).resolve().parent;V3=B if (B/'app/v03').exists() else Path('/data/oratorio_v03');O=B/'app/v04';O.mkdir(parents=True,exist_ok=True);S=B/'source/score-v04'
for f in (V3/'app/v03').iterdir():
 if f.is_file():shutil.copy2(f,O/f.name)
if (V3/'app/assets').resolve()!=(B/'app/assets').resolve():shutil.copytree(V3/'app/assets',B/'app/assets',dirs_exist_ok=True)
for f in S.glob('*.png'):shutil.copy2(f,B/'app/assets/score'/f.name)
audit=json.loads((S/'source-audit.json').read_text());content=json.loads((V3/'app/v03/data/content-v01.json').read_text());C=content['config'];C['build']='unified-internal-v0.4.0';N=content['narrativeReview'];N['scoreAudit']=audit
for key,name in [('no01page','no01-canonical-page7.png'),('no01crop','no01-canonical-page7-system1.png'),('no01page8','no01-page8.png'),('no01crop8','no01-page8-system16.png')]:
 p=B/'app/assets/score'/name;C['assets'][key]={'path':'assets/score/'+name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_pdf_sha256':audit['source']['pdfSha256'],'derived':True}
N['pages']={'7':{'pageKey':'no01page','cropKey':'no01crop','fullSize':[1488,2105],'cropPixels':[60,395,1430,1020],'pdfPage':3,'cropLabel':'1–3마디 시스템'},'8':{'pageKey':'no01page8','cropKey':'no01crop8','fullSize':[1488,2105],'cropPixels':[0,760,1438,1320],'pdfPage':4,'cropLabel':'16–18마디 시스템'}}
(O/'data').mkdir(exist_ok=True);(O/'data/content-v01.json').write_text(json.dumps(content,ensure_ascii=False,separators=(',',':')))
(O/'bundle.js').write_text('window.ORATORIO_BASELINE='+json.dumps(content,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+';')
items=[{'key':'content','url':'data/content-v01.json','bytes':(O/'data/content-v01.json').stat().st_size,'sha256':hashlib.sha256((O/'data/content-v01.json').read_bytes()).hexdigest(),'mime':'application/json'}]
for k,v in C['assets'].items():items.append({'key':k,'url':'../'+v['path'],'bytes':v['bytes'],'sha256':v['sha256'],'mime':'audio/mpeg' if k in ['tenor','piano'] else 'image/png'})
pkg=json.loads((V3/'app/v03/package.json').read_text());pkg.update(version='0.4.0-data.1',items=items,scope='No.1 7·8쪽 / 수동 서사·후보 터치 앵커 / 자동 동기화 아님');(O/'package.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2))
js=(V3/'app/v03/app.js').read_text().replace('내부 검증본 v0.3','내부 검증본 v0.4')
js=js.replace("let practiceMode='midi',narrativeStage='isolation';", "let practiceMode='midi',narrativeStage='isolation',scorePage=7,scoreObserver=null,dragged=false;\n")
js=js.replace("(state.zoom==='크게'&&state.from===1&&state.to<=3?A.no01crop:A.no01page)","scoreImageSource()")
js=js.replace('${n?modeSwitcher():\'\'}<div class="practice-meta">','${n?modeSwitcher()+scorePageControls():\'\'}<div class="practice-meta">')
js=js.replace("if(b.dataset.mode){", "if(b.dataset.scorePage){scorePage=Number(b.dataset.scorePage);updateScore();return;}if(b.dataset.scoreCue){if(dragged)return;narrativeStage=b.dataset.scoreCue==='CUE-N01-01'?'isolation':'revelation';renderNarrative();setMode('narrative');openNarrative(b);return;}\nif(b.dataset.mode){")
js=js.replace("narrativeStage=b.dataset.narrativeStage;renderNarrative();", "narrativeStage=b.dataset.narrativeStage;scorePage=narrativeStage==='revelation'?8:7;renderNarrative();updateScore();")
old="if(b.dataset.zoom){state.zoom=b.dataset.zoom;set('practice.scoreZoom',state.zoom);const was=playing;pause();render();if(was)play();return;}"
new="if(b.dataset.zoom){state.zoom=b.dataset.zoom;set('practice.scoreZoom',state.zoom);if(state.song==='NO01'){document.querySelectorAll('[data-zoom]').forEach(x=>{x.classList.toggle('selected',x===b);x.setAttribute('aria-pressed',String(x===b));});updateScore();return;}const was=playing;pause();render();if(was)play();return;}"
assert old in js;js=js.replace(old,new)
js=js.replace("for(const el of [meta,$('#score-frame'),$('.score-note'),$('.control-bar')])", "for(const el of [$('#score-page-controls'),meta,$('#score-frame'),$('.score-note'),$('.control-bar')])")
js=js.replace("renderNarrative();setMode(practiceMode);}", "renderNarrative();setMode(practiceMode);attachScoreControls();}")
# Replace v03's fixed-page disclaimer with a source/mapping-aware statement.
old="음악은 기존 플레이어에서 듣고 반복합니다. 원문 ${s.printedPages.join('–')}쪽 / 표시 악보 7쪽${s.id==='revelation'?' · 계시 대응 악보 미포함':''}."
new="음악은 기존 플레이어에서 듣고 반복합니다. 원문 ${s.printedPages.join('–')}쪽 · 악보 7·8쪽을 직접 선택할 수 있습니다.${s.id==='revelation'?' 원문 m14 부근 / PDF 가사 진입 m16 · 시작 범위 검토 필요.':''}"
assert old in js;js=js.replace(old,new)
js=js.replace('원문 그대로 표시합니다. 악보·성부·시간축 대조와 해석 승인은 별개입니다.</p><pre', '원문 그대로 표시합니다. 악보·성부·시간축 대조와 해석 승인은 별개입니다.</p>${anchorReview(s)}<pre')
js=js.replace("d._opener=button;d.onclose=()=>{if(d._opener?.isConnected)d._opener.focus({preventScroll:true});};", "d._opener=button;d._cue=button?.dataset.scoreCue;d.onclose=()=>{const target=d._opener?.isConnected?d._opener:d._cue?document.querySelector('[data-score-cue=\"'+d._cue+'\"]'):null;target?.focus({preventScroll:true});};")
js=js.replace("get practiceMode(){", "get scorePage(){return scorePage;},get practiceMode(){")
funcs=r'''
function scoreImageSource(){const p=N.pages[String(scorePage)];return A[state.zoom==='크게'?p.cropKey:p.pageKey];}
function scorePageControls(){return `<div id="score-page-controls" class="score-pages" role="group" aria-label="악보 페이지 · 음악 위치와 별도"><span>읽는 악보</span><button data-score-page="7">인쇄 7쪽</button><button data-score-page="8">인쇄 8쪽</button><span class="caption">페이지를 바꿔도 음악은 이동하지 않습니다.</span></div>`;}
function anchorReview(s){return `<div class="mapping-warning"><strong>악보 앵커 대조 · 좌표 후보</strong><p>${s.id==='revelation'?'원문: m14 부근 / PDF: 인쇄 8쪽 m16 「주의 날에」 성악 진입. 단계 시작과 가사 진입을 구분해 검토합니다. 원문 ff 표기는 No.1 PDF 3·4쪽에서 확인하지 못했습니다.':'PDF 인쇄 7쪽 m1 「너희」, Tenor solo · mp 표시를 앵커로 확인했습니다.'}</p><p class="caption">음표 전체 전사·음원 시간축 검증 및 해석 승인은 별개입니다. 자동 따라가기·Cue 구간 반복은 잠겨 있습니다.</p></div>`;}
function updateScore(){const img=$('#score-image'),frame=$('#score-frame');if(!img||state.song!=='NO01')return;frame.className='score-frame '+(state.zoom==='전체 페이지'?'page-fit':state.zoom==='크게'?'score-large':'score-normal');const source=scoreImageSource();if(img.src!==source)img.src=source;img.alt=`No.1 원본 PDF ${N.pages[String(scorePage)].pdfPage}쪽 · 인쇄 ${scorePage}쪽`;document.querySelectorAll('[data-score-page]').forEach(b=>{const yes=Number(b.dataset.scorePage)===scorePage;b.setAttribute('aria-pressed',String(yes));b.classList.toggle('selected',yes);});$('.score-note').textContent=`읽는 악보: 인쇄 ${scorePage}쪽 / PDF ${N.pages[String(scorePage)].pdfPage}쪽${state.zoom==='크게'?' · '+N.pages[String(scorePage)].cropLabel:''}. Cue 마커는 눈으로 대조한 후보 위치입니다. 재생 커서는 기존 후보 시간축이며 악보와 자동 동기화하지 않습니다.`;requestAnimationFrame(renderScoreAnchors);}
function transformAnchor(a){const p=N.pages[String(scorePage)],r=a.normalizedRect;let rect={...r},marker={...a.markerNormalized};if(state.zoom==='크게'){const [x,y,x2,y2]=p.cropPixels,[w,h]=p.fullSize;rect={x:(r.x*w-x)/(x2-x),y:(r.y*h-y)/(y2-y),width:r.width*w/(x2-x),height:r.height*h/(y2-y)};marker={x:(marker.x*w-x)/(x2-x),y:(marker.y*h-y)/(y2-y)};}return {rect,marker};}
function renderScoreAnchors(){const img=$('#score-image'),wrap=$('.score-image-wrap');if(!img?.complete||!img.naturalWidth||state.song!=='NO01')return;let layer=$('#no01-score-overlay');if(!layer){layer=document.createElement('div');layer.id='no01-score-overlay';layer.className='no01-score-overlay';wrap.append(layer);}const ib=img.getBoundingClientRect(),wb=wrap.getBoundingClientRect(),scale=Math.min(ib.width/img.naturalWidth,ib.height/img.naturalHeight),w=img.naturalWidth*scale,h=img.naturalHeight*scale;layer.style.cssText=`left:${ib.left-wb.left+(ib.width-w)/2}px;top:${ib.top-wb.top+(ib.height-h)/2}px;width:${w}px;height:${h}px`;layer.innerHTML=N.scoreAudit.anchors.filter(a=>a.printedPage===scorePage).map((a,i)=>{const {rect:r,marker:m}=transformAnchor(a);if(r.x+r.width<0||r.y+r.height<0||r.x>1||r.y>1)return '';const mx=Math.min(w-22,Math.max(22,m.x*w)),my=Math.min(h-22,Math.max(22,m.y*h));return `<div class="anchor-box" aria-hidden="true" style="left:${r.x*100}%;top:${r.y*100}%;width:${r.width*100}%;height:${r.height*100}%"></div><button class="no01-score-cue" data-score-cue="${a.cueId}" aria-label="${a.cueId} · 악보 m${a.measure} ${esc(a.lyric)} · 후보 해설 열기" aria-haspopup="dialog" style="left:${mx}px;top:${my}px"><span>${a.cueId.endsWith('01')?'①':'②'}</span></button>`;}).join('');}
function attachScoreControls(){const img=$('#score-image'),frame=$('#score-frame');img.onload=renderScoreAnchors;scoreObserver?.disconnect();scoreObserver=new ResizeObserver(renderScoreAnchors);scoreObserver.observe(img);const points=new Map();frame.addEventListener('pointerdown',e=>{dragged=false;points.set(e.pointerId,[e.clientX,e.clientY]);if(points.size>1)dragged=true;});frame.addEventListener('pointermove',e=>{const p=points.get(e.pointerId);if(p&&Math.hypot(e.clientX-p[0],e.clientY-p[1])>10)dragged=true;});frame.addEventListener('pointerup',e=>points.delete(e.pointerId));frame.addEventListener('pointercancel',e=>{points.delete(e.pointerId);dragged=true;});updateScore();}
'''
js=js.replace("if(state.part!=='none'){state.screen='home';",funcs+"\nif(state.part!=='none'){state.screen='home';")
(O/'app.js').write_text(js)
css=(V3/'app/v03/styles.css').read_text()+r'''
/* v0.4: page-aware candidate anchors, no audio seek on score navigation. */
.score-pages{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:14px 0;font-size:15px}.score-pages .caption{flex-basis:100%;margin:0}.score-pages button{font-size:15px}.narrative-view .score-pages{order:1}.no01-score-overlay{position:absolute;pointer-events:none;line-height:1;z-index:1}.anchor-box{position:absolute;border:1px dashed var(--gold-line);pointer-events:none;border-radius:3px}.no01-score-cue{position:absolute;transform:translate(-50%,-50%);pointer-events:auto;width:44px;min-width:44px;height:44px;min-height:44px;padding:0;border:0;background:transparent;display:grid;place-items:center;touch-action:auto;-webkit-tap-highlight-color:transparent}.no01-score-cue span{background:var(--surface);color:var(--gold);border:1px solid var(--gold-line);border-radius:50%;font-size:22px;line-height:28px;width:28px;height:28px}.no01-score-cue:focus-visible{outline-offset:0}.no01-score-cue:hover span{background:var(--pressed)}.mapping-warning strong{font-size:15px;color:var(--ink)}.mapping-warning p{font-size:15px;line-height:1.75;margin:8px 0}.score-image-wrap{isolation:isolate}
'''
(O/'styles.css').write_text(css)
for f in ['offline.js','sw.js']:
 t=(O/f).read_text().replace('oratorio-v03','oratorio-v04').replace('shell-0.3.0','shell-0.4.0')
 if f=='offline.js':
  t=t.replace("laodicea:'라오디게아 149쪽 악보'","laodicea:'라오디게아 149쪽 악보',no01page8:'No.1 인쇄 8쪽 악보',no01crop8:'No.1 16–18마디 시스템'")
  t=t.replace('m.items.length!==6','m.items.length!==8').replace('m?.items.length||6','m?.items.length||8')
 (O/f).write_text(t)
(O/'boot.js').write_text((O/'boot.js').read_text().replace('0.3.0-data.1','0.4.0-data.1'))
(O/'index.html').write_text((O/'index.html').read_text().replace('내부 검증본 v0.3','내부 검증본 v0.4'))
m=json.loads((O/'manifest.webmanifest').read_text());m['name']='오라토리오 리허설 · 악보 터치 내부 검증본 v0.4';(O/'manifest.webmanifest').write_text(json.dumps(m,ensure_ascii=False,indent=2))
manifest=[{'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(O.rglob('*')) if p.is_file()]+[{'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [(B/'app/assets/score'/n) for n in ['no01-canonical-page7.png','no01-canonical-page7-system1.png','no01-page8.png','no01-page8-system16.png']]]
(B/'v04-file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('v04:',len(items),'package items;',len(manifest),'app/image files; audio unchanged; source crosswalk candidate.')

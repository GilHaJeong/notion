from pathlib import Path
import json,shutil,hashlib,re
B=Path(__file__).resolve().parent;V4=B if (B/'app/v04').exists() else Path('/data/oratorio_v04');O=B/'app/v05';O.mkdir(parents=True,exist_ok=True)
for f in (V4/'app/v04').iterdir():
 if f.is_file():shutil.copy2(f,O/f.name)
if (B/'app/assets').resolve()!=(V4/'app/assets').resolve():shutil.copytree(V4/'app/assets',B/'app/assets',dirs_exist_ok=True)
c=json.loads((V4/'app/v04/data/content-v01.json').read_text());c['config']['build']='unified-internal-v0.5.0';c['config']['playbackPolicy']={'default':'whole','defaultLoop':False,'fullFileOnce':True,'rangePractice':'explicit-only','sourceFormat':'MIDI-level-rendered-MP3','rawSMFVerified':False};(O/'data').mkdir(exist_ok=True);(O/'data/content-v01.json').write_text(json.dumps(c,ensure_ascii=False,separators=(',',':')));(O/'bundle.js').write_text('window.ORATORIO_BASELINE='+json.dumps(c,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+';')
pkg=json.loads((V4/'app/v04/package.json').read_text());p=O/'data/content-v01.json';pkg['version']='0.5.0-data.1';pkg['scope']='No.1 전곡 1회 재생 기본 / 구간 연습 선택 / 후보 음원·수동 서사';pkg['items'][0].update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(O/'package.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2))
s=(V4/'app/v04/app.js').read_text().replace('내부 검증본 v0.4','내부 검증본 v0.5')
s=s.replace("song:'NO01',from:1,to:3,filter:","song:'NO01',from:1,to:21,playbackScope:'whole',filter:").replace("loop:get('practice.loop',true)","loop:false")
s=s.replace('const duration=C.no01.duration_seconds;', 'let duration=C.no01.duration_seconds,ended=false;')
s=s.replace('const range=()=>[sec(state.from),Math.min(duration,sec(state.to+1))];',"const range=()=>state.playbackScope==='whole'?[0,duration]:[sec(state.from),Math.min(duration,sec(state.to+1))];")
s=s.replace('seconds:position(),track:state.track','seconds:position(),track:state.track,playbackScope:state.playbackScope,loop:state.loop')
s=s.replace('return ctx.decodeAudioData(data);}));})();','return ctx.decodeAudioData(data);}));duration=Math.max(...buffers.map(b=>b.duration));if($(\'#seek\'))$(\'#seek\').max=duration;})();')
s=s.replace('const generation=++playGeneration;try{state.audioError=null;', 'const generation=++playGeneration;try{ended=false;state.audioError=null;')
s=s.replace("else if(raw>=b){state.counts[key()]=(state.counts[key()]||0)+1;set('practice.repeatCount',state.counts);pause();offset=b;updateTransport();return;}","else if(raw>=b){if(state.playbackScope==='segment'){state.counts[key()]=(state.counts[key()]||0)+1;set('practice.repeatCount',state.counts);}pause();offset=b;ended=true;persistPosition();updateTransport();return;}")
s=s.replace("$('#play').textContent=playing?txt('practice','aria.pause'):txt('practice','aria.play');", "$('#play').textContent=playing?'일시정지':ended?'처음부터 다시 재생':p>range()[0]+0.05?'이어서 재생':state.playbackScope==='whole'?'전곡 재생':'구간 재생';")
s=s.replace("$('#repeat-count').textContent=`누적 반복 ${state.counts[key()]||0}회`;", "$('#repeat-count').textContent=state.playbackScope==='whole'?(ended?'전곡 1회 재생 완료':playing?'전곡 재생 중 · 반복 없음':p>0?'일시정지 · 현재 위치 유지':'전곡 1회 · 사용자가 중단 가능'):`구간 누적 반복 ${state.counts[key()]||0}회`;")
s=s.replace("function choose(song,from=1,to=3){pause();state.song=song;state.from=from;state.to=to;", "function choose(song,from=1,to=21,scope='whole'){pause();state.song=song;state.from=from;state.to=to;state.playbackScope=scope;state.loop=false;ended=false;")
start=s.index('function home(){');end=s.index('function progress(){',start)
s=s[:start]+'''function home(){const completed=Object.entries(state.progress).filter(([id,x])=>id.startsWith('NO')&&['ready','nearly_stable'].includes(x.status)).length;return `<section class="screen" aria-labelledby="screen-title"><div class="section-heading"><div><p class="eyebrow">먼저 한 곡을 끝까지</p><h2 id="screen-title">전곡을 듣고,<br>필요할 때 멈춥니다.</h2></div><span class="tag">${partName()}</span></div><article class="panel hero"><p class="eyebrow">No.1 · 전곡 후보 음원</p><h3>${C.songs[0].title}</h3><p>전체 1–21마디 · 약 ${fmt(duration)} · ${eligible()?'테너 + 피아노':'피아노 반주만'}</p><p class="caption">MIDI 기반 렌더 음원 · 실제 가창·정본 아님. 1·7·15·18마디/Piano 이벤트 구조 대조가 남아 있습니다.</p><div class="entry-actions"><button class="primary" data-action="full-listen">전곡 듣기</button><button class="secondary" data-open="NO01">곡·음원 정보</button><button class="secondary" data-action="segment-setup">구간 연습</button></div><p class="caption">기본은 처음부터 끝까지 1회 재생입니다. 반복은 꺼져 있으며 사용자가 일시정지·중단할 수 있습니다.</p></article><div class="two-up"><article class="panel"><p class="eyebrow">이어서 듣기</p><h3>${state.last?'No.1 · '+(state.last.playbackScope==='whole'?'전곡':state.last.measureFrom+'–'+state.last.measureTo+'마디'):CP.empty.noHistory}</h3><button class="secondary" data-action="resume" ${!state.last?'disabled':''}>${CP.home['button.resume']}</button></article><article class="panel"><p class="eyebrow">악보 · 해설 검증</p><h3>라오디게아</h3><p>인쇄 149쪽 · L32-03<br>45–53마디 · 음원 미연결</p><button class="secondary" data-open="laodicea">해설 먼저 보기</button></article></div><article class="panel readiness"><div><p class="eyebrow">나의 연습 기록</p><h3>${completed}곡 · 준비됨·거의 안정</h3><p class="caption">직접 남긴 자가 체크입니다. 자료 검수·프로젝트 완료율과 다릅니다.</p></div><button class="secondary" data-route="progress_all">${CP.home['link.allSongs']}</button></article><p class="caption">현재 재생 가능한 전곡 후보는 No.1입니다. 전체 36곡 음원은 아직 연결되지 않았습니다. 자료함에 저장하면 오프라인으로 다시 열 수 있습니다.</p></section>`;}
''' +s[end:]
# Keep detail as an optional information/range setup screen, with whole-first choices.
s=s.replace('${[[1,3],[4,6],[1,21]].map', '${[[1,21],[1,3],[4,6]].map')
s=s.replace('<strong>${a}–${b}마디</strong>',"<strong>${a===1&&b===21?'전곡 · 1–21마디':a+'–'+b+'마디'}</strong>")
s=s.replace("txt('songDetail','primary.practiceSelected',{from:state.from,to:state.to})", "(state.playbackScope==='whole'?'전곡 재생 화면 열기':state.from+'–'+state.to+'마디 연습 화면 열기')")
s=s.replace("modeSwitcher()+scorePageControls()", "modeSwitcher()+scorePageControls()")
s=s.replace('<div class="control-bar"><div class="range-row">','<div class="control-bar">${n?playbackScopeControls():\'\'}<div class="range-row ${n&&state.playbackScope===\'whole\'?\'whole-range\':\'\'}">')
s=s.replace('${n?`<label>시작 마디', '${n?`${state.playbackScope===\'segment\'?`<label>시작 마디')
s=s.replace('</select></label><label>트랙<select id="track">', '</select></label>`:`<div class="full-scope-summary"><strong>No.1 전곡 · 1–21마디</strong><p class="caption">파일 전체를 1회 재생합니다. 반복 없음 · 일시정지/중단 가능</p></div>`}<label>트랙<select id="track">')
s=s.replace('${CP.practice[\'aria.play\']}</button><button class="secondary" data-action="stop"', "전곡 재생</button><button class=\"secondary\" data-action=\"stop\"")
s=s.replace('>정지</button><button id="loop"', '>중단 · 처음으로</button><button id="loop"')
s=s.replace("aria-pressed=\"${state.loop}\" ${!n?'disabled':''}", "aria-pressed=\"${state.loop}\" ${!n||state.playbackScope==='whole'?'disabled':''}")
s=s.replace('<p id="audio-error" class="error" hidden>', '<p class="caption audio-disclosure">${n?\'MIDI 기반 후보 렌더 음원입니다. 실제 가창·정본 검수·음악–악보 싱크 승인 전이며, 1·7·15·18마디/Piano 이벤트 구조 문제는 미해결입니다.\':\'이 구간 음원은 아직 연결되지 않았습니다.\'}</p><p id="audio-error" class="error" hidden>')
s=s.replace("if(b.dataset.mode){", "if(b.dataset.playbackScope){setPlaybackScope(b.dataset.playbackScope);return;}\nif(b.dataset.mode){")
s=s.replace("choose(b.dataset.open,b.dataset.open==='NO01'?1:45,b.dataset.open==='NO01'?3:53)", "choose(b.dataset.open,b.dataset.open==='NO01'?1:45,b.dataset.open==='NO01'?21:53)")
s=s.replace("if(b.dataset.segment){[state.from,state.to]=b.dataset.segment.split(',').map(Number);offset=sec(state.from);render();return;}", "if(b.dataset.segment){[state.from,state.to]=b.dataset.segment.split(',').map(Number);state.playbackScope=state.from===1&&state.to===21?'whole':'segment';state.loop=false;ended=false;offset=sec(state.from);render();return;}")
s=s.replace("switch(b.dataset.action){case 'library':", "switch(b.dataset.action){case 'full-listen':choose('NO01',1,21,'whole');route('practice');play();break;case 'segment-setup':choose('NO01',1,3,'segment');route('song_detail');break;case 'library':")
s=s.replace("case 'stop':pause();offset=range()[0];", "case 'stop':pause();ended=false;offset=range()[0];")
s=s.replace("case 'loop':{const was=playing;", "case 'loop':{if(state.playbackScope==='whole')return;const was=playing;")
s=s.replace("choose('NO01',l.measureFrom,l.measureTo);", "choose('NO01',l.measureFrom,l.measureTo,l.playbackScope||((l.measureFrom===1&&l.measureTo===21)?'whole':'segment'));if(state.playbackScope==='segment')state.loop=l.playbackScope==='segment'&&l.loop===true;")
s=s.replace("const val=Number(el.value);", "ended=false;const val=Number(el.value);")
s=s.replace("pause();offset=Math.max(range()[0],Math.min(requested", "pause();ended=false;offset=Math.max(range()[0],Math.min(requested")
s=s.replace("window.__oratorioReview={state,", "window.__oratorioReview={state,get ended(){return ended;},get duration(){return duration;},get decodedDurations(){return buffers?.map(b=>b.duration)||[];},")
funcs='''function playbackScopeControls(){return `<div class="playback-scopes" role="group" aria-label="재생 방식"><button data-playback-scope="whole" class="${state.playbackScope==='whole'?'selected':''}" aria-pressed="${state.playbackScope==='whole'}">전곡 1회</button><button data-playback-scope="segment" class="${state.playbackScope==='segment'?'selected':''}" aria-pressed="${state.playbackScope==='segment'}">구간 연습</button></div>`;}
function setPlaybackScope(scope){if(scope===state.playbackScope)return;pause();state.playbackScope=scope;state.loop=false;ended=false;if(scope==='whole'){state.from=1;state.to=21;}else{state.from=1;state.to=3;}offset=range()[0];render();persistPosition();}
'''
s=s.replace('function modeSwitcher(){',funcs+'function modeSwitcher(){')
s=s.replace('scoreObserver.observe(img);const points=', "scoreObserver.observe(img);frame.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')dragged=false;});const points=")
(O/'app.js').write_text(s)
css=(V4/'app/v04/styles.css').read_text()+'''\n/* Whole-file playback is primary; range practice is opt-in. */
.entry-actions{display:flex;gap:8px;flex-wrap:wrap}.playback-scopes{display:flex;gap:8px;margin-bottom:18px}.playback-scopes button{flex:1}.whole-range{grid-template-columns:1.3fr 1fr}.full-scope-summary{align-self:center}.full-scope-summary p{margin:8px 0 0}.audio-disclosure{border-top:1px solid var(--border);padding-top:12px}@media(max-width:600px){.whole-range{grid-template-columns:1fr}.entry-actions{display:grid;grid-template-columns:1fr}.entry-actions button{width:100%}}
''';(O/'styles.css').write_text(css)
for name in ['offline.js','sw.js','boot.js','index.html','manifest.webmanifest']:
 t=(O/name).read_text().replace('oratorio-v04','oratorio-v05').replace('0.4.0','0.5.0').replace('v0.4','v0.5');(O/name).write_text(t)
m=[{'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(O.rglob('*')) if p.is_file()];(B/'v05-file-manifest.json').write_text(json.dumps(m,indent=2));print('Built',len(m),'v05 files. Existing two audio stems unchanged.')

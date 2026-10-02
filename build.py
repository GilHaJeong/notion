import json,pathlib,base64,hashlib
b=pathlib.Path(__file__).resolve().parent;app=b/'app'
config=json.loads((app/'data/integration.json').read_text());copy=json.loads((app/'data/copy.json').read_text());assets={}
for key,info in config['assets'].items():
 p=app/info['path'];mime='audio/mpeg' if p.suffix=='.mp3' else 'image/png';assets[key]=f'data:{mime};base64,'+base64.b64encode(p.read_bytes()).decode()
bundle={'config':config,'copy':copy,'assets':assets};js=(app/'app.js').read_text();css=(app/'styles.css').read_text()
html='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>오라토리오 · 단일 통합 웹앱 내부 검증본 v0.1</title><style>'''+css+'''</style></head><body><div class="texture-stack" aria-hidden="true"><div class="texture-layer"></div><div class="texture-layer"></div><div class="texture-layer"></div></div><p class="orientation">태블릿을 세로로 세우시면 악보가 크게 보입니다. 가로로도 보실 수 있습니다.</p><p id="storage-notice" class="global-notice" hidden>저장 기능을 사용할 수 없습니다. 이 창에서만 기록이 유지됩니다.</p><p id="phone-notice" class="global-notice phone-notice" hidden>스마트폰은 음원 청취 보조용입니다. 악보 연습은 태블릿을 권합니다.</p><main id="app" class="app-shell"></main><p id="toast" role="status" hidden></p><noscript>이 검증본은 JavaScript가 필요합니다.</noscript><script>window.ORATORIO_BUNDLE='''+json.dumps(bundle,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+''';</script><script>'''+js+'''</script></body></html>'''
(app/'index.html').write_text(html)
print('독립 HTML 생성',len(html.encode()),'bytes',hashlib.sha256(html.encode()).hexdigest())

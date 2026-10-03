import urllib.request,json,hashlib,time,pathlib,concurrent.futures
B=pathlib.Path('/data/oratorio_v04');sha=json.load(open(B/'commit.json'))['sha'];files=json.load(open(B/'github-upload-files.json'))
def verify(x):
 r=urllib.request.urlopen(f'https://raw.githubusercontent.com/GilHaJeong/notion/{sha}/'+x['path']).read();return {'path':x['path'],'matches':hashlib.sha256(r).digest()==hashlib.sha256(pathlib.Path(x['source']).read_bytes()).digest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:checks=list(ex.map(verify,files))
assert all(x['matches'] for x in checks);print('repo',len(checks),'SHA256 match',flush=True)
for _ in range(36):
 runs=json.load(urllib.request.urlopen('https://api.github.com/repos/GilHaJeong/notion/actions/runs?head_sha='+sha+'&per_page=5'));run=runs['workflow_runs'][0]
 if run['status']=='completed':break
 time.sleep(5)
assert run['conclusion']=='success',run
print('Pages success:',run['html_url'],flush=True)
manifest=json.load(open(B/'v04-file-manifest.json'))
def live(x):
 data=urllib.request.urlopen('https://gilhajeong.github.io/notion/'+x['path']+'?v='+sha).read();return {'path':x['path'],'matches':hashlib.sha256(data).hexdigest()==x['sha256']}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:prod=list(ex.map(live,manifest))
assert all(x['matches'] for x in prod)
legacy=[]
for path in ['app/index.html','app/v02/index.html','app/v03/index.html','app/assets/audio/no01-tenor.mp3','app/assets/audio/no01-piano.mp3']:
 try:
  before=urllib.request.urlopen('https://raw.githubusercontent.com/GilHaJeong/notion/f02f6c769a0c25551dd9bd3f46588d159addd148/'+path).read();after=urllib.request.urlopen(f'https://raw.githubusercontent.com/GilHaJeong/notion/{sha}/'+path).read();legacy.append({'path':path,'unchanged':hashlib.sha256(before).digest()==hashlib.sha256(after).digest()})
 except Exception as e:legacy.append({'path':path,'error':str(e)})
report={'sha':sha,'commit':'https://github.com/GilHaJeong/notion/commit/'+sha,'pagesRun':run['html_url'],'repository':checks,'deployment':prod,'legacy':legacy};(B/'qa/deployment-report.json').write_text(json.dumps(report,indent=2));print('deployed',len(prod),'SHA256 match; legacy:',legacy,flush=True)

from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,json
root=Path('/data/oratorio_v04');os.chdir(root)
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  state=root/'qa/fail-state.json'
  mode=json.loads(state.read_text()) if state.exists() else {}
  if mode.get('match') and mode['match'] in self.path:
   log=root/'qa/fail-log.jsonl'
   with log.open('a') as f:f.write(json.dumps({'path':self.path})+'\n')
   self.send_response(200);self.end_headers();self.wfile.write(b'corrupt-QA-response');return
  if self.path.startswith('/qa/control'):
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({'ok':True}).encode());return
  return super().do_GET()
 def log_message(self,*args):pass
ThreadingHTTPServer(('127.0.0.1',8775),Handler).serve_forever()

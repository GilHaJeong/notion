import http from 'node:http';
import { DialogueSession } from './protocol.mjs';

const session = new DialogueSession({
  sessionId: process.env.SESSION_ID ?? 'aml-live-001',
  participants: [
    { id: 'astra', provider: 'openai', role: 'coordinator' },
    { id: 'grok', provider: 'xai', role: 'skeptic' },
    { id: 'gemini', provider: 'google', role: 'historian' }
  ]
});

const clients = new Set();
const port = Number(process.env.PORT ?? 8787);

function sendJson(res, status, data) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' });
  res.end(JSON.stringify(data));
}

function broadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of clients) res.write(payload);
}

async function body(req) {
  let raw = '';
  for await (const chunk of req) raw += chunk;
  return raw ? JSON.parse(raw) : {};
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'OPTIONS') {
      res.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET,POST,OPTIONS', 'access-control-allow-headers': 'content-type' });
      return res.end();
    }
    if (req.method === 'GET' && req.url === '/state') return sendJson(res, 200, session.exportState());
    if (req.method === 'GET' && req.url === '/events') {
      res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', 'connection': 'keep-alive', 'access-control-allow-origin': '*' });
      res.write(`event: state\ndata: ${JSON.stringify(session.exportState())}\n\n`);
      clients.add(res);
      req.on('close', () => clients.delete(res));
      return;
    }
    if (req.method === 'POST' && req.url === '/turn') {
      const turn = session.appendTurn(await body(req));
      broadcast('turn', turn);
      return sendJson(res, 201, turn);
    }
    if (req.method === 'POST' && req.url === '/reaction') {
      const reaction = session.addReaction(await body(req));
      broadcast('reaction', reaction);
      return sendJson(res, 201, reaction);
    }
    if (req.method === 'POST' && req.url === '/user-reaction') {
      const reaction = session.addUserReaction(await body(req));
      broadcast('user-reaction', reaction);
      return sendJson(res, 201, reaction);
    }
    sendJson(res, 404, { error: 'not_found' });
  } catch (error) {
    sendJson(res, 400, { error: error.message });
  }
});

server.listen(port, () => console.log(`AML live server listening on http://localhost:${port}`));

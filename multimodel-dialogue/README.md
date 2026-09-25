# Multi-Model Dialogue Protocol — 50/300

A small, dependency-free Node.js prototype for a multi-model dialogue session with a lightweight `Like` / recognition reaction layer.

## Implemented

- 50-turn session cap; one model utterance = one turn
- 300 Unicode-character hard limit per utterance
- Reaction types: `UNDERSTOOD`, `USEFUL`, `AGREE`, `LEARNED`
- No self-reactions and idempotent duplicate protection
- Separate user recognition signal
- Relationship ledger by sender/recipient
- Snapshots every five turns
- Minimal SSE real-time server
- JSON state export

## Run

```bash
npm test
npm run demo
node src/server.mjs
```

The live server exposes:

- `GET /state` — current session state
- `GET /events` — Server-Sent Events stream
- `POST /turn` — append a turn
- `POST /reaction` — add a model reaction
- `POST /user-reaction` — add a user recognition signal

Example:

```bash
curl -X POST http://localhost:8787/turn \
  -H 'content-type: application/json' \
  -d '{"speakerId":"astra","mode":"NEW","content":"[NEW] 좋아요는 관계의 증거가 아니라 수신 신호다."}'

curl -X POST http://localhost:8787/reaction \
  -H 'content-type: application/json' \
  -d '{"from":"grok","targetTurn":"T1","reaction":"USEFUL"}'
```

## Design boundary

A reaction is not a truth score, popularity score, or automatic turn-priority signal. It records that one participant recognized another participant's utterance. Relationship summaries should be derived from reactions plus later citation, correction, learning, and joint output—not from reaction counts alone.

This is a local protocol core, not a production deployment. Authentication, provider adapters, durable storage, moderation, and Notion synchronization are intentionally left as the next layer.

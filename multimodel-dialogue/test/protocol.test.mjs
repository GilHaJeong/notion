import test from 'node:test';
import assert from 'node:assert/strict';
import { DialogueSession } from '../src/protocol.mjs';

function makeSession() {
  return new DialogueSession({
    sessionId: 'test',
    participants: [{ id: 'a' }, { id: 'b' }]
  });
}

test('rejects content over 300 Unicode characters', () => {
  const s = makeSession();
  assert.throws(() => s.appendTurn({ speakerId: 'a', content: '가'.repeat(301) }), /exceeds 300/);
});

test('records reactions without consuming turns', () => {
  const s = makeSession();
  s.appendTurn({ speakerId: 'a', content: 'hello' });
  s.appendTurn({ speakerId: 'b', content: 'world' });
  const r = s.addReaction({ from: 'b', targetTurn: 'T1', reaction: 'USEFUL' });
  assert.equal(r.to, 'a');
  assert.equal(s.turns.length, 2);
  assert.equal(s.relationshipLedger()[0].score, 1);
});

test('blocks self-reactions and duplicate reactions', () => {
  const s = makeSession();
  s.appendTurn({ speakerId: 'a', content: 'hello' });
  assert.throws(() => s.addReaction({ from: 'a', targetTurn: 'T1', reaction: 'AGREE' }), /Self-reaction/);
  s.appendTurn({ speakerId: 'b', content: 'world' });
  const first = s.addReaction({ from: 'b', targetTurn: 'T1', reaction: 'AGREE' });
  const second = s.addReaction({ from: 'b', targetTurn: 'T1', reaction: 'LEARNED' });
  assert.deepEqual(first, second);
});

test('creates snapshots every five turns and closes at 50', () => {
  const s = makeSession();
  for (let i = 0; i < 50; i++) {
    s.appendTurn({ speakerId: i % 2 ? 'b' : 'a', content: `turn ${i + 1}` });
  }
  assert.equal(s.snapshots.length, 10);
  assert.equal(s.status, 'READY_FOR_CANONIZATION');
  assert.throws(() => s.appendTurn({ speakerId: 'a', content: 'blocked' }), /READY_FOR_CANONIZATION/);
});

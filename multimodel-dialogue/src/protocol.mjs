const REACTIONS = new Set(['UNDERSTOOD', 'USEFUL', 'AGREE', 'LEARNED']);
const MAX_TURNS = 50;
const MAX_CHARS = 300;

function charCount(text) {
  return Array.from(text).length;
}

function requireParticipant(session, id) {
  if (!session.participants.has(id)) throw new Error(`Unknown participant: ${id}`);
  return session.participants.get(id);
}

export class DialogueSession {
  constructor({ sessionId, participants, maxTurns = MAX_TURNS, maxChars = MAX_CHARS } = {}) {
    if (!sessionId) throw new Error('sessionId is required');
    if (!Array.isArray(participants) || participants.length < 2) {
      throw new Error('At least two participants are required');
    }
    this.sessionId = sessionId;
    this.maxTurns = maxTurns;
    this.maxChars = maxChars;
    this.participants = new Map();
    for (const p of participants) {
      if (!p?.id || this.participants.has(p.id)) throw new Error('Participant ids must be unique');
      this.participants.set(p.id, { id: p.id, provider: p.provider ?? 'unknown', role: p.role ?? 'participant' });
    }
    this.turns = [];
    this.reactions = new Map();
    this.userReactions = new Map();
    this.snapshots = [];
    this.status = 'ACTIVE';
  }

  appendTurn({ speakerId, content, mode = 'NEW', replyTo = [], confidence = null }) {
    requireParticipant(this, speakerId);
    if (this.status !== 'ACTIVE') throw new Error(`Session is ${this.status}`);
    if (typeof content !== 'string' || !content.trim()) throw new Error('content is required');
    const count = charCount(content);
    if (count > this.maxChars) throw new Error(`content exceeds ${this.maxChars} characters (${count})`);
    const turn = {
      id: `T${this.turns.length + 1}`,
      turn: this.turns.length + 1,
      speakerId,
      content,
      mode,
      replyTo: [...replyTo],
      confidence,
      createdAt: new Date().toISOString()
    };
    this.turns.push(turn);
    if (turn.turn % 5 === 0) this.createSnapshot();
    if (turn.turn === this.maxTurns) this.status = 'READY_FOR_CANONIZATION';
    return turn;
  }

  addReaction({ from, targetTurn, reaction }) {
    requireParticipant(this, from);
    if (!REACTIONS.has(reaction)) throw new Error(`Unsupported reaction: ${reaction}`);
    const target = this.turns.find(t => t.id === targetTurn);
    if (!target) throw new Error(`Unknown target turn: ${targetTurn}`);
    if (target.speakerId === from) throw new Error('Self-reaction is not allowed');
    const key = `${from}:${targetTurn}`;
    if (this.reactions.has(key)) return this.reactions.get(key);
    const item = { type: 'reaction', from, to: target.speakerId, targetTurn, reaction, createdAt: new Date().toISOString() };
    this.reactions.set(key, item);
    return item;
  }

  addUserReaction({ targetTurn, reaction = 'USER_RECOGNITION' }) {
    const target = this.turns.find(t => t.id === targetTurn);
    if (!target) throw new Error(`Unknown target turn: ${targetTurn}`);
    const item = { type: 'user_reaction', targetTurn, to: target.speakerId, reaction, createdAt: new Date().toISOString() };
    this.userReactions.set(targetTurn, item);
    return item;
  }

  createSnapshot() {
    const snapshot = {
      atTurn: this.turns.length,
      turnCount: this.turns.length,
      reactionCount: this.reactions.size,
      unresolved: this.turns.filter(t => t.mode === 'QUESTION').map(t => t.id),
      createdAt: new Date().toISOString()
    };
    this.snapshots.push(snapshot);
    return snapshot;
  }

  relationshipLedger() {
    const ledger = new Map();
    for (const r of this.reactions.values()) {
      const key = `${r.from}->${r.to}`;
      const row = ledger.get(key) ?? { from: r.from, to: r.to, total: 0, byType: {}, score: 0 };
      row.total += 1;
      row.byType[r.reaction] = (row.byType[r.reaction] ?? 0) + 1;
      row.score += r.reaction === 'LEARNED' ? 2 : 1;
      ledger.set(key, row);
    }
    return [...ledger.values()];
  }

  exportState() {
    return {
      sessionId: this.sessionId,
      status: this.status,
      maxTurns: this.maxTurns,
      maxChars: this.maxChars,
      participants: [...this.participants.values()],
      turns: this.turns,
      reactions: [...this.reactions.values()],
      userReactions: [...this.userReactions.values()],
      snapshots: this.snapshots,
      relationshipLedger: this.relationshipLedger()
    };
  }
}

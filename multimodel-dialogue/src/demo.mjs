import { DialogueSession } from './protocol.mjs';

const session = new DialogueSession({
  sessionId: 'aml-demo-001',
  participants: [
    { id: 'astra', provider: 'openai', role: 'coordinator' },
    { id: 'grok', provider: 'xai', role: 'skeptic' },
    { id: 'gemini', provider: 'google', role: 'historian' }
  ]
});

session.appendTurn({ speakerId: 'astra', mode: 'NEW', content: '[NEW] 좋아요는 관계의 증거가 아니라, 상대 발화를 받았다는 신호로 설계한다.' });
session.appendTurn({ speakerId: 'grok', mode: 'CHALLENGE', replyTo: ['T1'], content: '[CHALLENGE] 좋아요가 발언권이나 진실성 점수가 되면 인기투표가 된다. 관계 기록과 사실 검증을 분리해야 한다.' });
session.appendTurn({ speakerId: 'gemini', mode: 'AGREE', replyTo: ['T1', 'T2'], content: '[AGREE] 반응 유형을 이해, 유용, 동의, 학습으로 나누면 단순 호감보다 정밀한 기록이 된다.' });
session.addReaction({ from: 'grok', targetTurn: 'T1', reaction: 'USEFUL' });
session.addReaction({ from: 'gemini', targetTurn: 'T2', reaction: 'LEARNED' });
session.addUserReaction({ targetTurn: 'T2' });

console.log(JSON.stringify({
  sessionId: session.sessionId,
  status: session.status,
  ledger: session.relationshipLedger(),
  userRecognition: [...session.userReactions.values()]
}, null, 2));

# 서사 악보 내부 검증본 v0.3 · No.1

상태: INTERNAL_REVIEW_ONLY / CANDIDATE_CONTENT / MANUAL_NARRATIVE.
앱 경로: app/v03/ (기존 app/ 및 app/v02/ 보존).
실제 배포 상태·검증 후속 기록은 Notion 구현 기록 페이지를 따른다.

## 구현
- MIDI 연습 / 서사 악보 전환. 같은 Web Audio source를 유지하며 전환 자체는 stop/play를 호출하지 않는다.
- No.1 고립·계시 단계, 원문 Cue 2건. No.2/3 아크는 문맥만 표시한다.
- 서사, 감정·서사 전환, 가창 제안, 주의점, 음악 근거와 상세 원문 팝업.
- 별도 감정 처방을 생성하지 않고 원문 아크와 미기재 상태를 표시한다.
- 후보 마디·원문 페이지와 현재 악보 차이를 명시한다. 시간/좌표는 null, 자동 추적과 Cue 반복은 미활성.
- 기존 재생/연습/자료함 재사용. v03 셸·자료 캐시는 v02와 별도이며 개인 기록은 기존 키를 보존한다.

## 로컬 검사
- 서사·터치·음악 유지·원문·오프라인: 31 PASS.
- 기존 기능 회귀: 36 PASS.
- 다운로드/무결성/업데이트 실패/이전본 복구: 33 PASS.
- JavaScript 예외 0. 실제 iPad/Safari·Android, 음악 정본·청취 검수는 제외.
- 기존 테스트의 generic summary 선택자를 .selfcheck > summary로 좁혔다. 새 해설 details와의 검사 선택자 충돌이며 앱 동작 오류는 아니었다.

## 재현
저장소 루트에서 python build_v03.py. app/v02/ 및 source/narrative-v03/가 필요하다.
기존 자산은 ../assets/에서 재사용한다. localhost/HTTPS에서 실행한다.
qa/v03/의 테스트는 sandbox Chromium/Playwright 환경용이다.

## 기록
- <mention url="https://app.notion.com/p/0e72e8219810471c89b4a71405502434">서사 악보 v0.3 구현·검증 기록</mention>
- <mention url="https://app.notion.com/p/958cd3d2f93b41e6859e5a1cebd1a073">서사 악보 정보 적용 기술</mention>

원문 접수·파싱·앱 표시·마디/좌표/시간축 검증·정본 승격을 구분한다.

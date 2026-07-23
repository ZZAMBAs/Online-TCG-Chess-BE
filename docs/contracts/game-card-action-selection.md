# Game Card Action Selection BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### command와 상태 전이

- 공통 command envelope의 `actionId`, `gameId`, `intent`, `baseStateVersion`과 멱등 규칙은 fixed game-state-sync를 유지한다.
- 선택형 카드 발동의 wire literal은 단일 `CARD_ACTIVATE`이고 닫힌 `{cardInstanceId}` payload를 사용한다. PRE_MOVE/POST_MOVE 허용 여부는 서버의 현재 권위 phase로 판정한다. 효과 해결은 `CARD_RESOLVE`와 닫힌 `{activationId,selection}` payload를 사용한다.
- 무대상 카드는 `CARD_ACTIVATE` 한 command와 한 transition 안에서 발동과 효과 결과를 순서대로 확정한다.
- client는 card ID/version, actor color, 비용, 효과, handler, 후보 계산 결과를 제출하지 않는다.
- `CARD_ACTIVATE` 발동 전 검증 실패는 actor-private application error이며 카드·마나·행동 슬롯·패·공개 상태·stateVersion을 바꾸지 않는다.
- 선택형 발동 성공은 카드·마나·행동 슬롯 소비, 패 제거, 공개·레전드 사용 완료와 `EFFECT_PENDING`을 새 transition으로 확정한다.
- malformed `CARD_RESOLVE`는 pending과 version을 유지하는 application error다. well-formed 후보 밖 selection과 효과 적용 불가는 소비를 유지하는 새 `CARD_EFFECT_FAILED` transition이다.
- 선택형 resolve는 `CARD_EFFECT_APPLIED` 또는 `CARD_EFFECT_FAILED`를 별도 transition으로 확정하며, 무대상 카드는 `CARD_ACTIVATED` 뒤 효과 결과를 같은 transition의 ordered event로 기록한다.

### projection, pending과 보드 perspective

- public projection은 발동 카드 ID/version, actor color, 소비·사용 완료, public pending 여부, generic 효과 결과와 관찰 가능한 outcome만 포함한다.
- `cardInstanceId`, `activationId`, 후보, cardinality/distinct/ordered 제약, raw selection과 상세 실패 사유는 actor-private다.
- actor reconnect snapshot은 동일 activation, 고정 card ID/version과 후보를 복원한다. opponent snapshot은 public pending만 복원한다.
- viewer snapshot은 해당 참가자의 `ownColor`를 포함한다. FE store는 canonical `a1~h8` 좌표만 유지하고 렌더링·포인터 입력 경계에서 자신의 home rank가 아래쪽인 `BoardPerspective`를 적용한다.
- `CARD_006`의 unordered selection은 검증·멱등 비교 전에 canonicalize한다.
- pending 중 시간·disconnect·game end 경쟁은 기존 경기별 직렬화 경계를 사용하며 종료가 먼저 확정되면 pending을 폐기한다.

### 카드별 제품 규칙

- selection 기준은 `001: pawn+direction`, `002/003: pawn`, `004: no-input`, `005: rook`, `006: unordered distinct opponent pieces 2`, `007~011: from+to`, `012: 서버 최단거리 후보 중 사용자 target 1개`다.
- 방향은 카드 사용자 진영 기준이다. White는 `LEFT(-1,0)`, `RIGHT(+1,0)`, `FORWARD_LEFT(-1,+1)`, `FORWARD_RIGHT(+1,+1)`이고 Black은 반대다.
- `CARD_004`는 막힌 폰을 제외한 eligible pawn만 동시에 전진하며 eligible 0개면 발동 전 비소모 거부한다.
- `CARD_006`은 왕·퀸을 제외한 서로 다른 두 상대 기물을 순서 없이 교환하고 관련 캐슬링·앙파상 권리를 제거하며 프로모션하지 않는다.
- `CARD_012`는 상대 킹을 제외한 최단거리 후보 중 사용자가 하나를 선택한다. 후보가 없으면 비소모 거부하고 후보 밖 선택·전환 불가는 소비 유지 효과 실패다.
- 카드 효과는 50수 규칙 횟수를 추가 증가시키지 않는다. 폰 이동·캡처는 초기화하고 그 외 변화와 효과 실패는 유지한다.

### version, catalog와 replay

- `docs/cards` versioned JSON은 작성·배포 원천이고 `active-versions.json`이 카드별 신규 경기 버전을 하나씩 지정한다.
- RDB에는 검증·배포된 모든 불변 버전과 현재 활성 버전을 보존한다. 활성 버전은 새 배포에서만 바뀌고 신규 경기가 ID/version/fingerprint를 고정한다.
- collection/deck client는 실행 version을 선택하지 않는다. 진행 경기와 기보 표시는 서버가 제공한 pinned/historical version 정의를 사용한다.
- 활성화·롤백 가능한 모든 버전은 handler, activation/resolve selection schema, public/private outcome과 fixture에 정확히 하나씩 연결한다.
- 과거 기보는 최신 handler를 재실행하지 않고 저장된 ordered 권위 outcome을 조회자별로 projection한다.
- historical replay REST의 구체적인 표시·privacy 계약은 후속 match-history topic이 소유한다.
- 실제 command/event/snapshot JSON Schema, pinned definition 전달 방식, generated union, fixture manifest와 fingerprint 전달은 후속 `contract-fixture` topic이 소유하며 그 topic fixed 전에는 FE/BE 카드 구현을 시작하지 않는다.

## 오류 포맷과 사용자 표시 영향

- fixed schema 전에는 selection UI, reducer variant, MSW/fake STOMP/Playwright fixture와 임의 mock 구현을 시작하지 않는다.
- 권위 public transition, private augmentation, local selection draft와 pending overlay를 분리한다.
- 카드별 선택 interaction과 public/private outcome을 exhaustive generated type으로 처리한다.

## 구현 메모

- fixed catalog 전에는 자유형 handler, effect/outcome Map이나 임시 schema로 gameplay 구현을 시작하지 않는다.
- catalog와 handler/version registry, 공통 불변식 validator, public/private allowlist serializer와 fixture gate를 이후 구현 입력으로 사용한다.

## 테스트/fixture/드리프트 검증

- catalog 완결성: 12장 각각 handler, selection, outcome, fixture 연결과 version 일치
- selection: discriminator, 누락·추가 field, 다른 카드 variant 교차 사용, 대상 cardinality·순서·중복, 유효·무효 후보
- domain: phase·마나·조건, 킹/체스 불변식, 원자 rollback, idempotency, 종료 경쟁
- projection: public allowlist, viewer-private 후보·selection, 레전드와 숨은 정보 privacy-negative
- FE: 선택·취소·재선택·확정, 성공/실패, receipt/transition 순서, MSW/fake STOMP/Playwright
- drift gate: catalog, generated union, handler registry, schema와 fixture fingerprint 불일치 차단

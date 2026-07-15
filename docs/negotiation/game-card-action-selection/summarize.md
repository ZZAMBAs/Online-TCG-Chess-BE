# Game Card Action Selection Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/game-card-action-selection/20260713-170103.md`, `docs/negotiation/game-card-action-selection/20260713-170413.md`, `docs/negotiation/game-card-action-selection/20260713-171108.md`, `docs/negotiation/game-card-action-selection/20260714-101746.md`, `docs/negotiation/game-card-action-selection/20260714-102244.md`, `docs/negotiation/game-card-action-selection/20260714-102920.md`, `docs/negotiation/game-card-action-selection/20260714-103103.md`, `docs/negotiation/game-card-action-selection/20260714-103247.md`, `docs/negotiation/game-card-action-selection/20260714-103533.md`, `docs/negotiation/game-card-action-selection/20260714-103709.md`, `docs/negotiation/game-card-action-selection/20260714-104229.md`, `docs/negotiation/game-card-action-selection/20260714-104525.md`, `docs/negotiation/game-card-action-selection/20260714-104821.md`, `docs/negotiation/game-card-action-selection/20260714-110248.md`, `docs/negotiation/game-card-action-selection/20260714-124023.md`, `docs/negotiation/game-card-action-selection/20260714-125148.md`, `docs/negotiation/game-card-action-selection/20260714-130806.md`, `docs/negotiation/game-card-action-selection/20260714-131307.md`, `docs/negotiation/game-card-action-selection/20260714-131739.md`, `docs/negotiation/game-card-action-selection/20260714-132514.md`, `docs/negotiation/game-card-action-selection/20260714-134736.md`
- supersedes: `game-command-catalog`의 `USE_PRE_MOVE_CARD`/`USE_POST_MOVE_CARD`, `{cardInstanceId,selection}`, `CARD_USED`와 카드 pending을 표현하지 못한 기존 phase 조항
- architecture_source: `docs/architecture/interview-20260714/final-summary.md`, `docs/architecture/fixed-20260714/impl-fixed.md`, `docs/architecture/adr/adr-002-versioned-card-catalog-rdb-sync.md`

## 결정

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

## FE 구현 영향

- fixed schema 전에는 selection UI, reducer variant, MSW/fake STOMP/Playwright fixture와 임의 mock 구현을 시작하지 않는다.
- 권위 public transition, private augmentation, local selection draft와 pending overlay를 분리한다.
- 카드별 선택 interaction과 public/private outcome을 exhaustive generated type으로 처리한다.

## BE 구현 영향

- fixed catalog 전에는 자유형 handler, effect/outcome Map이나 임시 schema로 gameplay 구현을 시작하지 않는다.
- catalog와 handler/version registry, 공통 불변식 validator, public/private allowlist serializer와 fixture gate를 이후 구현 입력으로 사용한다.

## 계약 테스트/검증

- catalog 완결성: 12장 각각 handler, selection, outcome, fixture 연결과 version 일치
- selection: discriminator, 누락·추가 field, 다른 카드 variant 교차 사용, 대상 cardinality·순서·중복, 유효·무효 후보
- domain: phase·마나·조건, 킹/체스 불변식, 원자 rollback, idempotency, 종료 경쟁
- projection: public allowlist, viewer-private 후보·selection, 레전드와 숨은 정보 privacy-negative
- FE: 선택·취소·재선택·확정, 성공/실패, receipt/transition 순서, MSW/fake STOMP/Playwright
- drift gate: catalog, generated union, handler registry, schema와 fixture fingerprint 불일치 차단

## 미결정 또는 사용자 결정 이력

- 2026-07-13 FE/BE는 공통 기술 기준선에 합의했지만 `docs/cards`와 실제 MVP 12장 제품 정의가 없어 topic을 `needs_user_decision`으로 유지했다.
- 필요한 사용자 결정은 승인된 카드 catalog를 원자료로 제공할지, `$spec-interview`부터 새로 정의할지다.
- 2026-07-13 사용자는 현재 승인된 catalog가 없으며 추후 제공하기로 결정했다. 지금 새 카드 제품 정의를 만들지 않고 catalog 제공 전까지 topic과 전체 협상을 중단한다.
- 미확정 상태에서 자유형 fallback, FE 효과 추론, 협상자의 임의 카드·밸런스·fixture 생성은 허용하지 않는다.
- 2026-07-14 사용자는 `docs/cards/information.md`를 형식 구조로, 12개 JSON을 실제 카드 정보로 제공했다. fresh FE/BE 검토에서 기본 inventory는 완결됐지만 카드별 의미와 상위 산출물·architecture gate가 남아 `needs_user_decision`을 유지했다.
- 중재 추천은 구조 필드 우선, canonical board 좌표, blocked pawn을 제외한 eligible-only 적용, unordered distinct swap, `CARD_012` 서버 고정 순서와 성공 no-op, 비가역 command 전 명시적 확인이다. 사용자 승인 전 fixed하지 않는다.
- 2026-07-14 사용자는 구조 필드 우선, canonical board 좌표, `CARD_004` eligible-only, `CARD_006` unordered distinct와 비가역 command 전 명시적 확인을 채택했다.
- `CARD_012`는 서버 자동 선택 대신 서버가 계산한 최단거리 후보 중 카드 사용자가 1개를 선택하도록 결정했다. 이에 따라 기존 `target: NONE`과 `FIXED_BOARD_ORDER`는 상위 요구사항 승인 후 target selection 구조로 변경해야 한다.
- 2026-07-14 사용자는 `CARD_012` 최단거리 후보에서 상대 킹을 제외하고, 킹을 제외한 상대 기물이 없으면 카드·마나·행동을 소비하지 않는 사용 조건 실패로 처리하기로 결정했다.
- 2026-07-14 사용자는 `CARD_006`의 교환된 룩 캐슬링 권리 제거, 폰 교환의 새 앙파상 생성 금지·관련 기존 권리 제거, 카드 효과 프로모션 금지와 보드 이력 반영을 채택했다.
- 2026-07-14 사용자는 카드 효과 자체의 halfmove clock 비증가, 폰 이동·향후 캡처의 0 초기화, 그 외 카드 효과의 clock 유지와 표준 말 이동의 일반 규칙 적용을 채택했다.
- 2026-07-14 사용자는 `CARD_012` 전환 기물의 새 진영 기준 이동, 기존 이력 유지, 캐슬링·앙파상 권리 제거, 즉시 프로모션 금지와 최종 보드 재판정을 채택했다.
- 2026-07-14 사용자는 `CARD_001~003` 방향을 카드 사용자 진영 기준으로 변경하고 FE가 항상 자신의 기물을 화면 아래쪽에 표시하도록 협의할 것을 결정했다. canonical FE tracked 문서에는 기존 orientation 규칙이 없었다.
- 2026-07-14 fresh FE는 사용자 결정을 최초 orientation 기준으로 수용했고, fresh BE도 canonical state와 presentation orientation 분리 및 actor-relative mapping을 수용했다. 추가 사용자 결정은 없다.
- 2026-07-14 사용자는 spec-interview 반영 예정 전체 요약을 승인했고 `docs/spec/spec-fixed.md`, `docs/cards/information.md`와 관련 카드 JSON에 결정 사항을 반영했다.
- 2026-07-14 사용자는 spec-review 섹션 8 추천안과 private receipt가 canonical state를 직접 변경하지 않는 이유·순서 역전 위험을 문서화하도록 확정했다.
- 2026-07-14 사용자는 spec-review 섹션 14 추천안을 채택하되 CARD_004는 막힌 폰을 제외하고 전진 가능한 폰만 움직이는 부분 적용으로 명확히 했다. 적용 대상의 원자 결과가 공통 게임 불변식을 깨는 경우에만 전체 비소모 실패한다.
- 카드 version·master 저장·과거 replay 방식이 기존 아키텍처 변경을 동반하면 최신 PRD 이후 `$architecture-decision`에서 확정한다.
- 2026-07-14 사용자는 모든 카드의 발동과 효과 적용을 분리했다. 최초 발동 조건 실패만 비소모이며, 발동 성공 시 카드·마나·카드 행동 슬롯을 소비하고 카드는 패에서 제거·공개된다.
- 발동 후 효과 적용 실패는 비용을 환급하거나 재선택하지 않고 종료한다. 발동된 레전드도 공개되고 사용 완료로 처리한다. 이는 기존의 일반적인 카드 효과 실패 비소모 원칙을 대체한다.
- 2026-07-14 사용자는 선택형 카드의 `CARD_ACTIVATE → EFFECT_PENDING → CARD_RESOLVE` 두 권위 전이와 무대상 카드의 단일 명령 내 발동·효과 ordered event 구분을 확정했다.
- 발동 후 well-formed selection의 후보 밖 선택·전환 불가는 소비가 유지되는 `CARD_EFFECT_FAILED`로 종료한다. malformed resolve 요청은 pending을 유지하고, 효과 실패의 부분 보드 변경은 전부 폐기한다.
- 발동·효과 실패는 public generic 결과와 actor-private 상세로 분리하며, pending 재접속 복원과 개인 경기 시간 계속 진행을 적용한다.
- 2026-07-14 사용자는 card ID와 같은 version 정의의 불변성, 규칙·계약 의미 변경 시 version 증가, 경기 생성 시 ID/version/fingerprint pinning과 새 version의 신규 경기 적용을 확정했다.
- 과거 기보는 최신 handler 재실행이 아니라 저장된 권위 `GameEvent` outcome으로 재생하고, 발동 후 효과 실패와 소비·공개 상태도 보존한다.
- catalog fixture는 activation/effect/projection 경계를 포함하는 catalog hash 기반 지속 CI gate로 둔다. master runtime 원천과 저장·배포·historical definition 방식은 PRD 최신화 후 아키텍처 영향을 판정한다.
- 2026-07-14 사용자는 전체 spec-review 보완 요약을 승인했고 `docs/spec/spec-fixed.md`, `docs/cards/information.md`와 12개 JSON에 최신 발동·효과·version·replay 정책을 반영했다.
- 2026-07-14 사용자는 `spec-fixed.md`에 오류 코드·명령·이벤트·내부 상태·저장 구조 같은 구현 설명이 나타나지 않게 정리하고 앞서 확정한 내용을 PRD에 반영하도록 승인했다. 요구사항 명세를 제품 행동 중심으로 정리하고 허브·gameplay·card-collection-deck·match-history PRD와 추적성 문서를 최신화했다.
- 2026-07-14 `$architecture-decision`에서 `docs/cards` 작성·배포 원천, RDB의 모든 배포 불변 버전·활성 버전 실행 원천, 배포 기반 활성 전환과 신규 경기 version pinning을 확정했다. 활성화·롤백 가능한 모든 버전은 효과 처리·계약·fixture를 유지하며 과거 기보는 저장된 권위 결과를 사용한다. ARCH-ADR-002와 `fixed-20260714`가 accepted/fixed 상태다.
- 2026-07-14 fresh FE/BE 2차 검토는 단일 `CARD_ACTIVATE` wire literal, `CARD_RESOLVE`, pending·projection·ownColor·version handoff에 이견 없이 수용했다. 실제 wire schema/fixture와 REST replay는 후속 topic으로 넘기고 이 의미 계약을 `fixed`로 확정했다.

## 참조 메모 반영 대상

- 전체 negotiation session이 completed되기 전에는 BE/FE 계약 동기화와 참조 메모를 만들지 않는다.
- 의미 계약은 fixed됐지만 `contract-fixture`, active card/deck REST와 match-history replay REST가 완료되기 전에는 구현 gate를 열지 않는다.

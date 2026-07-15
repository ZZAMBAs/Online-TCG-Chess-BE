# Game State Sync Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/game-state-sync/20260713-150009.md`, `docs/negotiation/game-state-sync/20260713-150101.md`, `docs/negotiation/game-state-sync/20260713-150656.md`, `docs/negotiation/game-state-sync/20260713-150831.md`, `docs/negotiation/game-state-sync/20260713-150957.md`
- supersedes: 없음

## 결정

### destination과 권한

- native STOMP endpoint는 fixed `auth-cookie-csrf` 계약의 `/ws`를 사용한다.
- 경기 명령은 `SEND /app/games/{gameId}/commands`, viewer snapshot 동기화 요청은 `SEND /app/games/{gameId}/sync`로 보낸다.
- 공개 확정 event는 `SUBSCRIBE /topic/games/{gameId}`, actor 결과·개인 오류·viewer 비공개 projection·snapshot은 `SUBSCRIBE /user/queue/games/{gameId}`로 받는다.
- `SUBSCRIBE`와 `SEND`마다 인증 session, 경기 참가, 계정 상태, 역할과 제재를 검증한다. 개인 routing은 인증 principal만 사용하고 client가 보낸 userId는 사용하지 않는다.
- destination path와 body의 `gameId`가 다르면 거부한다.

### command, event와 snapshot envelope

- sync request, full viewer snapshot, actor receipt, public/private transition과 application/fatal error의 required/null/forbidden field는 `docs/negotiation/contract-schema-closure/summarize.md`의 exact wire를 사용한다.
- viewer snapshot은 canonical FEN, turn/phase, 양쪽 public state·일반 손패, 자기 instance hand·미사용 legend, visible definitions, promotion/card pending, timer, terminal outcome과 actor-private opponent action capability를 포함하는 닫힌 projection이다.

- 모든 command, event, snapshot과 개인 결과는 고정 `schemaVersion`을 포함한다.
- command는 `actionId`, `gameId`, `intent`, `baseStateVersion`, `payload`를 사용한다.
- transition은 `eventId`, outer `messageType:"GAME_TRANSITION"`, `gameId`, `stateVersion`, `transitionId`, `serverTime`, `payload`를 사용한다. `eventType`은 inner event discriminator에만 사용하고 사유는 해당 inner payload variant에 둔다.
- viewer snapshot은 `lastViewerPrivateSequence`, public transition은 color별 `privateSequencesAfter`, viewer-private transition은 `viewerPrivateSequence`를 가진다. private cursor gap이나 public이 예고한 +1 envelope 유실은 부분 추정 없이 sync snapshot으로 복구한다.
- actor 개인 성공 receipt는 `actionId`, `gameId`, `stateVersion`, `transitionId`를 포함한다. 실패는 transport별 닫힌 application error variant로 보내 pending의 확정 여부를 관찰하게 하며 공개 event에 `actionId`를 노출하지 않는다.
- snapshot은 `requestId`, `gameId`, `stateVersion`, `projectionScope`, `payload`를 포함하는 viewer 기준 전체 권위 projection이며 개인 queue로 전달한다.
- `intent`, outer `messageType`, inner `eventType`, `projectionScope`와 각 payload는 판별 가능한 JSON Schema 공용체로 고정한다. 구체 게임 행동과 event 목록은 이 계약을 투영하는 STOMP schema에서 상위 요구사항의 행동·event만 사용한다.

### 멱등성, 직렬화와 version

- 의미상 동일 command는 schema 검증 뒤 `gameId`, `intent`, `baseStateVersion`, payload의 canonical value를 비교해 판정한다. JSON object key 순서 같은 표현 차이는 의미 차이로 보지 않는다.
- 같은 `actionId`와 같은 command는 최초 성공 또는 실패의 개인 결과와 당시 `stateVersion`을 재전달한다. 상태를 다시 변경하거나 공개·개인 event를 재방송하지 않는다.
- 같은 `actionId`에 다른 command가 오면 `COMMAND_CONFLICT`로 거부한다. 동기화 뒤 command 내용을 바꿔 다시 제출할 때는 새 `actionId`를 사용한다.
- idempotency 결과는 underlying game, event와 command 결과의 보존 lifecycle보다 먼저 만료하지 않는다. 별도 숫자 TTL은 이 계약에서 만들지 않는다.
- 변경 command의 `baseStateVersion`은 현재 version과 정확히 같아야 한다. 다르면 상태를 변경하지 않고 `STATE_VERSION_MISMATCH`, 현재 `stateVersion`, `resyncRequired: true`를 개인 결과로 보낸다.
- 플레이어 command, timer deadline, 모든 연결 종료 deadline, reconnect, 항복과 경기 종료 판정은 같은 경기별 lock 또는 command queue에서 직렬화한다.
- 성공한 도메인 변경과 `GameEvent` 저장이 함께 확정된 뒤에만 `stateVersion`을 단조 증가시키고 event를 발행한다. 실패와 replay는 version을 증가시키지 않는다.

### FE 적용과 재동기화

- FE feature store/reducer는 권위 projection, `stateVersion`, `pendingByActionId`, 연결·동기화 상태와 optimistic overlay를 소유한다.
- 같은 도메인 전이의 공개·개인 projection은 같은 `transitionId`와 `stateVersion`을 공유한다. FE는 `eventId`를 중복 제거하고 `(gameId, stateVersion, transitionId)`로 공개 전이를 한 번 적용한 뒤 개인 필드만 보강한다.
- FE는 command 전송 뒤 `actionId`별 optimistic overlay만 pending으로 표시한다. 성공 개인 결과로 overlay를 확정하고 실패하면 overlay만 제거한다. 과거 전체 state로 rollback하지 않는다.
- 전송 결과가 불명확한 reconnect에서는 같은 command와 같은 `actionId`를 다시 보내 최초 결과를 조회한다.
- 최초 snapshot 전, gap, schema 검증 실패와 reconnect 중에는 신규 command와 delta 적용을 멈춘다. viewer snapshot을 Ajv로 검증한 뒤 store와 version cursor를 원자 교체한다.
- snapshot보다 오래된 buffered event는 폐기하고, snapshot 다음 version부터 연속적이고 schema-valid인 event만 순서대로 적용한다. 다시 gap이 생기면 재동기화한다.
- fatal contract/schema drift는 일반 사용자 또는 일시적 transport 오류와 구분하고 reducer 진입과 자동 reconnect loop를 중단한다. 최종 오류 taxonomy는 공통 오류 topic과 대조한다.

### connection, deadline과 projection

- 서버는 사용자·경기별 참가가 승인된 활성 STOMP connection 집합을 관리한다. 다른 탭이나 기기 connection이 하나라도 남으면 disconnect로 보지 않는다.
- 집합이 처음 0이 된 것을 서버가 감지한 시점부터 명세의 20초 disconnect deadline을 시작하고, 그 전에 승인 connection이 복귀하면 취소한다. heartbeat의 새 숫자 정책은 이 계약에서 만들지 않는다.
- 현재 browser session 로그아웃은 해당 session connection만 제거한다. 다른 session connection이 남으면 몰수패 countdown을 시작하지 않는다.
- 연결 중단 중에도 본인 turn이면 server clock이 계속 감소한다. 시간패와 몰수패는 실제 deadline이 빠른 것을 적용하고 동일 시각이면 시간패를 우선하며 경기 종료와 종료 event는 한 번만 확정한다.
- 공개 projection에는 보드, turn·phase, 공개 일반 카드 정보, 마나, 남은 덱 장수, server timer, 공개 카드 효과와 경기 결과만 포함한다.
- 개인 projection에만 자신의 미사용 레전드 카드와 개인 오류를 포함한다. 상대 미사용 레전드, 덱 구성·순서, RNG 내부값, 비공개 MMR은 snapshot, event와 오류 어디에도 노출하지 않는다.
- 상대 disconnect 상태, 남은 몰수패 countdown, 자동 재시도 문구와 화면 표현은 현재 계약 범위에 포함하지 않는다.

## FE 구현 영향

- session-scope STOMP manager는 자기 connection, reconnect와 resync만 관리하며 다른 탭·기기 connection 상태를 추정하지 않는다.
- feature store/reducer 앞에서 Ajv schema 검증을 수행하고 `ready`, `reconnecting`, `resyncing`, `permission_denied`, `fatal_schema_error` 상태를 구분한다.
- 공개·개인 projection merge, optimistic overlay, snapshot 원자 교체와 duplicate/gap 처리를 fixture 기반으로 구현한다.

## BE 구현 영향

- inbound STOMP adapter가 destination, session principal, 참가·계정·제재, schema, path/body 일치를 검증한다.
- gameplay application은 경기별 단일 직렬화, 멱등 결과 보존, event 저장과 version 증가의 원자성, projection 생성을 보장한다.
- connection index와 deadline 처리는 사용자·경기별 승인 connection 집합을 기준으로 한다.
- public/private serializer를 분리하고 공통 domain object를 검증 없이 공개 destination에 직렬화하지 않는다.

## 계약 테스트/검증

- JSON Schema: command, actor success/failure, public/private event, viewer snapshot과 공통 오류 envelope
- 멱등성: 같은 `actionId`의 동일·상이 command, 최초 성공·실패 replay, 무재방송, lifecycle 보존
- concurrency: stale `baseStateVersion`, 동시 command, event 저장 실패, timer/disconnect/항복/종료 경쟁
- connection: 두 탭 중 하나 종료, 모든 연결 종료, 20초 이내 복귀, 경계 시각, 다른 session 유지와 session 무효화
- FE fake STOMP/Ajv: duplicate, 같은 version의 projection merge, gap, 역순, reconnect, schema drift, pending replay와 snapshot 원자 교체
- privacy-negative fixture: 공개 destination 또는 viewer snapshot에 상대 레전드, 덱 구성·순서, RNG, MMR, 개인 오류가 섞이면 실패
- Playwright: reconnect/resync 동안 command 차단, 권위 화면 유지, snapshot 교체 뒤 정상 재개
- drift gate: 양쪽이 같은 fixed schema와 positive/negative fixture fingerprint를 사용하고 불일치를 CI에서 차단

## 미결정 또는 사용자 결정 이력

- 사용자 판단이 필요 없는 기술 계약이다. FE 조건부 수용 사항을 BE가 모두 받아들여 이견 없이 확정했다.
- 멱등성 숫자 TTL, heartbeat 숫자, 상대 disconnect/countdown UX는 상위 근거 없이 새로 만들지 않았다.
- schema-fatal 공통 오류 명칭은 후속 공통 오류 topic에서 정하되 이 topic의 상태 동기화 의미는 변경하지 않는다.

## 참조 메모 반영 대상

- BE: 전체 협상 session이 `completed`가 된 뒤 `$sync-be-contracts`가 `docs/contracts/game-state-sync.md`에 구현 참조 계약을 투영한다.
- FE: 전체 협상 session이 `completed`가 된 뒤 FE 계약 동기화가 canonical BE repo의 fixed 요약을 구현 참조 문서로 투영한다.
- 현재는 양쪽 repo에 별도 참조 메모를 만들지 않는다.

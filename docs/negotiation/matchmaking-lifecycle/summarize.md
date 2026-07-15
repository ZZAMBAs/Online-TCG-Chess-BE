# Matchmaking Lifecycle Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/matchmaking-lifecycle/20260713-151523.md`, `docs/negotiation/matchmaking-lifecycle/20260713-151614.md`, `docs/negotiation/matchmaking-lifecycle/20260713-152100.md`, `docs/negotiation/matchmaking-lifecycle/20260713-152147.md`, `docs/negotiation/matchmaking-lifecycle/20260713-152624.md`, `docs/negotiation/matchmaking-lifecycle/20260713-152753.md`, `docs/negotiation/matchmaking-lifecycle/20260714-154113.md`
- supersedes: quick matchmaking request의 `{deckId}` 단독 payload

## 결정

### REST와 멱등성

- `POST /api/v1/matchmaking/quick`은 body의 `{deckId,deckRevision}`으로 새 quick attempt를 요청하고 session, CSRF와 `Idempotency-Key`를 검증한다. client는 deck entries, card version과 fingerprint를 제출하지 않는다.
- idempotency key는 인증 사용자, quick matchmaking 행위와 정규화된 request scope에 결합한다.
- 최초 `WAITING` 생성은 `201`, 이미 같은 사용자의 active `WAITING`이 있으면 새 entry 없이 `200`과 현재 상태를 반환한다.
- `GET /api/v1/matchmaking/quick`은 current 또는 latest attempt의 권위 상태를 반환한다. attempt 이력이 전혀 없으면 `404`이며 FE adapter는 이를 정상 `noAttempt` empty state로 변환한다.
- terminal attempt는 다음 POST가 새 attempt를 성공적으로 생성하기 전까지 latest attempt로 조회된다. 숫자 TTL은 새로 만들지 않고 영구 보존은 상위 데이터 보존 정책을 따른다.
- `DELETE /api/v1/matchmaking/quick`은 session, CSRF와 `Idempotency-Key`를 검증한다. `WAITING → CANCELED`와 이미 `CANCELED`인 attempt의 의미상 중복 취소는 `200 CANCELED`다.
- `MATCH_CONFIRMED` 또는 `GAME_CREATED` 뒤 취소는 `409 MATCH_ALREADY_CONFIRMED`와 현재 권위 상태를 반환한다.
- 같은 idempotency key와 같은 request는 최초 HTTP 결과를 재현한다. 같은 key와 다른 request는 `409 COMMAND_CONFLICT`다. replay 결과는 현재 상태보다 stale할 수 있으므로 FE는 version 비교 없이 cache를 덮지 않는다.

### REST 상태와 개인 event

- 모든 REST 상태 표현은 `queueEntryId`, `state`, `stateVersion`, `serverTime`을 포함한다. `GAME_CREATED`는 `gameId`, `ownColor`, `FAILED`는 안전한 `failureCode`를 추가한다.
- `FAILED.failureCode`는 `DECK_CHANGED | DECK_INVALID | ACCOUNT_NOT_ELIGIBLE | MATCH_CREATION_FAILED`로 닫는다. 상대 조건, block 관계, MMR/range와 상대 deck 정보는 failure에 포함하지 않는다.
- 개인 event destination은 `SUBSCRIBE /user/queue/matchmaking`이며 공개 topic은 두지 않는다.
- event는 `schemaVersion`, `eventId`, `messageType:"MATCHMAKING_STATE_CHANGED"`, `queueEntryId`, `state`, `stateVersion`, `serverTime`, `payload`를 포함한다. outer에 `eventType`을 사용하지 않는다.
- 같은 `(queueEntryId, stateVersion)`의 REST와 event는 완전히 같은 공개 projection을 뜻한다.
- FE는 `eventId`를 중복 제거한다. 같은 entry의 낮은 version은 폐기하고 같은 version·같은 상태는 중복으로 무시하며, 같은 version·다른 상태 또는 gap은 병합하지 않고 GET한다.
- 다른 `queueEntryId` event는 현재 cache를 직접 교체하지 않고 GET으로 latest attempt를 확인한다. TanStack Query의 REST 결과가 baseline이고 STOMP는 검증된 realtime overlay다.

### 취소·확정 경쟁과 game handoff

- 취소, 최종 조건 검증과 match 확정은 같은 server 직렬화 경계에서 처리한다. 먼저 확정된 `CANCELED`는 game을 만들지 않고, 먼저 확정된 match는 이후 cancel보다 우선한다.
- match 확정 직전에 양쪽 account·restriction·deck·block 조건을 다시 검증한다. block 후보 제외는 이유를 노출하지 않고 재탐색하며, 본인 조건 실패만 안전한 `FAILED` code로 전달한다.
- 색 배정, 양쪽 deck snapshot, 초기 game 생성, 양쪽 attempt의 `MATCH_CONFIRMED → GAME_CREATED`는 한 원자적 commit으로 확정하고 중복 game을 만들지 않는다.
- event는 commit 결과와 연계해 전달하며 유실 시 GET으로 같은 권위 상태를 복구할 수 있어야 한다. 구체 outbox 구현을 강제하지 않는다.
- `GAME_CREATED` REST/event payload는 `gameId`와 `ownColor`만 handoff한다. match payload에 game snapshot, MMR, range, block 관계, deck 내용이나 상대 상세를 넣지 않는다.
- FE는 current entry의 schema-valid `GAME_CREATED`를 event 또는 GET에서 확인한 뒤 같은 `gameId`로 한 번만 route 전환한다. matchmaking 구독을 종료하고 game-state-sync의 game 구독과 viewer snapshot sync를 시작한다.

### active game과 새 attempt

- 진행 중 game이 있는 사용자의 새 quick matchmaking POST는 `409 GAME_IN_PROGRESS`로 거부한다.
- 오류의 안전한 현재 상태에는 요청자 자신의 active `gameId`를 포함해 기존 game route 복구에 사용할 수 있게 하며 상대 정보는 포함하지 않는다.
- game이 terminal 상태가 된 뒤에는 이전 matchmaking attempt를 보존한 채 새 attempt 생성을 허용한다.
- 성공한 새 POST 응답의 `queueEntryId`가 current/latest attempt를 교체한다. 이전 attempt의 지연 event는 직접 병합하지 않고 GET으로 확인한다.
- active game 확인과 신규 entry 생성은 사용자 단위 직렬화 또는 동등한 원자적 제약을 사용한다. 새 POST가 commit까지 성공한 경우에만 latest terminal attempt를 교체하고 실패나 rollback이면 기존 attempt를 유지한다.
- queue 진입 시 single saved deck의 ID/revision 일치와 current validity를 검증하고 game 생성 직전에 다시 검증한다. 대기 중 revision 변경은 terminal `FAILED`의 `DECK_CHANGED`, current invalid는 `DECK_INVALID`다.
- game 생성 transaction에서 그 시점의 current active card version을 deck snapshot에 pin한다. deck 저장과 queue 진입은 card version을 pin하지 않는다.

## FE 구현 영향

- TanStack Query가 REST baseline을 소유하고 feature STOMP reducer가 duplicate, monotonic version, gap과 unknown entry를 처리한다.
- join/cancel pending 동안 UI 중복 입력을 막되 server idempotency를 최종 안전장치로 사용한다.
- 예상 matchmaking 오류와 noAttempt는 route error boundary가 아닌 feature loading/empty/error 상태로 표현한다.
- `GAME_CREATED` route handoff는 `gameId` dedup 뒤 game-state-sync로 전환한다.

## BE 구현 영향

- REST adapter가 session, CSRF, Idempotency-Key와 상태별 HTTP/error projection을 제공한다.
- matchmaking application이 사용자별 active entry, 취소·확정 경쟁, 최종 재검증과 game 생성의 원자성을 보장한다.
- active game 오류는 요청자 자신의 `gameId`만 포함하는 전용 최소 DTO를 사용하며 내부 game projection을 재사용하지 않는다.
- private event delivery는 commit과 연계되고 GET 복구 상태와 같은 version/projection을 제공한다.
- MMR, range, block 관계와 deck snapshot은 REST/event serializer에서 제외한다.

## 계약 테스트/검증

- OpenAPI: POST/GET/DELETE, 상태별 success/error union, Idempotency-Key와 공통 상태 projection
- STOMP JSON Schema: 상태별 discriminated event와 privacy-negative fixture
- idempotency: 같은 key replay, 다른 payload conflict, 다른 key 중복 join, 새 key 중복 cancel, stale replay cache 비역행
- concurrency: cancel 대 confirmation, final validation failure, 색·deck snapshot·game·양쪽 attempt 원자성, 중복 game 방지
- active game 종료와 새 POST 경쟁, 실패·rollback 때 latest terminal attempt 유지
- deck revision mismatch, queue 뒤 `DECK_CHANGED`, current `DECK_INVALID`, game 생성 시 active card version pinning
- FE MSW/fake STOMP: duplicate, 역행, 같은 version 불일치, gap, unknown entry, reconnect/reload GET 복구, `GAME_CREATED` 단일 이동
- privacy: MMR, range, block 관계, deck 내용, 상대 상세가 REST와 event에 포함되면 실패
- drift gate: 양쪽 OpenAPI/schema/fixture fingerprint 불일치를 CI에서 차단

## 미결정 또는 사용자 결정 이력

- 기술 계약은 FE/BE 조건부 합의가 이루어졌다.
- 사용자 결정 반영: 2026-07-13 사용자가 중재자 추천안인 active game 중 새 quick matchmaking 거부를 승인했다.
- 진행 중 game이 있으면 `409 GAME_IN_PROGRESS`로 거부하고, game이 terminal 상태가 된 뒤 새 attempt를 허용한다.
- FE/BE 2차 검토에서 사용자 결정과 기술 보강안이 트랜잭션·멱등성·projection과 충돌하지 않음을 확인해 fixed로 확정했다.
- 2026-07-14 fixed card-collection-deck-rest의 fresh FE/BE 검토가 request를 `{deckId,deckRevision}`으로 대체하고 deck change/invalid와 game-creation-time version pinning을 추가했다. 나머지 matchmaking lifecycle 의미는 변경하지 않았다.

## 참조 메모 반영 대상

- 전체 협상 session이 `completed`가 되기 전에는 BE/FE 동기화나 별도 참조 메모를 만들지 않는다.

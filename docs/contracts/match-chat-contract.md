# Match Chat Contract BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### transport와 공통 경계

- chat은 gameplay transition, `stateVersion`, pending과 reducer에서 완전히 분리한다.
- live send·receipt·delivery는 STOMP 개인 queue, current-game initial/reconnect 복구는 REST history를 사용한다.
- send는 `SEND /app/games/{gameId}/chat/messages`, receive는 `SUBSCRIBE /user/queue/games/{gameId}/chat`이다.
- 공개 game topic에는 chat message, receipt, application error와 block 결과를 발행하지 않는다.
- 신고 REST와 관리자 원문 조회는 후속 trust/safety 계약이 소유한다.
- 모든 schema는 `schemaVersion: "1"`과 최종 객체 `additionalProperties: false`를 사용한다.

### ChatMessageView

- REST history와 STOMP sender/recipient event는 동일한 닫힌 `ChatMessageView`를 사용한다.
- 필드는 `chatMessageId`, 경기별 양의 정수 `sequence`, `senderColor: WHITE|BLACK`, `maskedText`, UTC millisecond `sentAt`이다.
- raw text, sender userId, recipient, block/delivery eligibility, recipient count, 금칙어 사전·matched 위치·algorithm 정보는 포함하지 않는다.
- `maskedText`는 전송 당시 저장한 불변 사용자 projection이다. history에서 current 금칙어 사전으로 다시 계산하지 않는다.
- FE와 관리자 UI는 plain text node로 렌더링하고 HTML로 해석하지 않는다. server도 HTML entity로 이중 encoding하지 않는다.

### current-game REST history

- `GET /api/v1/games/{gameId}/chat/messages?cursor={opaque}`를 사용한다.
- 인증된 현재 진행 중 경기 참가자만 조회하며 응답은 `Cache-Control: no-store`다.
- cursor를 생략하면 recipient delivery eligibility를 먼저 적용한 뒤 viewer-visible 최신 50개를 선택하고 화면 적용 순서인 `sequence ASC`로 반환한다.
- 응답은 `{schemaVersion:"1",items:ChatMessageView[],nextCursor}`이며 nullable `nextCursor`는 더 과거 viewer-visible message 50개를 가리킨다.
- cursor는 viewer principal, game과 정렬 조건에 결합한다. 변조·타 사용자 재사용은 `400 VALIDATION_FAILED`로 처리한다.
- `matchChatVisible`을 다시 켜면 꺼 둔 동안 delivery eligible이었던 current-game message도 같은 history로 복원한다.
- history read와 `GAME_ENDED`는 gameplay의 같은 경기 직렬화 경계에서 선형화한다. 종료보다 먼저 승인된 read만 완료할 수 있다.
- 종료 경기 participant request는 message 존재·개수·last sequence를 포함하지 않는 `CHAT_CLOSED` 닫힌 오류로 거부한다.
- unknown game과 nonparticipant는 동일한 `404 RESOURCE_NOT_FOUND` shape로 존재와 참가 관계를 숨긴다.
- 경기 종료 후 사용자 history를 제공하지 않는다. FE가 이미 받은 message는 현재 route를 떠날 때까지 유지할 수 있으나 신규 history retry는 하지 않는다.
- 일반 기록의 7일 저장은 사용자 history 권한을 만들지 않는다.

### send command와 validation

- command는 `{schemaVersion:"1",actionId,gameId,text}`의 닫힌 객체다. body `gameId`는 path와 같아야 한다.
- senderId, nickname, color, role, recipient, account/restriction/block 상태는 client에서 받지 않고 server session과 공개 application port로 결정한다.
- `text`는 Unicode code point 최대 100자이며 빈 문자열과 Unicode 공백-only를 거부한다.
- 증거 원문을 바꾸지 않도록 server는 임의 trim과 Unicode normalization을 하지 않는다.
- 금칙어는 대소문자 비구분 단순 부분 문자열, 중첩 시 긴 단어 우선, 모든 출현 위치를 전체 길이 `*`로 마스킹한다.
- 금칙어 사전 변경은 변경 이후 승인 message부터 적용하고 기존 raw/`maskedText`를 재처리하지 않는다.

### STOMP success와 live delivery

- sender에게 `CHAT_SEND_ACCEPTED`를 보내며 `actionId`, `gameId`, 권위 `message: ChatMessageView`를 포함한다.
- delivery eligible 상대에게 `CHAT_MESSAGE_RECEIVED`를 보내며 `gameId`, `message: ChatMessageView`를 포함한다.
- sender receipt shape는 상대 delivery 여부, block과 visibility 설정에 관계없이 동일하다.
- 상대 delivery count와 block 여부를 receipt에 포함하지 않는다.
- chat application error는 chat 개인 queue에만 보내고 gameplay reducer·pending·stateVersion을 변경하지 않는다.

### 순서와 idempotency

- chat `sequence`는 경기별 승인·저장 message 순서이며 gameplay `stateVersion`과 무관하다. 거부 message는 sequence를 소비하지 않는다.
- block eligibility로 viewer history에 sequence gap이 생길 수 있으며 이는 transport loss, schema drift나 resync 조건이 아니다.
- idempotency 범위는 `principal + gameId + actionId`다.
- 같은 ID와 의미상 같은 command는 최초 terminal result만 replay하고 message 저장, 상대 live delivery와 rate-limit 계산을 반복하지 않는다.
- 같은 ID에 다른 game/text를 사용하면 `COMMAND_CONFLICT`다.
- parse 전 malformed frame에는 검증되지 않은 `actionId`를 반사하지 않는다.
- idempotent result lookup은 current active-game 검사보다 먼저 수행한다. 경기 종료·제재·block 변경 뒤에도 종료 전에 성공한 동일 action replay는 최초 sender receipt를 반환하되 상대 frame을 다시 발행하지 않는다.
- idempotency 결과는 연결된 일반 message와 같은 7일 lifecycle 동안 유지한다.

### transaction과 publish

- 승인 message, raw text, 저장 당시 `maskedText`, sequence, recipient eligibility와 idempotent terminal result를 하나의 RDB transaction으로 commit한다.
- commit 성공 뒤에만 sender receipt와 허용 recipient live frame을 경기별 발행 순서로 publish한다. `commit-before-publish`를 따른다.
- commit 뒤 crash나 publish 실패로 live frame이 유실되면 진행 중 경기에서는 REST history와 동일 action replay로 복구한다. 동일 message를 새로 만들거나 상대에게 재방송하지 않는다.
- send와 `GAME_ENDED`는 gameplay 공개 port의 같은 경기 직렬화 경계에서 선형화한다. 종료 뒤 새 send는 `GAME_NOT_ACTIVE`다.
- durable queue/outbox는 MVP에 도입하지 않는다. 종료 뒤 history가 없는 복구 제한은 승인된 제품 정책이다.

### block·restriction·visibility

- block은 방향성이다. A가 B를 block하면 B에서 A로의 delivery만 차단하고 B에게 이를 알리지 않는다.
- message 승인과 recipient eligibility 결정은 block/unblock transaction과 하나의 논리 순서로 선형화한다.
- block commit 이후 승인되는 상대 message는 해당 viewer에게 ineligible이다. block 전에 승인되어 eligible로 확정된 message는 physical publish가 늦어도 기존 eligible message다.
- block 전에 delivery eligible이었던 message는 history에 유지한다. block 중 ineligible로 확정된 message는 unblock 뒤에도 history/live replay로 소급 노출하지 않는다.
- `matchChatVisible=false`는 FE UI와 subscription/history 수행 선호일 뿐 eligibility, send 권한, 저장, 신고와 block filtering을 변경하지 않는다.
- communication suspension은 SEND만 `COMMUNICATION_SUSPENDED`로 거부하고 개인 subscription과 current-game history 수신은 허용한다.
- account suspension은 fixed session/STOMP 무효화와 주요 기능 차단을 적용한다.

### rate limit과 오류

- 사용자+경기 기준 1초 최대 3건과 10초 최대 10건을 동시에 적용한다.
- idempotent replay는 새 rate-limit request로 계산하지 않는다.
- 공백-only·100 code point 초과는 `VALIDATION_FAILED`와 `/text` field error다.
- limit 초과는 `RATE_LIMITED`와 earliest permitted time까지 올림한 양의 `retryAfterSeconds`다.
- send 종료 경기는 `GAME_NOT_ACTIVE`, history 종료 경기는 `CHAT_CLOSED`, communication/account suspension은 기존 code, idempotency conflict는 `COMMAND_CONFLICT`를 사용한다.
- 정상 연결 뒤 validation/domain/rate-limit error는 chat 전용 `StompApplicationError` variant로 개인 queue에 보내며 gameplay 전용 stateVersion/transitionId를 요구하지 않는다.
- 인증·CSRF·protocol·허용되지 않은 destination과 안전한 command context 생성 전 실패는 fixed `StompFatalError`, `ERROR` 후 close 규칙을 따른다.
- 거부 message는 정상 chat row와 sequence를 만들지 않고 보안·rate-limit log에 raw/masked text를 남기지 않는다.

### FE history/live merge

1. chat 개인 queue를 subscribe하고 live frame buffer를 시작한다.
2. 최신 REST history를 조회한다.
3. history와 buffer를 `chatMessageId`로 중복 제거한다.
4. `sequence ASC`로 정렬해 화면 state를 원자 적용한다.
5. 이후 live frame도 ID dedup과 sequence ordering으로 적용한다.

- reconnect와 visibility 재활성화 때 gap 유무와 관계없이 항상 latest history를 조회한다.
- 더 과거 page를 prepend할 때도 ID dedup과 ordering을 유지한다.
- optimistic bubble을 사용하면 `actionId`로만 pending을 관리하고 receipt의 authoritative `ChatMessageView`로 교체한다. text/time 추정 reconciliation은 금지한다.
- route 이탈, game 변경, logout과 session 무효화 때 chat query cache, buffer와 pending을 제거한다.
- `maskedText`를 FE observability, URL과 persistent storage에 기록하지 않는다.

### 모듈과 retention

- `matchchat`은 raw/masked message, sequence, recipient eligibility, idempotency와 일반 기록 cleanup을 소유한다.
- `gameplay` 공개 port로 participant/color/current-game과 종료 직렬화 경계를 확인한다.
- `identity` 공개 port로 account와 communication restriction을 확인한다.
- `trustsafety` 공개 port로 block 관계와 current forbidden-word dictionary를 확인한다.
- 신고 생성 시 `trustsafety` application service가 `matchchat` 공개 port로 message evidence snapshot을 받아 자체 transaction에 보관한다. 모듈 간 repository 직접 접근은 금지한다.
- 일반 raw/masked message, eligibility와 idempotency 부속 기록은 7일 뒤 함께 삭제하거나 원문을 제거한다. 신고 evidence copy의 별도 lifecycle에는 영향을 주지 않는다.
- raw text와 eligibility는 일반 REST/STOMP/error/game replay/운영 log에 포함하지 않는다.

## 오류 포맷과 사용자 표시 영향

- chat query/cache, buffer, reducer와 pending을 gameplay state에서 분리한다.
- generated OpenAPI/STOMP schema와 Ajv validation을 사용하며 sequence gap을 복구 오류로 해석하지 않는다.
- matchChatVisible off/on에서 unsubscribe/UI hide와 subscribe→history→merge를 수행한다.

## 구현 메모

- matchchat module이 JPA/Flyway 저장, command idempotency, recipient eligibility, masking과 cleanup을 소유한다.
- 공개 application port만으로 gameplay/identity/trustsafety와 협력하고 commit-before-publish와 경기별 발행 순서를 강제한다.
- 새 infrastructure와 architecture decision은 필요하지 않다.

## 테스트/fixture/드리프트 검증

- schema: REST history, command, `ChatMessageView`, accepted/received event와 chat error closed variant
- validation/masking: whitespace, 100 code point boundary, HTML plain text, multi/overlap forbidden words, dictionary change non-retroactivity
- limit/idempotency: 4th/11th request, same action replay no row/delivery/count, conflicting action, malformed ID no reflection
- ordering/recovery: live-before-history, history-before-live, receipt/message order inversion, duplicate, publish failure, reconnect and older prepend
- lifecycle/race: send/game-end linearization, active-check-before-replay 금지, terminated history reject, 7-day cleanup and evidence survival
- block/privacy: eligible history before block, ineligible during block, unblock non-retroactivity, normal sequence gap, identical sender receipt
- privacy-negative: raw/userId/recipient/block/eligibility/count/dictionary/admin info absent from payload/error/log/replay
- drift gate: OpenAPI, STOMP schema, generated client, MSW/Ajv fixture fingerprint mismatch를 차단한다.

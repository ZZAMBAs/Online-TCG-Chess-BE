# Common Error Contract BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### full registry closure

- 모든 fixed feature의 REST/STOMP status, errorCode와 required/forbidden conditional field는 `docs/negotiation/contract-schema-closure/summarize.md`의 Common error registry를 canonical registry로 사용한다.
- 기존 이 문서의 공통 envelope·privacy·retry 의미는 유지하되 누락된 feature code, `410 EVIDENCE_UNAVAILABLE`, `502 EMAIL_DELIVERY_FAILED`와 revision/consent condition variant는 closure가 대체한다.
- parsed game, malformed game, parsed chat, malformed chat과 fatal STOMP error는 closure의 `stomp-registry.md`에 서로 다른 final oneOf로 분리한다. chat error에는 gameplay state cursor를 금지하고 malformed error에는 client correlation을 반사하지 않는다.
- matchmaking `failureCode`와 committed card effect failure를 request errorCode로 혼합하지 않는다.

### 공통 의미와 schema

- 오류 schema의 초기 `schemaVersion` literal은 문자열 `"1"`이다. 호환되지 않는 envelope 변경에서만 증가시킨다.
- 모든 오류는 `schemaVersion`, `errorCode`, 안전한 fallback `message`, server-controlled `traceId`를 공통 의미로 가진다.
- `message`는 제품 문구, 번역 key 또는 FE 분기 원천이 아니다. FE는 `errorCode`로 상태와 다음 행동을 정한다.
- 예외명, stack trace, SQL, 내부 정책값, token, cookie, session ID, CSRF와 비공개 game 정보는 오류 DTO에 포함하지 않는다.
- 하나의 닫힌 core를 확장하지 않는다. `RestError`, `StompFatalError`, `StompApplicationError`가 각 최종 property를 직접 선언하고 객체 최종 수준에서 `additionalProperties: false`를 적용한다.
- `RestError`와 `StompApplicationError`는 code/context별 닫힌 `oneOf` variant로 조건부 field를 제한한다. feature별 context는 공통 객체에 임의 optional field를 추가하지 않고 새 닫힌 variant로 합의한다.

### validation과 field error

- `MALFORMED_REQUEST`는 JSON parse, 타입과 framing 실패에 사용하고 `fieldErrors`를 포함하지 않는다.
- `VALIDATION_FAILED`는 parse 뒤 DTO field validation 실패에 사용하며 `fieldErrors`를 필수로 가진다.
- `fieldErrors` 각 항목은 닫힌 `{field,errorCode,message}`다. `field`는 RFC 6901 JSON Pointer이며 예시는 `/profile/nickname`, `/items/0/name`이다.
- 같은 field의 복수 오류를 허용하지만 배열 순서에 의미를 두지 않는다. FE가 현재 form에 mapping할 수 없는 pointer는 inline field가 아닌 안전한 form/global 오류로 처리한다.

### REST status와 code

- `400`: `MALFORMED_REQUEST`, `VALIDATION_FAILED`
- `401`: `UNAUTHENTICATED`
- `403`: `CSRF_INVALID`, `FORBIDDEN`, `EMAIL_UNVERIFIED`, `ACCOUNT_SUSPENDED`, `COMMUNICATION_SUSPENDED` 등 인증 이후 권한·계정·기능 제한
- `404`: `RESOURCE_NOT_FOUND` 또는 endpoint가 존재 여부 은닉을 요구하는 동일한 안전 variant
- `409`: `COMMAND_CONFLICT`, `MATCH_ALREADY_CONFIRMED`, `GAME_IN_PROGRESS`, `STATE_VERSION_MISMATCH`와 현재 권위 상태 충돌
- `429`: `RATE_LIMITED`
- `410`: `EVIDENCE_UNAVAILABLE`
- `500`: `INTERNAL_ERROR`
- `502`: `EMAIL_DELIVERY_FAILED`
- 같은 ID와 같은 command는 최초 결과 replay이므로 일반 `DUPLICATE_COMMAND` 오류로 만들지 않는다. 같은 ID와 다른 command만 `COMMAND_CONFLICT`다.
- 존재 은닉 endpoint는 권한·존재 여부 모두 동일한 status, code와 안전 message shape를 사용하고 resource 상태·소유권을 포함하지 않는다. 존재 공개가 허용된 문맥에서만 `NOT_GAME_PARTICIPANT` 같은 구체 code를 사용한다.
- `GAME_IN_PROGRESS` variant에는 요청자 자신의 active `gameId`만 포함한다.

### STOMP 전달

- `StompFatalError`는 CONNECT, session, protocol 또는 destination 수준에서 command context를 안전하게 만들 수 없는 치명 실패에 사용한다. `ERROR` frame body로 전달하고 연결을 종료한다.
- Origin handshake `403`은 브라우저가 body 또는 공통 schema를 읽을 수 있다고 전제하지 않는다.
- `StompApplicationError`는 정상 연결 뒤 application/domain/rate-limit 거부를 인증 principal 개인 queue로 전달한다. 공개 topic에는 오류를 보내지 않는다.
- parsed game command variant는 `actionId`, `gameId`, 현재 `stateVersion`, 현재 권위 상태의 `transitionId`를 필수로 하고 code에 따라 `resyncRequired`, `retryAfterSeconds`, `fieldErrors`를 조건부 허용한다.
- payload를 안전하게 parse하지 못한 malformed application frame은 별도 variant를 사용한다. client가 보낸 미검증 `actionId`나 임의 값을 응답 상관키·trace/log 식별자로 반사하지 않는다.
- `STATE_VERSION_MISMATCH`는 상태를 변경하지 않고 개인 queue로 보내며 현재 `stateVersion`과 `resyncRequired: true`를 포함한다.
- `reasonCode`는 성공적으로 확정된 종료·상태 event의 도메인 사유다. `errorCode`는 거부된 request/command에만 사용한다.

### rate limit, retry와 fatal drift

- REST `RATE_LIMITED`는 `Retry-After`를 delta-seconds로 제공하고 body의 양의 정수 `retryAfterSeconds`와 같은 값을 사용한다. STOMP는 개인 오류 body 값만 사용한다.
- header/body 불일치는 transport contract violation이며 자동 retry 근거로 사용하지 않는다.
- `403`, `409`, `429`, `500`이라는 status만으로 mutation을 자동 재전송하지 않는다. fixed idempotency가 있더라도 결과 조회나 사용자 재시도를 우선하고 같은 의도 replay에는 같은 key/`actionId`를 사용한다.
- `STATE_VERSION_MISMATCH`는 snapshot resync를 먼저 수행하고 변경된 command에는 새 `actionId`를 사용한다.
- 미지원 `schemaVersion`, 필수 field 누락, 추가 field, type·variant 위반은 FE에서 fatal contract drift로 분류한다. reducer 적용, domain retry와 auto reconnect를 중단하고 안전한 observability에 기록한다.

### trace와 observability

- `traceId`는 server가 생성하거나 검증된 tracing context에서 파생한다. client 입력을 그대로 response 또는 log key로 사용하지 않는다.
- REST request부터 application/log까지, STOMP frame 처리부터 개인 오류/log까지 같은 trace 문맥을 연결한다.
- FE는 `traceId`를 문의 근거와 비민감 observability correlation으로만 사용하고 기능 분기나 사용자 식별에 사용하지 않는다.

## 오류 포맷과 사용자 표시 영향

- 공통 error normalization adapter가 REST, STOMP fatal과 STOMP application schema를 각각 검증해 typed error로 변환한다.
- feature는 field inline, malformed/global, auth boundary, permission/restriction, not-found, conflict/resync, rate-limit, internal fallback과 fatal contract drift를 code별로 mapping한다.
- expected error는 route error boundary로 보내지 않고 feature 상태로 처리하며 fatal drift는 reducer와 reconnect 전에 차단한다.

## 구현 메모

- exception handler와 STOMP adapter는 allowlist 오류 DTO만 serializer에 전달하고 임의 Map 또는 exception 객체를 노출하지 않는다.
- endpoint/application context별 닫힌 variant를 선택하고 status, code, condition field와 transport destination을 일치시킨다.
- rate limit, trace propagation과 privacy-safe logging은 REST/STOMP에서 같은 의미를 유지한다.

## 테스트/fixture/드리프트 검증

- OpenAPI/JSON Schema: `RestError`, `StompFatalError`, `StompApplicationError`와 code별 `oneOf` variant
- positive fixture: 모든 status/code, validation pointer, auth 세부 code, game state mismatch, rate limit, active game, fatal/application STOMP
- negative fixture: 추가 field, 미지원 version, 잘못된 JSON Pointer, forbidden condition field, wrong transport schema, public destination 오류, privacy field, exception/stack/SQL 노출
- MSW: `400/401/403/404/409/429/500`, field mapping, concealment, `Retry-After`와 body 일치·불일치
- fake STOMP/Ajv: fatal `ERROR` 후 close, 개인 application 오류, malformed frame, resync-first, no public error, fatal drift no reconnect
- Playwright: auth/account/restriction, form, not-found, conflict/resync, rate-limit 대기, internal fallback과 fatal drift 상태
- drift gate: 양쪽이 같은 fixed schema와 fixture fingerprint를 사용하고 불일치를 CI에서 차단

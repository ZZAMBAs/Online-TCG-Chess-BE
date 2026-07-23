# Auth Cookie Csrf BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### 배포와 session cookie

- FE는 same-origin 상대 경로를 사용하고 REST transport에 `credentials: "same-origin"`을 명시한다.
- session cookie는 `HttpOnly; Secure; SameSite=Lax; Path=/`를 사용한다.
- session ID는 JSON, JavaScript 접근 가능 cookie, URL, STOMP payload, client/server log와 observability에 노출하지 않는다.
- WebSocket handshake Origin은 환경별 정확한 `scheme://host[:port]` allowlist로 검증한다. wildcard, Origin 누락 허용, 요청 Origin 반사는 금지한다.
- 단일 public origin 외 별도 origin이나 cross-site 배포가 필요하면 이 계약을 확장하기 전에 FE/BE architecture decision을 재검토한다.

### CSRF와 session bootstrap

- `GET /api/v1/auth/csrf`는 비로그인 상태에서도 호출할 수 있다.
- 유효한 session cookie가 없으면 anonymous server session을 생성하고, 있으면 해당 session에 결합된 CSRF token을 사용한다.
- 성공 응답은 HTTP `200`, body `{ "schemaVersion":"1", "token": "..." }`, `Cache-Control: no-store`다.
- FE는 CSRF token을 transport 메모리에만 보관하고 storage, URL, DOM, TanStack Query cache, runtime config, log와 observability에 저장하지 않는다.
- 상태 변경 REST 요청과 STOMP `CONNECT` native header는 `X-CSRF-TOKEN`을 사용한다. query parameter 전달은 금지한다.
- `GET /api/v1/auth/session`은 bootstrap용 현재 상태 조회다. anonymous는 오류가 아니라 HTTP `200`, `{ "authenticated": false }`를 반환한다.
- 인증 상태 응답은 `authenticated`, `accountStatus`, `roles`, `activeRestrictions`의 최소 projection만 포함한다. 개인정보, session ID, CSRF token은 포함하지 않는다.
- 일반 보호 API에서 session이 없거나 만료되면 HTTP `401`, `UNAUTHENTICATED`를 반환한다.

### session 회전과 무효화

- 로그인, OAuth 완료, 비밀번호 재설정 완료 시 session ID를 회전한다.
- session ID 회전 또는 session 폐기 시 이전 CSRF token과 연결된 STOMP connection을 무효화한다.
- FE는 기존 CSRF와 STOMP를 폐기하고 `CSRF 재bootstrap → session 상태 재조회 → 허용 route 결정 → 필요한 STOMP 연결` 순서를 수행한다.
- OAuth 성공·실패·취소 귀환 뒤에도 client가 session을 추정하지 않고 같은 bootstrap 순서를 수행한다. provider callback path와 오류 mapping, 화면 문구는 별도 auth REST/OAuth 계약에서 정한다.
- 탈퇴, 계정정지, 비밀번호 재설정 완료는 해당 사용자의 기존 session과 STOMP를 모두 무효화한다.
- 일반 로그아웃은 요청을 인증한 현재 browser session과 그 session에 연결된 CSRF token·STOMP connection만 무효화한다.
- 다른 기기의 session과 STOMP connection은 일반 로그아웃으로 종료하지 않는다. 모든 기기 로그아웃은 향후 별도 보안 기능과 endpoint 계약으로 분리한다.

### WebSocket과 오류

- native WebSocket handshake path는 `/ws`다. SockJS는 사용하지 않는다.
- handshake의 Origin 실패는 HTTP `403`으로 거부하며 브라우저가 응답 body를 읽을 수 있다고 전제하지 않는다.
- handshake 뒤 STOMP `CONNECT`의 session·CSRF·계정 검증 실패는 공통 오류 JSON을 `ERROR` frame body에 담고 연결을 종료한다.
- REST와 STOMP 오류는 `common-error-contract`의 transport별 닫힌 schema를 사용하고 공통 필드 `schemaVersion`, `errorCode`, `message`, `traceId`와 code별 조건 field를 따른다.
- 기존 `UNAUTHENTICATED`, `EMAIL_UNVERIFIED`, `ACCOUNT_SUSPENDED`, `COMMUNICATION_SUSPENDED`, `FORBIDDEN`을 재사용하고 기술 코드 `CSRF_INVALID`, `ORIGIN_REJECTED`를 추가한다.
- `message`는 제품 문구 원천이 아닌 안전한 fallback이며 FE는 `errorCode`로 의미와 다음 행동을 정한다.
- STOMP `CONNECT`, `SUBSCRIBE`, `SEND`마다 현재 session, 역할, 계정 상태, 제재를 검증한다.
- 인증·CSRF·Origin·계정 상태·제재·권한 오류는 자동 reconnect하지 않는다. transport 종료·timeout 같은 일시적 network 실패만 제한된 backoff 대상이다.
- CSRF 실패 mutation은 자동 재전송하지 않는다.

## 오류 포맷과 사용자 표시 영향

- session provider가 CSRF와 session bootstrap, loading과 route guard 순서를 소유한다.
- 공통 fetch transport가 credential, CSRF header, 오류 mapping을 담당한다.
- session-scope STOMP manager는 연결 시점마다 현재 CSRF를 사용하고 인증 오류가 발생하면 reconnect loop를 종료한다.
- 예상 인증·계정 오류는 route error boundary로 보내지 않고 인증 필요, 인증 미완료, 계정 제한과 가능한 다음 행동으로 mapping한다.

## 구현 메모

- Spring Security session·CSRF와 inbound WebSocket/STOMP security adapter가 cookie, Origin, CSRF와 연결 lifecycle을 강제한다.
- session 회전·폐기와 STOMP connection index를 연계해 이전 인증 문맥을 종료한다.
- anonymous CSRF session 생성은 session 만료와 abuse 방어를 적용하되 계약에 없는 임계값을 새 제품 정책으로 만들지 않는다.
- REST와 STOMP adapter는 같은 오류 schema와 `errorCode` 체계를 사용하고 token, cookie, session ID를 기록하지 않는다.

## 테스트/fixture/드리프트 검증

- OpenAPI: CSRF bootstrap, session bootstrap, 공통 오류 schema와 `Cache-Control: no-store`
- Spring Security 통합 테스트: cookie 속성, anonymous/인증 CSRF, REST CSRF 성공·실패, session 회전·폐기, 보호 API `401`
- WebSocket/STOMP 통합 테스트: exact Origin allowlist, handshake `403`, `CONNECT` session·CSRF, `ERROR` JSON 후 close, `SUBSCRIBE`·`SEND` 재검증, session 폐기 후 socket 종료
- FE MSW: bootstrap 순서, credential/header, `401`/`403`, CSRF mutation 비자동재전송
- FE fake STOMP/Ajv: 최초 연결, 재bootstrap reconnect, session/token mismatch, 오류 후 close, 인증 실패 reconnect 중지
- Playwright: bootstrap loading, 로그인·OAuth 귀환, session 만료, 상태별 route/다음 행동, 현재 browser logout 후 해당 REST 거부·socket 종료와 다른 session 유지, cookie의 JavaScript 비노출
- contract drift: OpenAPI와 STOMP 오류 schema·fixture fingerprint, generated client, MSW와 Ajv fixture 동기화
- common error parity: auth status·세부 `errorCode` 의미를 유지한 versioned `RestError`·`StompFatalError` fixture

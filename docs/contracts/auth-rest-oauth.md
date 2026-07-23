# Auth Rest Oauth BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### local register, login과 logout

- `GET /api/v1/auth/consents/current`는 `no-store`의 `{schemaVersion:"1",termsVersion,privacyPolicyVersion}`를 반환하며 가입·OAuth onboarding은 이 current version과 정확히 일치해야 한다.
- `POST /api/v1/auth/local/register`는 `{email,password,nickname,termsVersion,privacyPolicyVersion,termsAgreed:true,privacyPolicyAgreed:true}`를 받는다.
- active email 또는 nickname 충돌은 사용자 승인에 따라 충돌 field를 밝히지 않는 `409 REGISTRATION_CONFLICT` 하나로 반환한다.
- current consent version 불일치는 `409 CONSENT_VERSION_OUTDATED`와 current 두 version을 반환하며 자동 재제출하지 않고 재동의를 받는다.
- 가입 성공은 `201`과 `UNVERIFIED` 최소 상태를 반환하고 rotated 제한 session을 만든다. email 인증 전에는 인증 관련 허용 route 외 주요 기능을 사용할 수 없다.
- account와 hashed verification token 저장 뒤 SMTP 즉시 1회 발송이 실패하면 account와 제한 session은 유지하고 `502 EMAIL_DELIVERY_FAILED`의 안전한 가입 상태 variant를 반환한다. FE는 가입을 rollback하거나 자동 재등록하지 않고 resend 흐름으로 전환한다.
- `POST /api/v1/auth/local/login`은 `{email,password}`를 받고 성공 `200`과 `/auth/session` 동일 projection을 반환하며 session을 회전한다.
- 없는 email과 틀린 password는 같은 `401 INVALID_CREDENTIALS`와 timing 범주를 사용한다. 잠금은 `429 ACCOUNT_LOCKED`와 delta-seconds `Retry-After`를 사용하되 email 존재, 실패 횟수와 내부 상태를 추가 노출하지 않는다.
- `POST /api/v1/auth/logout`은 session+CSRF를 검증하고 `204`로 현재 browser session·CSRF·STOMP만 폐기한다.

### email verification과 password reset

- `POST /api/v1/auth/email-verification/resend`는 `UNVERIFIED` local session+CSRF에서 body 없이 호출하며 성공 `202`다. 새 5분 token은 이전 미사용 token을 무효화한다. 실제 발송 실패는 `502 EMAIL_DELIVERY_FAILED`다.
- verification email link는 same-origin `/auth/email-verification#token={base64url-token}`을 사용한다. reset은 `/auth/password-reset#token={base64url-token}`, local reactivation은 `/auth/reactivation/local#token={base64url-token}`이다. token은 43~128자이고 fragment에는 token key 하나만 허용한다. fragment는 server request에 전달되지 않으며 FE는 읽은 즉시 history에서 제거하고 storage/log/observability에 남기지 않는다.
- `POST /api/v1/auth/email-verification/confirm`은 token을 body로 단회 제출한다. 성공 `204`, invalid/expired/reused는 `400 EMAIL_VERIFICATION_TOKEN_INVALID` 하나를 사용한다. token만으로 다른 browser에 인증 session을 새로 만들지 않는다.
- 가입 때 생성된 기존 `UNVERIFIED` 제한 session browser는 confirm 뒤 `/auth/session` bootstrap으로 `ACTIVE`를 관찰한다.
- `POST /api/v1/auth/password-reset/request`는 `{email}`을 받고 account 존재와 SMTP 성공·실패 여부에 관계없이 동일 `202`를 반환한다. delivery 실패는 안전한 운영 관측에만 남긴다.
- reset link도 token을 fragment로 전달하고 즉시 제거한 뒤 `POST /api/v1/auth/password-reset/confirm` body의 `{token,newPassword}`로 단회 제출한다.
- reset token invalid/expired/reused는 `400 PASSWORD_RESET_TOKEN_INVALID` 하나를 사용한다.
- reset confirm 성공은 token 소비, 실패 횟수·잠금 초기화, 해당 사용자 모든 기존 session·STOMP 폐기를 원자적으로 수행한다. 요청 browser도 새 anonymous session/CSRF 문맥으로 bootstrap하며 자동 login하지 않는다.

### OAuth login과 onboarding

- `GET /api/v1/auth/oauth/{provider}/start`는 `google|kakao`만 허용하고 top-level browser navigation으로 provider에 redirect한다.
- server는 고엔트로피 OAuth `state`를 server session, provider와 purpose에 만료·단회로 결합한다. login과 reactivation purpose를 분리한다.
- `GET /api/v1/auth/oauth/{provider}/callback`은 code/state/provider/session/purpose를 검증하고 provider token과 identity를 server에서만 처리한다.
- callback 결과는 server session에 일회 저장한 뒤 항상 `303 /auth/oauth/complete`로 redirect한다. SPA URL, history, referrer, client state와 observability에 code, state, provider token, email과 provider subject를 넣지 않는다.
- `GET /api/v1/auth/oauth/result`는 `Cache-Control: no-store`의 single-consumer outcome을 반환한다. purpose별 outcome은 closure registry의 비민감 닫힌 union이고, pending result가 없는 새 session·reload·back·다중 탭 비승자는 purpose를 추정하지 않는 `purpose:null,outcome:NO_PENDING_OAUTH_RESULT` variant로 수렴한다.
- FE completion route는 auth guard redirect 전에 result를 한 번 소비하고 일반 TanStack Query cache, retry, focus/reconnect refetch를 사용하지 않는다. reload·back·다중 탭의 비승자 소비자는 `NO_PENDING_OAUTH_RESULT` 뒤 session bootstrap으로 수렴한다.
- 신규 OAuth identity는 제한 session에서 `POST /api/v1/auth/oauth/onboarding`의 nickname·terms/privacy version·동의를 완료한다. 성공 뒤 session을 재회전하고 bootstrap한다.
- active local account와 같은 email 충돌은 `LOCAL_EMAIL_COLLISION`만 반환하고 local account 인증, 자동 linking과 새 OAuth account 생성을 하지 않는다.

### session과 route

- session rotation 뒤 FE는 이전 CSRF, session-scope STOMP와 민감 cache를 폐기하고 `CSRF bootstrap → /auth/session → route 결정` 순서를 다시 수행한다.
- bootstrap 완료 전 route guard는 redirect하지 않는다.
- `UNVERIFIED`는 email confirm/resend, password reset, logout과 최소 session 상태만 허용한다. `SUSPENDED`는 제한 안내, logout과 최소 session 상태만 허용한다. `WITHDRAWN`은 login session을 만들 수 없다.
- expected auth/account 오류는 route error boundary가 아닌 feature 상태로 처리한다.

### withdrawal과 reactivation

- withdrawal은 account를 물리 삭제하지 않고 `WITHDRAWN`으로 전환하며 기존 nickname·기록을 유지하고 해당 사용자 모든 session·STOMP를 폐기한다.
- reactivation은 새 account row를 만들지 않고 동일 가입 identity를 검증해 기존 account, nickname과 기록을 복원한다. local/OAuth linking은 만들지 않는다.
- withdrawal 전 local account는 current password, OAuth account는 동일 provider fresh reauthorization을 반드시 요구한다.
- local reactivation은 기존 password와 5분 email token을 모두 요구한다. OAuth reactivation은 동일 provider reauthorization을 요구하며 provider 이용 불가 복구는 MVP에서 제외한다.
- proof는 authenticated session, account identity와 `withdrawal` 또는 `reactivation` purpose에 결합하고 다른 용도에 재사용하지 않는다. 구체 endpoint·payload는 BE 2차 검토에서 닫힌 schema로 확정한다.

#### withdrawal endpoint와 proof

- `POST /api/v1/auth/withdrawal`은 session+CSRF를 요구하고 account 가입 방식별 닫힌 request variant를 사용한다.
- local variant는 `{method:"LOCAL",currentPassword}`를 받아 password 검증과 `ACTIVE|UNVERIFIED|SUSPENDED → WITHDRAWN`, 전체 session·CSRF·STOMP 폐기를 한 transaction으로 처리한다.
- OAuth variant는 `{method:"OAUTH"}`를 받고 현재 session에 결합된 미사용 withdrawal proof를 원자 소비한다. client가 provider나 accountId를 지정하지 않는다.
- `GET /api/v1/auth/oauth/withdrawal/start`는 현재 account의 provider를 server가 선택하고 `WITHDRAWAL` purpose, account, provider와 originating session에 state를 결합해 provider로 redirect한다.
- 공통 OAuth callback이 `WITHDRAWAL` state를 받으면 동일 `provider+providerUserId`를 검증해 5분·단회 withdrawal proof를 server session에 저장할 뿐 account 상태를 바꾸지 않는다.
- OAuth result는 `WITHDRAWAL_REAUTHENTICATED`, `CANCELLED`, `FAILED`의 비민감 outcome을 단회 반환한다. 실제 withdrawal은 이후 CSRF POST가 수행한다.
- withdrawal 오류는 `UNAUTHENTICATED`, `REAUTHENTICATION_FAILED`, `REAUTHENTICATION_PROOF_REQUIRED`, `AUTH_METHOD_MISMATCH`, `ACCOUNT_STATE_CONFLICT`, `RATE_LIMITED`의 닫힌 variant를 사용한다.

#### local reactivation

- `POST /api/v1/auth/reactivation/local/start`는 `{email,password}`를 받고 형식이 정상인 경우 account 존재·상태·password·SMTP 결과와 무관한 동일 `202`를 반환한다.
- 일치하는 `WITHDRAWN` local identity에만 account/purpose에 결합된 hashed 5분·단회 token을 발급해 즉시 한 번 발송하며 새 token은 이전 미사용 token을 무효화한다.
- `POST /api/v1/auth/reactivation/local/confirm`은 `{token}`을 받고 token 소비, 기존 account row의 활성화, 기존 nickname·기록 유지와 인증 session 생성·회전을 한 transaction으로 처리한다.
- 성공은 `200`과 `/auth/session` 동일 projection이다. invalid/expired/reused token은 존재를 숨기는 `REACTIVATION_TOKEN_INVALID`, 동시 상태 변경은 `ACCOUNT_STATE_CONFLICT`다.

#### OAuth reactivation

- `GET /api/v1/auth/oauth/{provider}/reactivation/start`는 anonymous CSRF session에 `REACTIVATION` purpose, provider와 state를 결합해 provider로 redirect한다.
- callback은 동일 `provider+providerUserId`의 `WITHDRAWN` row만 원자 복원하고 기존 nickname·기록을 유지하며 인증 session을 생성·회전한다.
- result는 `REACTIVATED`, `CANCELLED`, `FAILED`의 비민감 outcome만 고정 completion route에서 단회 제공한다.
- active account login, 신규 OAuth 가입과 local email collision은 reactivation으로 우회하지 않고 기존 OAuth flow로 처리한다.
- provider 불일치·이용 불가 복구와 local/OAuth linking은 MVP에서 제공하지 않는다.

#### proof 보안과 concurrency

- OAuth state/proof는 purpose, accountId, provider, providerUserId와 originating session에 결합하고 5분 만료·단회·원자 소비한다.
- local token은 purpose/account에 결합해 hash로 저장하고 평문은 발송 시점 외 저장하지 않는다.
- 동시 confirm, callback과 withdrawal 중 하나만 성공하며 나머지는 state conflict 또는 consumed proof/token 오류다.
- code, state, token, proof, email, provider token과 session ID는 redirect URL, response, log와 trace에 포함하지 않는다.

## 오류 포맷과 사용자 표시 영향

- session provider와 route guard가 bootstrap, 제한 session, rotation과 logout/reset/withdrawal 뒤 수렴을 소유한다.
- email token은 fragment에서 즉시 제거해 POST adapter로 한 번만 전달한다.
- OAuth completion은 비캐시 단회 consumer이며 closed outcome으로 onboarding/login/collision/recovery를 mapping한다.
- generated OpenAPI client와 common error adapter를 사용하고 auth mutation을 임의 자동 retry하지 않는다.

## 구현 메모

- auth application이 token hash·5분·단회·재발급 무효화, login lock, session rotation/invalidation과 SMTP 결과를 원자적 상태 규칙에 맞게 처리한다.
- OAuth adapter가 state의 session/provider/purpose/expiry/single-use와 callback secret 처리를 server-only로 보장한다.
- account adapter는 soft withdrawal과 same-row reactivation을 보장하고 record/nickname identity를 유지한다.
- withdrawal과 reactivation adapter는 purpose-bound proof의 발급·소비, 가입 방식 일치와 동시 상태 전이를 원자적으로 강제한다.

## 테스트/fixture/드리프트 검증

- OpenAPI: 모든 local/OAuth endpoint, closed request/response/outcome, CSRF, session cookie와 common error variant
- token: 5분 경계, 단회, 재발급 뒤 이전 token, fragment 제거, query/storage/log 비노출, 다른 browser confirm 비로그인
- login: unknown/wrong-password parity, 5회·10분 lock, reset 뒤 lock 초기화와 전체 session 폐기
- OAuth: expired/reused/wrong-session/wrong-provider/wrong-purpose state, callback URL 비밀정보 부재, single-consumer result, reload/back/multi-tab, local collision, onboarding rotation
- MSW: 제한 session, register delivery failure 유지, reset 동일 `202`, outcome 재소비와 common error
- Playwright: local signup→verify→login, reset anonymous bootstrap, OAuth success/cancel/failure/collision/onboarding, logout/withdrawal multi-tab convergence
- withdrawal/reactivation: wrong password/provider/purpose/session, proof·token 만료/재사용, 동일 `202` enumeration parity, same-row/nickname 유지, OAuth reauth 뒤 final CSRF withdrawal
- drift gate: OpenAPI, generated client, MSW와 fixture fingerprint 불일치를 CI에서 차단

# Canonical REST Operation Registry

## 공통 security와 error set

- `PUBLIC`: 인증 불필요.
- `ANON_CSRF`: anonymous session cookie와 CSRF header required.
- `USER`: authenticated session required.
- `ACTIVE`: USER + 주요 기능 허용 account state. communication suspension은 해당 endpoint가 별도 금지하지 않으면 허용.
- `ADMIN`: ACTIVE + ADMIN role. account suspension은 role보다 우선한다.
- `MUT`: CSRF required. `IDEM`: `Idempotency-Key` required.

Manifest security profile은 다음 literal로 닫는다. `MUT`, `IDEM`, `AUDITED_READ`는 각각 boolean 속성으로 전개한다.

- `PUBLIC`: session 불필요, account/role constraint 없음.
- `PUBLIC_SESSION`: anonymous 또는 authenticated server session 필요, account/role constraint 없음.
- `ANON_CSRF`: server session과 CSRF 필요, authenticated account 불필요.
- `USER`: authenticated non-WITHDRAWN account.
- `USER_ANY_ACCOUNT_STATUS`: authenticated `ACTIVE|UNVERIFIED|SUSPENDED` account.
- `UNVERIFIED_LOCAL`: authenticated local `UNVERIFIED` account.
- `OAUTH_ONBOARDING_RESTRICTED`: authenticated OAuth onboarding restricted account.
- `ACTIVE`: authenticated ACTIVE account.
- `ACTIVE_OWNER`: ACTIVE이며 path resource owner.
- `ACTIVE_PARTICIPANT`: ACTIVE이며 종료 경기 participant.
- `CURRENT_GAME_PARTICIPANT`: authenticated current active-game participant.
- `ADMIN`: ACTIVE와 ADMIN role.
- `ADMIN_AUDITED`: ADMIN이며 audit commit-before-response.
- `OAUTH_PURPOSE_SESSION`: server session에 유효하거나 실패로 소비할 OAuth purpose/state 문맥이 있음.

Error set은 manifest 생성 시 아래 code별 ErrorVariant로 전개한다.

- `BASE_INPUT`: `400 MALFORMED_REQUEST | VALIDATION_FAILED`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR`.
- `USER_ACCESS`: `401 UNAUTHENTICATED`, `403 EMAIL_UNVERIFIED | ACCOUNT_SUSPENDED`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR`.
- `RESTRICTED_USER_ACCESS`: `401 UNAUTHENTICATED`, `403 ACCOUNT_SUSPENDED`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR`. endpoint가 허용한 미완료 상태를 오류로 되돌리지 않는다.
- `ACTIVE_ACCESS`: USER_ACCESS와 동일하되 endpoint 성공 eligibility가 ACTIVE다.
- `ADMIN_ACCESS`: `401 UNAUTHENTICATED`, `403 EMAIL_UNVERIFIED | ACCOUNT_SUSPENDED | FORBIDDEN`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR`.
- `CSRF`: `403 CSRF_INVALID`.
- `IDEMPOTENCY`: `409 COMMAND_CONFLICT`.
- 각 operation은 표의 set과 특수 error만 허용하며 다른 global code를 임의 반환하지 않는다.
- `Cache-Control: no-store`는 CSRF/session/current-consent/OAuth-result, 모든 `/api/v1/me/**`, 모든 일반 사용자 community, current game chat, 모든 block/report와 `/api/v1/admin/**` success/error 응답에 required다. community·block/report·admin과 `/me/**`의 `204`도 포함한다. manifest의 각 해당 SuccessVariant/ErrorVariant `requiredHeaders`에 전개하며 OAuth `302/303`과 catalog `304`에는 각 fixed endpoint가 명시한 header만 둔다.

## Auth operations

| operationId | method/path | security | request | success variants | errors |
| --- | --- | --- | --- | --- | --- |
| `getCsrfToken` | GET `/api/v1/auth/csrf` | PUBLIC | NO_BODY | `200 CsrfTokenResponse`, no-store | `500 INTERNAL_ERROR` |
| `getAuthSession` | GET `/api/v1/auth/session` | PUBLIC | NO_BODY | `200 AuthSession`, no-store | `500 INTERNAL_ERROR` |
| `getCurrentConsents` | GET `/api/v1/auth/consents/current` | PUBLIC | NO_BODY | `200 CurrentConsentsResponse`, no-store | `429 RATE_LIMITED`, `500 INTERNAL_ERROR` |
| `registerLocalAccount` | POST `/api/v1/auth/local/register` | ANON_CSRF | LocalRegistrationRequest | `201 AuthSession` | BASE_INPUT, CSRF, `409 REGISTRATION_CONFLICT | CONSENT_VERSION_OUTDATED`, `502 EMAIL_DELIVERY_FAILED` |
| `loginLocalAccount` | POST `/api/v1/auth/local/login` | ANON_CSRF | LocalLoginRequest | `200 AuthSession` | BASE_INPUT, CSRF, `401 INVALID_CREDENTIALS`, `429 ACCOUNT_LOCKED` |
| `logoutCurrentSession` | POST `/api/v1/auth/logout` | USER+MUT | NO_BODY | `204 NO_BODY` | `401 UNAUTHENTICATED`, CSRF, `500 INTERNAL_ERROR` |
| `resendEmailVerification` | POST `/api/v1/auth/email-verification/resend` | UNVERIFIED_LOCAL+MUT | NO_BODY | `202 NO_BODY` | RESTRICTED_USER_ACCESS, CSRF, `403 AUTH_METHOD_MISMATCH`, `409 ACCOUNT_STATE_CONFLICT`, `502 EMAIL_DELIVERY_FAILED` |
| `confirmEmailVerification` | POST `/api/v1/auth/email-verification/confirm` | ANON_CSRF | EmailVerificationConfirmRequest | `204 NO_BODY` | BASE_INPUT, CSRF, `400 EMAIL_VERIFICATION_TOKEN_INVALID` |
| `requestPasswordReset` | POST `/api/v1/auth/password-reset/request` | ANON_CSRF | PasswordResetRequest | `202 NO_BODY` | BASE_INPUT, CSRF |
| `confirmPasswordReset` | POST `/api/v1/auth/password-reset/confirm` | ANON_CSRF | PasswordResetConfirmRequest | `204 NO_BODY` | BASE_INPUT, CSRF, `400 PASSWORD_RESET_TOKEN_INVALID` |
| `startOAuthLogin` | GET `/api/v1/auth/oauth/{provider}/start` | PUBLIC_SESSION | provider path | `302 NO_BODY + Location` | `400 VALIDATION_FAILED`, `500 INTERNAL_ERROR` |
| `handleOAuthCallback` | GET `/api/v1/auth/oauth/{provider}/callback` | OAUTH_PURPOSE_SESSION | provider path + callback query variants | `303 NO_BODY + Location:/auth/oauth/complete` | callback semantic/structural failure도 303 result로 수렴, result persistence/redirect 불능 `500`만 |
| `getOAuthResult` | GET `/api/v1/auth/oauth/result` | PUBLIC_SESSION | NO_BODY | `200 OAuthResult`, no-store | `500 INTERNAL_ERROR` |
| `completeOAuthOnboarding` | POST `/api/v1/auth/oauth/onboarding` | OAUTH_ONBOARDING_RESTRICTED+MUT | OAuthOnboardingRequest | `200 AuthSession` | RESTRICTED_USER_ACCESS, CSRF, `403 AUTH_METHOD_MISMATCH`, `409 ACCOUNT_STATE_CONFLICT | REGISTRATION_CONFLICT | CONSENT_VERSION_OUTDATED` |
| `withdrawAccount` | POST `/api/v1/auth/withdrawal` | USER+MUT | WithdrawalRequest oneOf | `204 NO_BODY` | `401 UNAUTHENTICATED`, CSRF, `403 REAUTHENTICATION_FAILED | REAUTHENTICATION_PROOF_REQUIRED | AUTH_METHOD_MISMATCH`, `409 ACCOUNT_STATE_CONFLICT`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR` |
| `startOAuthWithdrawal` | GET `/api/v1/auth/oauth/withdrawal/start` | USER | NO_BODY | `302 NO_BODY + Location` | `401 UNAUTHENTICATED`, `403 ACCOUNT_SUSPENDED`, `500 INTERNAL_ERROR` |
| `startLocalReactivation` | POST `/api/v1/auth/reactivation/local/start` | ANON_CSRF | LocalReactivationStartRequest | `202 NO_BODY` | BASE_INPUT, CSRF |
| `confirmLocalReactivation` | POST `/api/v1/auth/reactivation/local/confirm` | ANON_CSRF | LocalReactivationConfirmRequest | `200 AuthSession` | BASE_INPUT, CSRF, `400 REACTIVATION_TOKEN_INVALID`, `409 ACCOUNT_STATE_CONFLICT` |
| `startOAuthReactivation` | GET `/api/v1/auth/oauth/{provider}/reactivation/start` | PUBLIC_SESSION | provider path | `302 NO_BODY + Location` | `400 VALIDATION_FAILED`, `500 INTERNAL_ERROR` |

`OAuthResult`는 purpose별 세 final variant와 `{schemaVersion:"1",purpose:null,outcome:"FAILED"|"NO_PENDING_OAUTH_RESULT"}` 독립 variant다. callback secret/code/state는 response/error에 없다.

Callback query는 다음 known variant를 해석한다.

- success: required `code,state`, optional provider `scope,authuser,prompt`.
- provider failure/cancel: required `error`, optional `state,error_description,error_uri`.
- exact session/provider/purpose/expiry에 state가 일치하고 `error:"access_denied"`인 경우만 purpose-specific `CANCELLED`, 그 외 valid-state provider error는 purpose-specific `FAILED`다. missing/invalid/reused state와 목적을 권위적으로 고를 수 없는 누락·혼합 조합은 `purpose:null,outcome:"FAILED"`를 저장하고 303으로 수렴한다.
- 알 수 없는 provider query는 무시하되 response, result, log와 redirect URL에 반사하지 않는다. provider token 교환이나 result 저장 자체의 infrastructure failure만 `500 INTERNAL_ERROR`다.

### Out-of-band mail navigation

- verification mail은 same-origin `/auth/email-verification#token={token}`, password reset mail은 `/auth/password-reset#token={token}`, local reactivation mail은 `/auth/reactivation/local#token={token}`만 사용한다.
- `{token}`은 43~128자의 base64url `[A-Za-z0-9_-]` 문자열이다. fragment에는 `token` 한 key만 허용하며 query, path segment와 server-side request/log/referrer에는 token을 넣지 않는다.
- FE는 route 진입 시 fragment를 한 번 읽어 문법 검증 후 즉시 `history.replaceState`로 전체 fragment를 제거하고 token을 memory의 해당 confirm command에만 전달한다. invalid/missing fragment는 POST하지 않는 local invalid-link 상태다.
- bundle은 세 mail URL positive, query/path token과 extra/duplicate fragment key privacy-negative, invalid alphabet/length structural-negative fixture를 포함한다.

## Identity operations

| operationId | method/path | security | request | success | errors |
| --- | --- | --- | --- | --- | --- |
| `getMyProfile` | GET `/api/v1/me/profile` | ACTIVE | NO_BODY | `200 MyProfileResponse` | ACTIVE_ACCESS |
| `getMyAccessStatus` | GET `/api/v1/me/access-status` | USER_ANY_ACCOUNT_STATUS | NO_BODY | `200 AccessStatusResponse` | `401 UNAUTHENTICATED`, `500 INTERNAL_ERROR` |
| `getMySettings` | GET `/api/v1/me/settings` | ACTIVE | NO_BODY | `200 SettingsView` | ACTIVE_ACCESS |
| `replaceMySettings` | PUT `/api/v1/me/settings` | ACTIVE+MUT | ReplaceSettingsRequest | `200 SettingsView` | ACTIVE_ACCESS, CSRF, `409 SETTINGS_CHANGED` |
| `listMyNotifications` | GET `/api/v1/me/notifications` | ACTIVE | query `{cursor?}` | `200 NotificationPage` | ACTIVE_ACCESS, `400 VALIDATION_FAILED` |

## Card, collection, pack and deck

| operationId | method/path | security | request | success | errors |
| --- | --- | --- | --- | --- | --- |
| `listActiveCardCatalog` | GET `/api/v1/cards/catalog` | ACTIVE | optional `If-None-Match` | `200 CardCatalogResponse + ETag`; `304 NO_BODY + ETag` | ACTIVE_ACCESS |
| `getMyCardCollection` | GET `/api/v1/me/card-collection` | ACTIVE | NO_BODY | `200 CardCollectionView` | ACTIVE_ACCESS |
| `getBasicCardPack` | GET `/api/v1/card-packs/basic` | ACTIVE | NO_BODY | `200 BasicPackView` | ACTIVE_ACCESS |
| `openBasicCardPack` | POST `/api/v1/card-packs/basic/openings` | ACTIVE+MUT+IDEM | EmptyJsonObject | `201 BasicPackOpeningResult` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `429 RATE_LIMITED` |
| `getMyDeck` | GET `/api/v1/me/deck` | ACTIVE | NO_BODY | `200 DeckView` | ACTIVE_ACCESS |
| `replaceMyDeck` | PUT `/api/v1/me/deck` | ACTIVE+MUT | ReplaceDeckRequest | `200 DeckView` | ACTIVE_ACCESS, CSRF, `400 VALIDATION_FAILED`, `409 DECK_REVISION_MISMATCH` |

`CardCatalogResponse = {schemaVersion,catalogViewFingerprint,cards:CardDefinitionView[]}`이며 cards는 결정적 정렬이다. ETag는 catalogViewFingerprint와 동일하다.

## Matchmaking, history, chat and community

| operationId | method/path | security | request | success | errors |
| --- | --- | --- | --- | --- | --- |
| `createQuickMatchAttempt` | POST `/api/v1/matchmaking/quick` | ACTIVE+MUT+IDEM | CreateQuickMatchAttemptRequest | new `201`, existing `200` QuickMatchStateView | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `409 GAME_IN_PROGRESS`, deck/account validation은 `400 VALIDATION_FAILED` |
| `getQuickMatchAttempt` | GET `/api/v1/matchmaking/quick` | ACTIVE | NO_BODY | `200 QuickMatchStateView` | ACTIVE_ACCESS, `404 RESOURCE_NOT_FOUND` |
| `cancelQuickMatchAttempt` | DELETE `/api/v1/matchmaking/quick` | ACTIVE+MUT+IDEM | NO_BODY | `200 QuickMatchStateView(CANCELED)` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `409 MATCH_ALREADY_CONFIRMED` |
| `getMyMatchHistorySummary` | GET `/api/v1/me/match-history/summary` | ACTIVE | NO_BODY | `200 MatchHistorySummary` | ACTIVE_ACCESS |
| `listMyMatches` | GET `/api/v1/me/match-history/matches` | ACTIVE | query `{cursor?}` | `200 MatchHistoryPage` | ACTIVE_ACCESS, `400 VALIDATION_FAILED` |
| `getMyMatchReplay` | GET `/api/v1/me/match-history/matches/{gameId}/replay` | ACTIVE_PARTICIPANT | gameId path | `200 MatchReplay` | ACTIVE_ACCESS, `404 RESOURCE_NOT_FOUND` |
| `listCurrentGameChatMessages` | GET `/api/v1/games/{gameId}/chat/messages` | CURRENT_GAME_PARTICIPANT | path `{gameId}`, query `{cursor?}` | `200 ChatMessagePage`, no-store | USER_ACCESS, `400 VALIDATION_FAILED`, `404 RESOURCE_NOT_FOUND`, `409 CHAT_CLOSED` |
| `listCommunityPosts` | GET `/api/v1/community/posts` | ACTIVE | query `{cursor?,q?}` | `200 CommunityPostPage` | ACTIVE_ACCESS, `400 VALIDATION_FAILED` |
| `getCommunityPost` | GET `/api/v1/community/posts/{postId}` | ACTIVE | path `{postId}` | `200 CommunityPostView` | ACTIVE_ACCESS, `404 RESOURCE_NOT_FOUND` |
| `createCommunityPost` | POST `/api/v1/community/posts` | ACTIVE+MUT+IDEM | CreateCommunityPostRequest | `201 CommunityPostView` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `403 COMMUNICATION_SUSPENDED`, `400 VALIDATION_FAILED` |
| `updateCommunityPost` | PATCH `/api/v1/community/posts/{postId}` | ACTIVE_OWNER+MUT+IDEM | UpdateCommunityPostRequest | `200 CommunityPostView` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `403 COMMUNICATION_SUSPENDED`, `404 RESOURCE_NOT_FOUND`, `409 POST_REVISION_MISMATCH` |
| `deleteCommunityPost` | DELETE `/api/v1/community/posts/{postId}` | ACTIVE_OWNER+MUT+IDEM | DeleteCommunityPostRequest | `204 NO_BODY` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `403 COMMUNICATION_SUSPENDED`, `404 RESOURCE_NOT_FOUND`, `409 POST_REVISION_MISMATCH` |

`MATCH_ALREADY_CONFIRMED` variant는 base와 `currentMatchmakingState:QuickMatchStateView`를 required로 가진다. 다른 error에는 이 field를 금지한다.

## Trust and admin operations

| operationId | method/path | security | request | success | errors |
| --- | --- | --- | --- | --- | --- |
| `listMyBlocks` | GET `/api/v1/me/blocks` | ACTIVE | query `{cursor?}` | `200 Page<BlockView>` | ACTIVE_ACCESS, `400 VALIDATION_FAILED` |
| `createBlock` | POST `/api/v1/me/blocks` | ACTIVE+MUT+IDEM | CreateBlockRequest | first `201`, existing `200` BlockResponse | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND` |
| `deleteBlock` | DELETE `/api/v1/me/blocks/{blockId}` | ACTIVE+MUT+IDEM | DeleteBlockRequest | `204 NO_BODY` | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 BLOCK_CHANGED` |
| `createReport` | POST `/api/v1/reports` | ACTIVE+MUT+IDEM | CreateReportRequest | new `201`, duplicate `200` OwnReportResponse | ACTIVE_ACCESS, CSRF, IDEMPOTENCY, `403 COMMUNICATION_SUSPENDED` for chat/post, `404 RESOURCE_NOT_FOUND` |
| `getMyReport` | GET `/api/v1/me/reports/{reportId}` | ACTIVE | path `{reportId}` | `200 OwnReportResponse` | ACTIVE_ACCESS, `404 RESOURCE_NOT_FOUND` |
| `listAdminReportCases` | GET `/api/v1/admin/report-cases` | ADMIN | query `{cursor?,status?,targetType?,reportedFrom?,reportedTo?}` | `200 Page<ReportCaseListItem>` | ADMIN_ACCESS, `400 VALIDATION_FAILED` |
| `getAdminReportCase` | GET `/api/v1/admin/report-cases/{caseId}` | ADMIN_AUDITED | path `{caseId}` | `200 ReportCaseResponse` | ADMIN_ACCESS, `404 RESOURCE_NOT_FOUND` |
| `accessAdminRawEvidence` | POST `/api/v1/admin/report-cases/{caseId}/reports/{reportId}/raw-evidence-accesses` | ADMIN+MUT | EmptyJsonObject | `200 RawEvidenceResponse` | ADMIN_ACCESS, CSRF, `404 RESOURCE_NOT_FOUND`, `410 EVIDENCE_UNAVAILABLE` |
| `resolveAdminReportCase` | POST `/api/v1/admin/report-cases/{caseId}/resolutions` | ADMIN+MUT+IDEM | ResolveReportCaseRequest oneOf | `200 ReportCaseResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 REPORT_CASE_CHANGED | REPORT_CASE_RESOLVED | REPORT_ACTION_INVALID` plus embedded action conflict |
| `moderateAdminCommunityPost` | POST `/api/v1/admin/community/posts/{postId}/moderation-actions` | ADMIN+MUT+IDEM | ModerateCommunityPostRequest | `200 ModerationActionResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 POST_REVISION_MISMATCH | MODERATION_STATE_CONFLICT | REPORT_ACTION_INVALID` |
| `searchAdminUsers` | GET `/api/v1/admin/users` | ADMIN | query `{q,cursor?}` | `200 Page<AdminUserSearchItem>` | ADMIN_ACCESS, `400 VALIDATION_FAILED` |
| `listAdminUserSanctions` | GET `/api/v1/admin/users/{subjectRef}/sanctions` | ADMIN | path `{subjectRef}`, query `{cursor?}` | `200 Page<SanctionView>` | ADMIN_ACCESS, `400 VALIDATION_FAILED`, `404 RESOURCE_NOT_FOUND` |
| `createAdminSanction` | POST `/api/v1/admin/users/{subjectRef}/sanctions` | ADMIN+MUT+IDEM | CreateSanctionRequest | `201 CreateSanctionResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND` including self, `409 SANCTION_ALREADY_ACTIVE | REPORT_ACTION_INVALID` |
| `extendAdminSanction` | PATCH `/api/v1/admin/sanctions/{sanctionId}` | ADMIN+MUT+IDEM | ExtendSanctionRequest | `200 SanctionActionResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 SANCTION_CHANGED | SANCTION_NOT_ACTIVE` |
| `revokeAdminSanction` | POST `/api/v1/admin/sanctions/{sanctionId}/revocations` | ADMIN+MUT+IDEM | RevokeSanctionRequest | `200 SanctionActionResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 SANCTION_CHANGED | SANCTION_NOT_ACTIVE` |
| `listAdminForbiddenWords` | GET `/api/v1/admin/forbidden-words` | ADMIN | query `{q?,cursor?}` | `200 Page<ForbiddenWordView>` | ADMIN_ACCESS, `400 VALIDATION_FAILED` |
| `createAdminForbiddenWord` | POST `/api/v1/admin/forbidden-words` | ADMIN+MUT+IDEM | CreateForbiddenWordRequest | `201 ForbiddenWordResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `400 VALIDATION_FAILED`, `409 FORBIDDEN_WORD_DUPLICATE` |
| `updateAdminForbiddenWord` | PATCH `/api/v1/admin/forbidden-words/{forbiddenWordId}` | ADMIN+MUT+IDEM | UpdateForbiddenWordRequest | `200 ForbiddenWordResponse` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `400 VALIDATION_FAILED`, `404 RESOURCE_NOT_FOUND`, `409 FORBIDDEN_WORD_DUPLICATE | FORBIDDEN_WORD_CHANGED` |
| `deleteAdminForbiddenWord` | DELETE `/api/v1/admin/forbidden-words/{forbiddenWordId}` | ADMIN+MUT+IDEM | DeleteForbiddenWordRequest | `204 NO_BODY` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `404 RESOURCE_NOT_FOUND`, `409 FORBIDDEN_WORD_CHANGED` |
| `listAdminCards` | GET `/api/v1/admin/cards` | ADMIN_AUDITED | query `{q?,cardType?,cursor?}` | `200 Page<CardDefinitionView>` | ADMIN_ACCESS, `400 VALIDATION_FAILED` |
| `createAdminAnnouncement` | POST `/api/v1/admin/announcements` | ADMIN+MUT+IDEM | CreateAnnouncementRequest | `201 AnnouncementCreateResult` | ADMIN_ACCESS, CSRF, IDEMPOTENCY, `400 VALIDATION_FAILED` |

`CreateSanctionRequest = {expectedSanctionSetRevision,sanctionType,duration,reason,sourceCaseId?}`. duration은 fixed preset/custom oneOf다.

## Parameter registry

- 모든 `{...Id}`, `{subjectRef}` path parameter는 비어 있지 않은 URL-encoded opaque string이며 slash를 포함하지 않는다. `{provider}`는 `google | kakao` 소문자 literal이다.
- `cursor`는 생략 가능하고 present 시 비어 있지 않은 opaque base64url string이다. 빈 문자열, 중복 query key와 알려지지 않은 query parameter는 `400 VALIDATION_FAILED`다.
- `q`는 trim 후 1~100 Unicode code point plain text다. `searchAdminUsers`에서만 required이고 나머지는 optional이다.
- `status`는 `OPEN | RESOLVED`, `targetType`은 `CHAT_MESSAGE | COMMUNITY_POST | USER_PROFILE`, `cardType`은 `NORMAL | LEGEND`다.
- `reportedFrom,reportedTo`는 UTC millisecond `Z` timestamp이고 둘 다 있으면 from ≤ to다.
- `If-None-Match`는 선택적 quoted catalog fingerprint 한 값만 허용한다. `Idempotency-Key`는 MUT+IDEM operation에서 required인 1~128 ASCII visible character opaque value다.
- 표에 열거되지 않은 path/query/header parameter는 허용하지 않는다. 단, OAuth provider callback은 앞의 callback query 규칙이 우선하여 unknown key는 무시하고 duplicate/mixed/missing 조합은 `FAILED` result와 303으로 수렴한다. 그 외 operation의 unknown/duplicate parameter는 `400 VALIDATION_FAILED`다. manifest는 각 항목을 location/name/required/schemaRef로 전개한다.

## Registry completeness

- 총 63개 operationId가 unique하다.
- 각 success status, redirect와 304는 manifest의 별도 SuccessVariant다.
- 표에 없는 status/code, security scope, header와 body variant는 허용하지 않는다.

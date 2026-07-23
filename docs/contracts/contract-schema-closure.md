# Contract Schema Closure BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

## 공통 schema 규칙

- REST는 OpenAPI 3.1, STOMP는 JSON Schema draft 2020-12를 canonical authored source로 사용한다.
- 모든 JSON 최종 객체는 `additionalProperties: false`다. request optional property는 생략만 허용하고 명시적 `null`을 금지한다. response nullable property는 required이며 값에만 `null` union을 허용한다.
- JSON success body는 `schemaVersion: "1"`을 required literal로 가진다. `202/204` no-body 응답에는 JSON body를 두지 않는다.
- ID는 비어 있지 않은 opaque string, count·revision·version·ordinal은 JSON safe nonnegative integer, 시각은 UTC millisecond `Z`, square는 `^[a-h][1-8]$`다.
- enum·discriminator·required/null/forbidden 조건을 schema `oneOf`로 닫는다. unknown discriminator, 추가 field, 미지원 schema version은 FE cache/reducer 진입 전 fatal contract drift다.
- canonical `CardDefinitionRef`와 `CardDefinitionView`는 `contract-fixture` 정의를 직접 `$ref`하고 alias 또는 부분 재선언을 금지한다.

## Auth와 consent exact wire

### AuthSession

- anonymous: `{schemaVersion,authenticated:false}`
- authenticated: `{schemaVersion,authenticated:true,accountStatus,roles,activeRestrictions}`
- `accountStatus`: `ACTIVE | UNVERIFIED | SUSPENDED`
- `roles`: 중복 없는 결정적 정렬의 `USER | ADMIN` 배열
- `activeRestrictions`: 중복 없는 결정적 정렬의 `ACCOUNT_SUSPENSION | COMMUNICATION_SUSPENSION` 배열

### endpoint closure

| endpoint | request | success |
| --- | --- | --- |
| `GET /api/v1/auth/consents/current` | 없음 | `200 {schemaVersion,termsVersion,privacyPolicyVersion}`, `no-store` |
| `POST /api/v1/auth/local/register` | `{email,password,nickname,termsVersion,privacyPolicyVersion,termsAgreed:true,privacyPolicyAgreed:true}` | `201 AuthSession(UNVERIFIED)` |
| `POST /api/v1/auth/local/login` | `{email,password}` | `200 AuthSession` |
| `POST /api/v1/auth/logout` | 없음 | `204` |
| `POST /api/v1/auth/email-verification/resend` | body 없음 | `202` |
| `POST /api/v1/auth/email-verification/confirm` | `{token}` | `204` |
| `POST /api/v1/auth/password-reset/request` | `{email}` | 항상 `202` |
| `POST /api/v1/auth/password-reset/confirm` | `{token,newPassword}` | `204` |
| `POST /api/v1/auth/oauth/onboarding` | `{nickname,termsVersion,privacyPolicyVersion,termsAgreed:true,privacyPolicyAgreed:true}` | `200 AuthSession` |
| `POST /api/v1/auth/reactivation/local/start` | `{email,password}` | 항상 `202` |
| `POST /api/v1/auth/reactivation/local/confirm` | `{token}` | `200 AuthSession` |

- 현재 consent version과 다르면 `409 CONSENT_VERSION_OUTDATED`에 `currentTermsVersion,currentPrivacyPolicyVersion`을 required로 제공한다. FE는 새 버전을 표시하고 재동의를 받으며 자동 재제출하지 않는다.
- active email 또는 nickname 가입 충돌은 사용자 승인에 따라 field 없는 `409 REGISTRATION_CONFLICT` 하나로 반환한다. 어떤 값이 충돌했는지, account 존재·상태와 재활성화 가능 여부를 body에 넣지 않는다.
- register SMTP 실패는 account와 제한 session을 유지한 `502 EMAIL_DELIVERY_FAILED`이며 이 endpoint variant에만 `registrationStatus:"UNVERIFIED"`를 required로 둔다. resend SMTP 실패 variant에는 추가 field가 없다.
- email verification invalid/expired/reused는 `EMAIL_VERIFICATION_TOKEN_INVALID`, password reset은 `PASSWORD_RESET_TOKEN_INVALID`, local reactivation은 `REACTIVATION_TOKEN_INVALID` 하나로 각각 합쳐 존재·상태를 숨긴다.
- endpoint purpose별 OAuth result는 서로 다른 닫힌 union이다. login은 `AUTHENTICATED | ONBOARDING_REQUIRED | LOCAL_EMAIL_COLLISION | CANCELLED | FAILED`, withdrawal은 `WITHDRAWAL_REAUTHENTICATED | CANCELLED | FAILED`, reactivation은 `REACTIVATED | CANCELLED | FAILED`다. state를 신뢰할 수 없는 callback 실패는 `{purpose:null,outcome:"FAILED"}`, pending result가 없으면 `{purpose:null,outcome:"NO_PENDING_OAUTH_RESULT"}`를 반환한다.

## Common error registry

### envelope와 조건 field

- 추가 field 없는 base variant는 정확히 `{schemaVersion,errorCode,message,traceId}`다.
- `VALIDATION_FAILED`: `fieldErrors[]` required. 각 item은 `{field,errorCode,message}`이며 `field`는 RFC 6901 pointer다.
- `MALFORMED_REQUEST`: `fieldErrors` forbidden.
- `RATE_LIMITED | ACCOUNT_LOCKED`: REST `Retry-After`와 body `retryAfterSeconds` required. STOMP는 body만 사용한다.
- `GAME_IN_PROGRESS`: 요청자 자신의 `gameId`만 추가한다.
- `STATE_VERSION_MISMATCH`: parsed game application error에 `actionId,gameId,stateVersion,transitionId,resyncRequired:true` required.
- `DECK_REVISION_MISMATCH | POST_REVISION_MISMATCH`: `currentRevision,resyncRequired:true` required.
- `SETTINGS_CHANGED | BLOCK_CHANGED | REPORT_CASE_CHANGED | SANCTION_CHANGED | FORBIDDEN_WORD_CHANGED`: `currentRevision` required.
- `CONSENT_VERSION_OUTDATED`: current consent version 두 field required.
- `MATCH_ALREADY_CONFIRMED`: `currentMatchmakingState` required이며 canonical `QuickMatchStateView`를 직접 참조한다.
- register `EMAIL_DELIVERY_FAILED`: `registrationStatus:"UNVERIFIED"` required. 그 외 variant에는 금지한다.
- REST, game parsed, game malformed, chat parsed, chat malformed과 fatal 오류는 `rest-registry.md`와 `stomp-registry.md`의 transport/context별 final union을 사용한다. 조건 field가 열거되지 않은 해당 variant에는 허용된 correlation 외 field를 금지한다.

### REST status registry

| status | errorCode |
| --- | --- |
| 400 | `MALFORMED_REQUEST`, `VALIDATION_FAILED`, `EMAIL_VERIFICATION_TOKEN_INVALID`, `PASSWORD_RESET_TOKEN_INVALID`, `REACTIVATION_TOKEN_INVALID` |
| 401 | `UNAUTHENTICATED`, `INVALID_CREDENTIALS` |
| 403 | `CSRF_INVALID`, `FORBIDDEN`, `EMAIL_UNVERIFIED`, `ACCOUNT_SUSPENDED`, `COMMUNICATION_SUSPENDED`, `REAUTHENTICATION_FAILED`, `REAUTHENTICATION_PROOF_REQUIRED`, `AUTH_METHOD_MISMATCH` |
| 404 | `RESOURCE_NOT_FOUND` |
| 409 | `REGISTRATION_CONFLICT`, `COMMAND_CONFLICT`, `MATCH_ALREADY_CONFIRMED`, `GAME_IN_PROGRESS`, `STATE_VERSION_MISMATCH`, `ACCOUNT_STATE_CONFLICT`, `CONSENT_VERSION_OUTDATED`, `DECK_REVISION_MISMATCH`, `POST_REVISION_MISMATCH`, `SETTINGS_CHANGED`, `BLOCK_CHANGED`, `GAME_NOT_ACTIVE`, `CHAT_CLOSED`, `REPORT_CASE_CHANGED`, `REPORT_CASE_RESOLVED`, `REPORT_ACTION_INVALID`, `MODERATION_STATE_CONFLICT`, `SANCTION_CHANGED`, `SANCTION_ALREADY_ACTIVE`, `SANCTION_NOT_ACTIVE`, `FORBIDDEN_WORD_DUPLICATE`, `FORBIDDEN_WORD_CHANGED` |
| 410 | `EVIDENCE_UNAVAILABLE` |
| 429 | `RATE_LIMITED`, `ACCOUNT_LOCKED` |
| 500 | `INTERNAL_ERROR` |
| 502 | `EMAIL_DELIVERY_FAILED` |

- `DECK_CHANGED | DECK_INVALID | ACCOUNT_NOT_ELIGIBLE | MATCH_CREATION_FAILED`는 matchmaking terminal state의 `failureCode`이며 REST errorCode가 아니다.
- 카드 발동 후 효과 실패는 committed game event이며 REST/STOMP application error가 아니다.
- `ORIGIN_REJECTED`는 handshake/fatal 관측용이며 readable REST error body를 보장하지 않는다.

## Matchmaking exact wire

- `QuickMatchStateView`는 공통 `{schemaVersion,queueEntryId,state,stateVersion,serverTime}`를 가진 닫힌 union이다.
- `WAITING | CANCELED | MATCH_CONFIRMED`에는 추가 field가 없다.
- `GAME_CREATED`에는 `gameId,ownColor`가 required다.
- `FAILED`에는 `failureCode`가 required이며 `DECK_CHANGED | DECK_INVALID | ACCOUNT_NOT_ELIGIBLE | MATCH_CREATION_FAILED`만 허용한다.
- 상대 조건, 상대 identity, block 관계, MMR/range와 상대 deck은 금지한다. 상대 조건 실패는 failure로 노출하지 않고 재탐색한다.
- 개인 event는 `{schemaVersion,messageType:"MATCHMAKING_STATE_CHANGED",eventId,queueEntryId,state,stateVersion,serverTime,payload}`다. 빈 상태 payload는 정확히 `{}`, `GAME_CREATED`는 `{gameId,ownColor}`, `FAILED`는 `{failureCode}`다.

## Game sync와 transition exact wire

### sync와 receipt

- `SEND /app/games/{gameId}/sync`: `{schemaVersion:"1",requestId,gameId}`. path/body gameId 불일치와 추가 identity/version/projection field를 거부한다.
- snapshot envelope: `{schemaVersion,messageType:"GAME_VIEWER_SNAPSHOT",requestId,gameId,stateVersion,projectionScope:"VIEWER_PRIVATE",serverTime,payload}`.
- success receipt: `{schemaVersion,messageType:"GAME_COMMAND_ACCEPTED",actionId,gameId,stateVersion,transitionId}`. receipt 자체는 version cursor를 전진시키지 않는다.
- transition outer는 `{schemaVersion,messageType:"GAME_TRANSITION",eventId,gameId,stateVersion,transitionId,serverTime,payload}`다. public payload는 `{projectionScope:"PUBLIC",events,privateSequencesAfter}`이고 viewer-private payload는 `{projectionScope:"VIEWER_PRIVATE",viewerPrivateSequence,events}`다. public sequence 배열은 WHITE/BLACK 두 viewer의 해당 commit 뒤 private cursor를 순서대로 제공한다.
- public/private envelope는 같은 transition cursor를 공유하되 eventId는 다르다. public transition만 FE cursor를 전진시키고 private event는 해당 viewer state를 보강한다.
- public after private cursor가 +1인데 buffer에 exact private가 없으면 2,000ms 단회 grace 뒤 sync한다. grace 중 reconnect 또는 새 public cursor가 오면 즉시 sync하며 tail loss를 무기한 기다리지 않는다.

### ViewerGameState

- required fields: `ownColor,fen,turnNumber,turnColor,phase,players,publicGeneralHands,ownGeneralHand,ownUnusedLegend,visibleCardDefinitions,pendingCardEffect,ownPendingCardEffect,pendingPromotion,timer,terminalOutcome,opponentActions,lastViewerPrivateSequence`.
- `phase`: `TURN_START | PRE_MOVE | PIECE_MOVE | PROMOTION | POST_MOVE | EFFECT_PENDING | TURN_END | GAME_ENDED`.
- `players`는 WHITE/BLACK 순의 `{color,mana,checkReceivedCount,remainingGeneralDeckCount}` 두 item이다.
- `publicGeneralHands`는 color별 집계 ref/count, `ownGeneralHand`는 actor instance/ref, `ownUnusedLegend`는 nullable actor instance/ref다.
- `visibleCardDefinitions`는 현재 viewer projection이 실제 참조하는 canonical view만 포함한다. 상대 미사용 레전드와 숨은 deck definition은 금지한다.
- `pendingCardEffect`는 public `{actorColor,definitionRef,originPhase}`, `ownPendingCardEffect`는 actor-only `{activationId,cardInstanceId,definitionRef,activationBaseStateVersion,originPhase,candidates}` nullable union이다.
- `pendingPromotion`은 PROMOTION phase에서만 `{from,to,color,choices:[QUEEN,ROOK,BISHOP,KNIGHT]}`이고 그 외 null이다.
- timer는 `{timerState:"RUNNING",activeColor,whiteRemainingMillis,blackRemainingMillis,zeroAt,graceEndsAt}` 또는 `{timerState:"STOPPED",whiteRemainingMillis,blackRemainingMillis}`다.
- terminal outcome은 nonterminal에서 null, terminal에서 `{outcomeType:"DECISIVE",winnerColor,loserColor} | {outcomeType:"DRAW"} | {outcomeType:"INVALID"}`다.
- `opponentActions`는 actor-private `{subjectRef,canBlock,canReportProfile}`이며 public transition과 replay에 금지한다.

### 19개 GameEvent payload registry

| eventType | required payload | 조건/금지 |
| --- | --- | --- |
| `TURN_STARTED` | `turnNumber,turnColor` |  |
| `PHASE_CHANGED` | `fromPhase,toPhase` | 같은 phase 금지 |
| `PRE_MOVE_SKIPPED` | `actorColor` |  |
| `PIECE_MOVED` | `actorColor,from,to,movedPieceType,moveKind,capture,secondaryMove,notation,resultingFen` | moveKind별 capture/castling/promotion oneOf |
| `PROMOTION_REQUIRED` | `actorColor,from,to,choices` | UCI/SAN 금지 |
| `PROMOTION_COMPLETED` | `actorColor,from,to,pieceType,uci,san,resultingFen` | 승격 4종만 |
| `CARD_ACTIVATED` | public `actorColor,usedDefinition,actorPublicGeneralHandAfter` | actor private에만 activationId/cardInstanceId |
| `EFFECT_PENDING` | public `actorColor,definitionRef,originPhase` | actor private에만 full own pending |
| `CARD_EFFECT_APPLIED` | public `actorColor,usedDefinition,outcome` | actor private에만 canonical selection/activation; outcome resultingFen 권위 |
| `CARD_EFFECT_FAILED` | public `actorColor,usedDefinition` | private failure만 `SELECTION_NOT_CANDIDATE | EFFECT_NOT_APPLICABLE | KING_SAFETY_VIOLATION | GAME_INVARIANT_VIOLATION`; public 상세 금지 |
| `CARD_DRAWN` | `actorColor,drawnDefinition,actorPublicGeneralHandAfter,remainingGeneralDeckCountAfter` |  |
| `POST_MOVE_PASSED` | `actorColor` |  |
| `MANA_CHANGED` | `color,before,after,delta,reasonCode` | reason `TURN_START | CAPTURE | EN_PASSANT_CAPTURE | CHECK_RECEIVED_THRESHOLD | CARD_COST` |
| `CHECK_DECLARED` | `checkingColor,checkedColor,checkReceivedCountAfter,doubleCheck` | 서로 다른 color |
| `TURN_ENDED` | `turnNumber,turnColor` |  |
| `TIMER_UPDATED` | `timer` | UI tick event 금지 |
| `GAME_ENDED` | `reasonCode,terminalOutcome,endedAt` | reason/outcome mapping 고정 |
| `PRIVATE_HAND_UPDATED` | `ownGeneralHandAfter` | viewer-private actor only |
| `PRIVATE_LEGEND_UPDATED` | `ownUnusedLegendAfter` | viewer-private actor only |

- end reason은 `CHECKMATE | STALEMATE | INSUFFICIENT_MATERIAL | FIFTY_MOVE_RULE | THREEFOLD_REPETITION | TIME_FORFEIT | DISCONNECT_FORFEIT | RESIGNATION | SERVER_ABORTED`다.
- decisive reason은 `CHECKMATE,TIME_FORFEIT,DISCONNECT_FORFEIT,RESIGNATION`, draw reason은 네 표준 무승부, invalid reason은 `SERVER_ABORTED`다.
- public event에는 `actionId,cardInstanceId,activationId,candidates,raw selection,상세 실패,subjectRef`를 금지한다.

## Match history exact wire

- summary: `{schemaVersion,countedMatches,wins,losses,draws,winRate}`. count 합계 불변식과 `winRate` 한 자리 decimal string을 검증한다.
- list: `{schemaVersion,items,nextCursor}` 최대 10개. item은 `{gameId,opponent,color,startedAt,endedAt,reasonCode,result}`다.
- opponent는 `ACTIVE{nickname} | WITHDRAWN`, result는 viewer-relative `WIN | LOSS | DRAW`다. list는 전적에 반영되는 정상 종료 경기만 포함하므로 `SERVER_ABORTED`와 `INVALID`를 금지한다. 무효 경기 replay는 참가자 접근을 유지한다.
- replay: `{schemaVersion,gameId,viewerColor,startedAt,endedAt,terminalOutcome,initialState,steps,visibleCardDefinitions}`.
- step: `{stepIndex,stateVersion,transitionId,serverTime,events,stateAfter}`. index와 event ordinal은 0부터 연속이고 `stateAfter`가 권위다.
- replay `events`는 live public union을 재사용하지 않는 별도 `ReplayGameEvent[]`다. card occurrence는 top-level historical definition registry를 선행한 ref-only variant다.
- `initialState,stateAfter`는 별도 closed `ReplayGameState`를 사용한다. live `ViewerGameState`를 직접 `$ref`하지 않는다.
- `ReplayGameState`는 live state에서 `opponentActions`, `ownPendingCardEffect`, `lastViewerPrivateSequence`를 제거하고, pending은 공개 `{actorColor,definitionRef,originPhase}`만 허용한다. actor 후보·activation/card instance, receipt/error/connection metadata와 상대 미사용 레전드·raw selection·상세 실패를 금지한다.
- replay는 current handler를 재실행하지 않고 저장 transition/stateAfter와 historical `CardDefinitionView`를 사용한다.

## Community와 trust/admin schema merge

- `CommunityPostView` required는 `postId,revision,title,body,author,capabilities,authorActions,createdAt,contentUpdatedAt`다.
- `capabilities`는 `{canEdit,canDelete,canReportPost}` 하나로 합치고 `authorActions`는 `null | {subjectRef,canBlock,canReportProfile}`다.
- self/withdrawn 또는 가능한 author action이 없으면 null이다. raw author ID, report count, block·moderation state는 금지한다.
- block/report/case/raw evidence/resolution/moderation/sanction/forbidden-word/announcement은 `trust-safety-admin-rest`의 endpoint 의미를 유지하고 이 문서의 common page/error/null 규칙을 사용한다.
- page는 `{schemaVersion,items,nextCursor}`이며 nextCursor는 required nullable이다.
- report view는 `OPEN`이면 `resolvedAt,result` null, `RESOLVED`이면 둘 다 non-null인 oneOf다.
- raw evidence는 chat/post/profile oneOf이며 `EVIDENCE_UNAVAILABLE`는 `410`이다. raw access는 receipt와 자동 retry가 없다.
- case resolution은 `NO_ACTION`, `ACTION_TAKEN+EXISTING_ACTION`, `ACTION_TAKEN+CREATE_SANCTION`, `ACTION_TAKEN+HIDE_POST` oneOf이며 target ID는 case에서 server가 결정한다.
- 관리자 카드 응답 item은 canonical `CardDefinitionView`를 직접 `$ref`한다. required field는 `cardId,cardVersion,definitionFingerprint,viewFingerprint,name,type,packId,image,timing,manaCost,summary,useGuide,selectionKind`이며 `version,description,cardType,publicEffectRepresentation` alias를 금지한다.
- 공지 eligible population은 사용자 승인에 따라 transaction snapshot의 모든 non-WITHDRAWN account다. UNVERIFIED, ACCOUNT_SUSPENDED와 관리자도 포함한다. NORMAL은 notification enabled 계정만 inbox 생성, IMPORTANT는 모든 eligible 계정에 생성한다. 현재 access restriction은 inbox 열람에서 그대로 적용한다.
- 공지 success `{schemaVersion,announcementId,importance,createdAt,eligibleCount,deliveredCount,skippedCount}`는 `eligibleCount = deliveredCount + skippedCount`를 만족한다.

### trust/admin endpoint closure

| endpoint | request | success |
| --- | --- | --- |
| `GET /api/v1/me/blocks` | cursor query | `200 Page<BlockView>` |
| `POST /api/v1/me/blocks` | `{subjectRef}` | first `201`, existing `200`, `{schemaVersion,block}` |
| `DELETE /api/v1/me/blocks/{blockId}` | `{expectedRevision}` | `204` |
| `POST /api/v1/reports` | `{target,reasonCode,detail?}` | new `201`, semantic duplicate `200`, `{schemaVersion,report}` |
| `GET /api/v1/me/reports/{reportId}` | 없음 | `200 {schemaVersion,report}` |
| `GET /api/v1/admin/report-cases` | fixed filter/cursor query | `200 Page<ReportCaseListItem>` |
| `GET /api/v1/admin/report-cases/{caseId}` | 없음 | `200 {schemaVersion,case}`; audit commit-before-response |
| `POST /api/v1/admin/report-cases/{caseId}/reports/{reportId}/raw-evidence-accesses` | 정확히 `{}` | `200` chat/post/profile evidence oneOf; receipt 없음 |
| `POST /api/v1/admin/report-cases/{caseId}/resolutions` | resolution oneOf + expectedRevision | `200 {schemaVersion,case}` |
| `POST /api/v1/admin/community/posts/{postId}/moderation-actions` | `{expectedRevision,action,reason,sourceCaseId?}` | `200 {schemaVersion,moderationAction}` |
| `GET /api/v1/admin/users` | required `q`, cursor | `200 Page<AdminUserSearchItem>` |
| `GET /api/v1/admin/users/{subjectRef}/sanctions` | cursor | `200 Page<SanctionView>` |
| `POST /api/v1/admin/users/{subjectRef}/sanctions` | create sanction command | `201 {schemaVersion,sanction,sanctionSetRevision,actionRef}` |
| `PATCH /api/v1/admin/sanctions/{sanctionId}` | `{expectedRevision,endsAt}` | `200 {schemaVersion,sanction,actionRef}` |
| `POST /api/v1/admin/sanctions/{sanctionId}/revocations` | `{expectedRevision,reason}` | `200 {schemaVersion,sanction,actionRef}` |
| `GET /api/v1/admin/forbidden-words` | q/cursor | `200 Page<ForbiddenWordView>` |
| `POST /api/v1/admin/forbidden-words` | `{value,changeReason}` | `201 {schemaVersion,forbiddenWord}` |
| `PATCH /api/v1/admin/forbidden-words/{forbiddenWordId}` | `{expectedRevision,value,changeReason}` | `200 {schemaVersion,forbiddenWord}` |
| `DELETE /api/v1/admin/forbidden-words/{forbiddenWordId}` | `{expectedRevision,changeReason}` | `204` |
| `GET /api/v1/admin/cards` | q/cardType/cursor | `200 Page<CardDefinitionView>` |
| `POST /api/v1/admin/announcements` | `{title,body,importance}` | `201` count result |

- `BlockView`: `{blockId,revision,blockedUser,blockedAt}`, blockedUser는 `ACTIVE{nickname} | WITHDRAWN`다. stale delete는 `BLOCK_CHANGED{currentRevision}`, inaccessible/self/invalid ref는 동일 404다.
- report target은 `CHAT_MESSAGE{chatMessageId} | COMMUNITY_POST{postId} | USER_PROFILE{subjectRef}`다. reason은 fixed 6종, detail은 present 시 1~500 code point다.
- `OwnReportView`는 `{reportId,targetType,reasonCode,submittedAt,status,resolvedAt,result}`이며 OPEN은 마지막 두 field null, RESOLVED는 non-null이다.
- `ReportCaseListItem`: `{caseId,revision,targetType,status,createdAt,latestReportedAt,memberReportCount,resolvedAt,result}`. case detail은 target, member reports, evidence availability와 qualifying action refs를 포함하되 raw evidence는 포함하지 않는다.
- raw evidence는 `CHAT_MESSAGE`, `COMMUNITY_POST`, `USER_PROFILE` discriminator oneOf다. case/report membership 불일치는 404, expiry는 410이며 raw/detail을 error·receipt·log에 넣지 않는다.
- resolution은 `NO_ACTION`, `EXISTING_ACTION`, `CREATE_SANCTION`, `HIDE_POST` source oneOf다. ACTION_TAKEN은 정확히 하나의 source가 필수이고 target은 case가 결정한다.
- moderation stale은 `POST_REVISION_MISMATCH`, invalid transition은 `MODERATION_STATE_CONFLICT`다. restore는 qualifying ACTION_TAKEN source가 아니다.
- sanction duration은 `PRESET_DAYS{1|3|7|30} | CUSTOM_ENDS_AT`, status는 `ACTIVE | EXPIRED | REVOKED`다. same type active, stale, inactive와 source case conflict는 registry의 닫힌 409 variant를 사용한다.
- forbidden word duplicate/stale은 `FORBIDDEN_WORD_DUPLICATE | FORBIDDEN_WORD_CHANGED`; PATCH는 실제 value 변경을 요구한다.
- 접근 검사는 authentication → account state → admin role → structural schema → target-type communication restriction → exact receipt → resource/revision 순이다.

## Canonical manifest와 fixture closure

- manifest required root: `schemaVersion,bundleFormatVersion,jsonSchemaDialect,hashAlgorithm,files,openapi,stomp,fixtures,cardContracts,rootFingerprint`.
- fixed literal: schema/bundle format `"1"`, dialect draft 2020-12, hash `SHA-256-RFC8785`.
- `files[]`는 bundle-relative path, mediaType, role, sha256을 가지며 path 정렬·중복·escape·미참조·누락·stale file을 검증한다. manifest 파일 자체는 `files[]`와 per-file hash 대상에서 제외해 self-reference를 만들지 않는다.
- `rootFingerprint` 계산 projection은 manifest의 `rootFingerprint` property만 제외하며 `files[]`는 위 authored/generated data file closure만 포함한다.
- `openapi.operations[]`는 모든 fixed REST operation의 operationId/method/path/request/success/error schema ref와 fixture ID를 정확히 한 번 포함한다.
- `stomp.channels[]`는 direction, destination pattern, `MESSAGE_TYPE | INTENT | NONE` wire discriminator variant, schema ref, authorization scope와 fixture ID를 포함한다. CONNECT/fatal, game command/sync/public/private, matchmaking, chat send/private channel을 모두 포함한다.
- `fixtures[]`는 `POSITIVE | STRUCTURAL_NEGATIVE | DOMAIN_NEGATIVE | PRIVACY_NEGATIVE | SEQUENCE | PROVENANCE_DRIFT` class와 transport/target/path/hash를 가진다.
- 모든 operation/message/union variant는 positive fixture를 가지며 required 누락, 추가 field, wrong discriminator/status/conditional field와 privacy leakage negative fixture를 가진다.
- 모든 `$ref`는 bundle root 내부 상대 참조만 허용하고 external ref/runtime URL/registry ref를 금지한다.
- root fingerprint는 자기 field를 제외한 RFC 8785 canonical manifest value의 SHA-256이다. source Git commit은 manifest에 넣지 않고 FE adoption metadata가 canonical repo identity, full 40-character BE commit, bundle root와 expected root fingerprint를 고정한다.

## 오류 포맷과 사용자 표시 영향

- generated TypeScript가 AuthSession, OAuth result, RestError, matchmaking state, ViewerGameState, 19 events, replay outcome와 trust/admin union을 직접 생성하며 수기 union 확장을 금지한다.
- 모든 discriminated switch는 exhaustive 처리하고 schema 검증 실패는 query cache/reducer 전에 fatal drift로 차단한다.
- snapshot/stateAfter는 원자 교체하고 outcome 좌표를 FEN에 재적용하거나 current card handler로 replay하지 않는다.
- MSW, fake STOMP, Ajv와 Playwright는 canonical fixture와 generated type만 사용한다.

## 구현 메모

- OpenAPI/STOMP serializer는 allowlist DTO만 사용하고 임의 Map, exception, internal entity를 노출하지 않는다.
- public/private projection과 error conditional field를 schema variant에 맞춰 생성한다.
- canonical authored source에서 clean bundle·manifest·fixture closure를 결정적으로 재생성한다.

## 테스트/fixture/드리프트 검증

- auth: register 201/502 session bootstrap, generic registration conflict, stale consent 재동의, token safe error, OAuth single consumer.
- error: 모든 status/code, required/forbidden conditional field, wrong status/header, public STOMP error와 privacy field 거부.
- game/match: snapshot 원자 교체, 19 variant, receipt/transition 역순, duplicate/gap/resync, end reason mapping과 public/private leakage.
- replay: count invariant, 10-item cursor, withdrawn opponent, random seek/stateAfter, historical definition과 privacy.
- trust/admin: capability merge, report status nullability, case action source cardinality, evidence expiry, revision conflicts, announcement counts와 canonical card `$ref`.
- bundle: clean regeneration, manifest closure, per-file/root hash, unmanifested/stale/missing, external ref, pin/copy/fingerprint-only 변경과 generated output drift.

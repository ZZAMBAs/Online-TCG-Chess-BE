# Trust Safety Admin Rest BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### 공통 형식과 권한

- 모든 JSON 응답은 `schemaVersion: "1"`, 모든 객체는 `additionalProperties: false`인 닫힌 schema다.
- user/report/admin 응답은 `Cache-Control: no-store`다.
- mutation은 session과 CSRF를 검사하고 생성·해제·처리·moderation·sanction·dictionary command는 persistent `Idempotency-Key`를 요구한다.
- 같은 authorized principal/operation/key와 같은 canonical command는 최초 terminal result를 replay하고 다른 command는 `409 COMMAND_CONFLICT`다.
- idempotency receipt lookup은 current session, role, account와 target-type restriction matrix를 통과한 뒤 current resource state/revision 검사보다 먼저 수행한다.
- ADMIN route는 server가 매 request마다 role과 account state를 검증한다. account suspension은 ADMIN role보다 우선한다.
- raw evidence access, audited report case detail과 audited admin card query는 일반 자동 retry/prefetch/focus refetch를 사용하지 않는다.

### action-scoped subjectRef

- 일반 user mutation target에는 internal account ID나 직접 입력 nickname을 사용하지 않고 server-issued opaque `subjectRef`를 사용한다.
- `subjectRef`는 viewer, canonical target account, source context, allowed actions와 expiry에 결합되며 client가 구성할 수 없다.
- community active author projection은 nullable `authorActions {subjectRef,canBlock,canReportProfile}`과 post capability `canReportPost`를 제공한다.
- self post에서는 report/profile/block capability가 false이고 withdrawn author에는 subjectRef가 없다.
- gameplay actor-private viewer snapshot은 `opponentActions {subjectRef,canBlock,canReportProfile}`을 제공한다.
- subjectRef와 capability는 public game topic, match-history/replay, ChatMessageView, 상대 projection과 일반 log에 포함하지 않는다.
- chat report는 이미 받은 `chatMessageId`를 사용하며 chat payload에 account ID/subjectRef를 추가하지 않는다.

### 사용자 block

- `GET /api/v1/me/blocks?cursor={opaque}`는 최대 20개, `(blockedAt DESC,blockId DESC)` user-bound keyset page를 반환한다.
- `BlockView`는 `blockId`, nonnegative `revision`, `blockedUser: ACTIVE{nickname}|WITHDRAWN`, `blockedAt`만 포함한다.
- `POST /api/v1/me/blocks` body는 `{subjectRef}`이고 Idempotency-Key를 요구한다. first create는 `201`, already-blocked relation은 새 row 없이 current view `200`이다.
- `DELETE /api/v1/me/blocks/{blockId}` body는 `{expectedRevision}`이고 Idempotency-Key를 요구한다. success/exact replay는 `204`다.
- stale active relation은 `409 BLOCK_CHANGED`와 currentRevision, invalid/self/expired/non-viewer ref와 inaccessible relation은 identity를 숨기는 동일 `404 RESOURCE_NOT_FOUND`다.
- block/unblock commit, matchmaking candidate/final check와 match-chat recipient eligibility decision은 하나의 논리 순서로 선형화한다.
- block 관계, 차단자 identity와 matchmaking 제외 이유는 상대에게 노출하지 않는다.

### 사용자 report 제출과 조회

- `POST /api/v1/reports`는 Idempotency-Key와 닫힌 target union을 사용한다.
  - `CHAT_MESSAGE {chatMessageId}`
  - `COMMUNITY_POST {postId}`
  - `USER_PROFILE {subjectRef}`
- reason code는 `HARASSMENT | HATE_SPEECH | SEXUAL_CONTENT | SPAM | INAPPROPRIATE_NAME | OTHER`다.
- optional detail은 최대 500 Unicode code point이고 present whitespace-only를 거부하며 plain text다.
- community post는 same reporter/canonical post에 lifetime one report만 허용한다. OPEN/RESOLVED duplicate는 새 row/case 없이 existing own projection `200`이다.
- chat message와 user profile은 same reporter/canonical target의 open report 하나만 허용하고, resolved 뒤 same target submission은 new report와 new open case를 만들 수 있다. different subjectRef가 same account를 가리키면 같은 profile target이다.
- self target, non-visible chat, hidden/deleted/expired post와 invalid/expired subjectRef는 target 정보를 숨기는 동일 404다.
- `GET /api/v1/me/reports/{reportId}`는 owner only이며 unknown/non-owner는 동일 404다. user report list는 MVP에 없다.
- own view는 `reportId`, `targetType`, `reasonCode`, `submittedAt`, `status`, nullable `resolvedAt`, nullable `result`만 포함한다.
- status는 `OPEN | RESOLVED`; OPEN result는 null, RESOLVED result는 `ACTION_TAKEN | NO_ACTION`이다.
- 다른 reporter 수/identity, case ID, linked action/sanction/moderation, admin identity/memo와 evidence는 user view에 없다.

### evidence snapshot과 expiry

- report submission transaction에서 target별 immutable evidence snapshot을 저장한다.
- chat: raw/masked content와 최소 game/message/sender/reporter/sentAt metadata.
- post: 신고 당시 revision, raw/masked title/body와 author 최소 reference.
- profile: 당시 display nickname과 access-controlled target linkage.
- reporter optional detail도 evidence에 포함한다.
- case/report resolve 시각부터 30일이 지나면 cleanup 실행 지연과 무관하게 evidence를 `EXPIRED`로 계산하고 raw access를 즉시 거부한다.
- raw/masked content, profile nickname snapshot과 optional detail은 삭제한다. report/case ID, target type/linkage, reason code, result/timestamps, linked actions와 audit는 보존한다.
- future backup/PITR architecture는 restore 후 service open 전에 expired cleanup을 재실행하거나 동등한 deletion guarantee를 제공해야 한다.

### admin report case queue/detail

- admin queue unit은 same canonical target의 open individual reports를 묶은 case다.
- `GET /api/v1/admin/report-cases?cursor=&status=&targetType=&reportedFrom=&reportedTo=`는 최대 20개 `(createdAt DESC,caseId DESC)` keyset page이며 cursor는 admin/filter에 결합한다.
- `GET /api/v1/admin/report-cases/{caseId}`는 case revision, status/result, masked target/evidence summary, admin-scoped reporter/target refs, member reports와 `evidenceAvailability: AVAILABLE|EXPIRED`를 제공한다.
- report와 case status는 `OPEN|RESOLVED`; IN_REVIEW, assignment, reopen과 appeal은 MVP에 없다.
- canonical target별 open case 하나를 DB constraint/serialization으로 보장한다.
- report가 resolve보다 먼저 case에 가입하면 같은 resolution에 포함되고 resolve가 먼저면 후속 report가 new open case를 만든다.

### explicit admin raw evidence access

- `POST /api/v1/admin/report-cases/{caseId}/reports/{reportId}/raw-evidence-accesses` body는 `{}`이고 CSRF가 필수다.
- raw response는 chat/post/profile target별 닫힌 evidence union이다.
- current ADMIN/account state와 case/report membership/evidence availability를 검증하고 audit row commit 성공 뒤에만 raw response를 반환한다.
- raw access는 Idempotency-Key와 persistent response receipt를 사용하지 않는다. 매 successful access는 새 audit action이다.
- raw response/detail query는 FE prefetch, auto retry, focus/reconnect refetch를 금지하고 route exit, role loss, logout/session invalidation 때 cache를 제거한다.
- raw/evidence를 response receipt, general log/trace/metric, URL과 FE persistent storage에서 보존하지 않는다.
- expired evidence는 `EVIDENCE_UNAVAILABLE` closed error이며 audit/backing application store에서 복원할 수 없다.

### case resolution과 linked action

- `POST /api/v1/admin/report-cases/{caseId}/resolutions`는 `expectedRevision`, persistent Idempotency-Key와 닫힌 result union을 사용한다.
- `NO_ACTION`은 linked action을 포함하지 않는다.
- `ACTION_TAKEN`은 정확히 하나의 qualifying action source가 필수다.
  - command에 포함된 new `CREATE_SANCTION` 또는 `HIDE_POST` action 하나
  - 또는 same case에 이미 immutable link된 auto-hide/admin-hide/sanction-create/sanction-extend 등 실제 state-changing action reference 하나
- new action이면 action/audit, case resolution, all open member report resolution과 reporter notification creation을 same transaction에 확정한다.
- existing action이면 resolution transaction에서 immutable link와 qualifying state change를 lock/validate하고 action을 재실행하지 않는다.
- action 없는 ACTION_TAKEN은 거부한다. actual action 없이 resolve할 때는 NO_ACTION만 허용한다.
- resolved case의 new resolution은 closed 409 conflict이고 exact replay만 최초 result를 반환한다.
- all member reports receive same result. fixed optional notification rule에 따라 reporter inbox가 disabled이면 report original은 resolve하되 optional REPORT_RESOLVED inbox row는 만들지 않는다.

### admin community moderation

- `POST /api/v1/admin/community/posts/{postId}/moderation-actions` command는 `expectedRevision`, `action:HIDE|RESTORE`, trim 1~500 Unicode code point mandatory plain-text `reason`, optional case linkage와 Idempotency-Key를 사용한다.
- HIDE는 `ACTIVE → MANUAL_HIDDEN`, RESTORE는 `AUTO_HIDDEN|MANUAL_HIDDEN → ACTIVE`다. DELETED restore는 없다.
- post revision/state transition과 audit를 same transaction에 확정한다.
- restore는 original createdAt/raw/masked content와 keyset position을 유지하고 remask하지 않는다.
- stale revision은 `409 POST_REVISION_MISMATCH`; already-hidden HIDE, active RESTORE와 other terminal-invalid new command는 closed conflict다. exact replay만 success receipt를 재생한다.

### admin sanction

- `GET /api/v1/admin/users?q=&cursor=`는 nickname/admin-scoped user ref 검색과 최대 20 keyset page를 제공한다.
- `GET /api/v1/admin/users/{subjectRef}/sanctions?cursor=`는 sanction history를 반환한다.
- `POST /api/v1/admin/users/{subjectRef}/sanctions`는 immediate-start sanction create다.
- `PATCH /api/v1/admin/sanctions/{sanctionId}`는 active sanction `endsAt` extension이고 expectedRevision/Idempotency-Key를 요구한다.
- `POST /api/v1/admin/sanctions/{sanctionId}/revocations`는 expectedRevision, mandatory revoke reason과 Idempotency-Key를 요구한다.
- type은 `COMMUNICATION_SUSPENSION | ACCOUNT_SUSPENSION`이다.
- duration은 preset `1|3|7|30` days 또는 commit 기준 1시간~365일 future custom endsAt union이다. scheduled start는 없다.
- same account/type active sanction은 하나이고 extension은 overlapping row 대신 current sanction revision/endsAt을 갱신한다.
- 두 type은 함께 존재할 수 있고 account suspension이 effective access에서 우선한다.
- self-sanction은 금지한다.
- public/revoke reason은 trim 1~500 Unicode code point mandatory plain text고 source report/case linkage는 optional validated reference다.
- expired/revoked new revoke는 closed conflict, exact replay만 최초 result다.
- sanction original, identity restriction projection, required account-restriction notification과 audit를 same RDB transaction에 확정한다.
- account suspension의 session/CSRF/STOMP invalidation은 commit 뒤 수행하고 모든 inbound request/frame은 DB-confirmed restriction을 재검증한다.

### admin forbidden-word dictionary

- `GET /api/v1/admin/forbidden-words?cursor=&q=`, `POST /api/v1/admin/forbidden-words`, `PATCH /api/v1/admin/forbidden-words/{forbiddenWordId}`, `DELETE /api/v1/admin/forbidden-words/{forbiddenWordId}`를 사용한다.
- view는 `forbiddenWordId`, `revision`, `value`, `createdAt`, `updatedAt`이다.
- value는 trim 후 1~50 Unicode code point, whitespace-only/line break를 거부하고 case-insensitive exact duplicate를 금지한다.
- advanced Unicode normalization/confusable/chosung detection은 MVP에 없다.
- every mutation은 trim 1~200 Unicode code point mandatory plain-text `changeReason`, revision과 persistent Idempotency-Key를 사용한다.
- PATCH는 actual value change가 필수이고 reason-only update는 없다.
- dictionary mutation과 chat/community snapshot acquisition을 하나의 logical order로 선형화한다.
- commit 뒤 new content부터 적용하고 existing chat/post를 remask하지 않는다.
- before/after/reason/admin/time은 audit에 저장하되 general observability에는 value/reason raw를 남기지 않는다.

### admin card list read-only

- `GET /api/v1/admin/cards?cursor=&q=&cardType=`는 current active cards만 반환한다.
- 최대 20개, `(cardId ASC,cardVersion ASC)` deterministic keyset ordering과 admin/filter-bound opaque cursor를 사용한다.
- query는 card name simple search, cardType은 existing closed card type filter다.
- item은 `contract-fixture`의 canonical active `CardDefinitionView`를 직접 `$ref`하며 재선언하지 않는다.
- required field는 `cardId,cardVersion,definitionFingerprint,viewFingerprint,name,type,packId,image,timing,manaCost,summary,useGuide,selectionKind`다. `version,description,cardType,publicEffectRepresentation` alias와 관리자 전용 추가 field를 금지한다.
- cardcollection이 active catalog query를 소유하고 trustsafety admin adapter/application이 ADMIN/account state를 검증해 public port를 호출한다.
- admin card read audit commit 성공 뒤에만 response를 반환한다. FE는 prefetch/focus/refetch와 automatic retry를 끄고 explicit search/page action만 수행한다.
- card create/update/delete, effect/probability/pack price edit와 historical version activation endpoint는 없다.

### admin announcement create

- `POST /api/v1/admin/announcements`는 session, CSRF, ADMIN/account-state와 persistent Idempotency-Key를 요구한다.
- request는 `{title,body,importance}`다. title은 1~100 Unicode code point, whitespace-only/line break 거부, body는 1~1,000 code point, whitespace-only 거부/line break 허용 plain text다.
- importance는 `NORMAL | IMPORTANT`다.
- NORMAL은 optional in-app notification enabled recipient에게만 inbox row를 만들고 IMPORTANT는 setting과 관계없이 required inbox row를 만든다.
- eligible population은 사용자 승인에 따라 transaction snapshot 시점의 모든 non-WITHDRAWN account다. UNVERIFIED, ACCOUNT_SUSPENDED와 관리자 계정도 포함하며 현재 access restriction은 inbox 열람에서 그대로 적용한다.
- announcement original, admin audit와 recipient inbox rows를 same RDB transaction에 확정한다.
- success는 `201`과 announcementId, importance, createdAt, eligible/delivered/skipped counts의 admin-safe result이며 recipient identity를 포함하지 않는다.
- same key/same command는 original result replay, different command는 COMMAND_CONFLICT이며 duplicate inbox row를 만들지 않는다.
- update, recall/delete, scheduled publication과 async queue/fan-out은 MVP에 없다.

### 접근 행렬

| 상태 | block | profile report | chat report | post report | own report detail | admin |
|---|---:|---:|---:|---:|---:|---:|
| ACTIVE | 허용 | 허용 | 허용 | 허용 | 허용 | ADMIN role이면 허용 |
| ACTIVE + communication suspension | 허용 | 허용 | `403 COMMUNICATION_SUSPENDED` | `403 COMMUNICATION_SUSPENDED` | 허용 | ADMIN role이면 허용 |
| UNVERIFIED | `403 EMAIL_UNVERIFIED` | 동일 | 동일 | 동일 | 동일 | 거부 |
| ACCOUNT_SUSPENDED | `403 ACCOUNT_SUSPENDED` | 동일 | 동일 | 동일 | 동일 | 동일 |
| anonymous/WITHDRAWN | `401 UNAUTHENTICATED` | 동일 | 동일 | 동일 | 동일 | 동일 |

- non-ADMIN admin request는 resource lookup 전 `403 FORBIDDEN`이다.
- communication suspension은 admin moderation 자체를 막지 않지만 account suspension은 ADMIN role보다 우선한다.
- communication suspension 뒤 past chat/post report exact replay도 거부한다. block/profile report exact replay는 current matrix를 통과하면 허용한다.
- account suspension은 every user/admin receipt lookup 전에 거부한다.

### 핵심 transaction과 privacy

- post report + evidence + membership/count + 5th valid `AUTO_HIDDEN`
- case resolution + one new/linked action + member reports + notifications
- standalone moderation + post transition + audit
- sanction create/extend/revoke + identity projection + required notification + audit
- forbidden-word mutation + dictionary revision + audit
- raw evidence access audit commit-before-response
- admin card query audit commit-before-response
- admin announcement original + audit + optional/required inbox fan-out
- trustsafety는 block/report/evidence/case/sanction/dictionary/audit original을 소유한다. identity/community/matchchat/matchmaking/cardcollection과 public application port로만 협력하고 repository/entity 직접 접근을 금지한다.
- reporter/block relation, raw evidence, admin identity/memo, target sanction detail, internal account ID와 forbidden-word before/after는 허용되지 않은 response/error/log/observability에 포함하지 않는다.

### PRD 충돌 기록

- `trust-safety-admin/prd.md` 시나리오 1의 오기는 2026-07-14 `$create-prd trust-safety-admin`으로 상위 fixed spec에 맞게 “매칭 후보 탐색과 매칭 확정 검사에서 제외하며”로 정정되었다.
- 계약과 current PRD 모두 차단 상대를 candidate search와 match final check에서 제외한다.

## 오류 포맷과 사용자 표시 영향

- public/admin layouts와 query cache를 분리하고 role/account loss, logout/session rotation 때 sensitive cache를 제거한다.
- generated closed unions와 TanStack Query를 사용하되 raw/detail/card audited query의 auto retry/prefetch/focus refetch를 끈다.
- subjectRef capability로 action을 표시하고 server access matrix를 최종 권위로 처리한다.
- conflict에서 draft를 유지하고 refetch하며 auto merge/retry하지 않는다.

## 구현 메모

- trustsafety application service가 evidence/case/moderation/sanction/dictionary/audit transaction을 소유하고 public port로 other module state를 함께 확정한다.
- DB unique constraints/locking, persistent idempotency, revision과 audit-before-response를 구현한다.
- current fixed architecture로 충분하며 architecture decision 재개가 필요 없다.

## 테스트/fixture/드리프트 검증

- schema: block/report target/reason/status/case/evidence/resolution action/duration/sanction/dictionary/card view closed unions
- access: full account/restriction/role matrix and receipt lookup ordering
- block: self/expired ref, duplicate relation, stale remove, chat/match linearization/privacy
- report/case: post lifetime duplicate, chat/profile open duplicate와 resolved-new case, canonical subject target, self/non-visible, resolve/report race, exact one linked action
- evidence: audit-before-raw, no auto retry, AVAILABLE→EXPIRED time boundary, 30-day deletion and no restoration path
- moderation/sanction: revision/state conflicts, exact replay, same transaction projection/notification/audit, commit-after session close
- dictionary: 50/200 boundaries, case duplicate, actual PATCH, snapshot ordering/non-retroactivity
- admin card: active-only 20 page, filter/search, audit-before-response, no mutation endpoints
- privacy-negative: internal IDs, reporter/block/count, raw/admin/action detail and subjectRef public leakage
- drift gate: OpenAPI, generated client, MSW/runtime schema and fixture fingerprint mismatch를 차단한다.

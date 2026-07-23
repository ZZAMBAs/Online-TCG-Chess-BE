# Community Rest BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### 공통 경계와 endpoint

- 로그인 사용자용 community REST는 다음 다섯 endpoint를 사용한다.
  - `GET /api/v1/community/posts?cursor={opaque}&q={optional}`
  - `GET /api/v1/community/posts/{postId}`
  - `POST /api/v1/community/posts`
  - `PATCH /api/v1/community/posts/{postId}`
  - `DELETE /api/v1/community/posts/{postId}`
- JSON 응답 최상위는 `schemaVersion: "1"`, 모든 객체는 `additionalProperties: false`인 닫힌 schema다. body 없는 DELETE `204`만 예외다.
- 모든 일반 사용자 community 응답은 `Cache-Control: no-store`다.
- category, comment, like, image, public profile, client 지정 limit/sort/search target과 external full-text search는 MVP endpoint/schema/fixture에 없다.
- 신고 endpoint와 관리자 moderation REST는 trust-safety-admin topic이 소유한다.

### CommunityPostView

- trust-safety 후속 capability를 병합한 canonical view의 `capabilities`는 `{canEdit,canDelete,canReportPost}`, `authorActions`는 required nullable `null | {subjectRef,canBlock,canReportProfile}`다.
- list/detail/create/PATCH가 동일한 merged view를 사용한다. `canReport` alias, raw author ID, report count, block/moderation state는 금지한다.

- list와 detail은 같은 authoritative projection을 사용한다.
- 필드는 `postId`, nonnegative safe-integer `revision`, 전체 masked `title`, 전체 masked `body`, `author`, `capabilities`, required nullable `authorActions`, `createdAt`, nullable `contentUpdatedAt`이다.
- `author`는 `{type:"ACTIVE",nickname}` 또는 `{type:"WITHDRAWN"}` 닫힌 공용체다. internal account ID와 withdrawn 이전 nickname은 반환하지 않는다.
- `capabilities`는 server-computed `{canEdit,canDelete,canReportPost}`다. communication suspension이면 owner mutation과 post 신고 capability가 false다. mutation 때 권한과 상태를 다시 검증한다.
- `authorActions`는 self/withdrawn 또는 허용 action이 없으면 null이고, 타 ACTIVE author에 대해 허용된 block/profile-report action만 scope한 `{subjectRef,canBlock,canReportProfile}`을 제공한다.
- response 문자열은 HTML이 아닌 plain text다. server가 HTML entity encoding하지 않고 FE가 text node로 렌더링하며 `dangerouslySetInnerHTML`을 사용하지 않는다.

### 길이와 FE 표시

- title은 1~100 Unicode code point이며 whitespace-only와 line break를 거부한다.
- body는 1~1,000 Unicode code point이며 whitespace-only를 거부하고 line break를 허용한다.
- search `q`는 trim 후 1~100 Unicode code point이며 빈 결과를 거부한다.
- FE가 같은 규칙으로 선검증하지만 server가 최종 권위다.
- API와 query cache에는 전체 masked title/body를 유지한다.
- FE 목록에서 title은 1줄, body는 3줄을 넘으면 presentation-only ellipsis를 적용한다. detail은 화면 폭에 맞춰 줄바꿈하고 전체 내용을 표시한다.
- server는 preview, line count, CSS width와 truncated string을 생성하지 않는다.

### list와 search

- 한 page는 최대 20개이고 `(createdAt DESC,postId DESC)` keyset ordering을 사용한다.
- cursor가 없으면 첫 page, nullable `nextCursor`는 다음 과거 page를 가리킨다.
- cursor는 viewer principal, trim된 search condition과 ordering에 결합된 opaque token이다. 변조·타 사용자·다른 q 재사용은 `400 VALIDATION_FAILED`다.
- `q`가 없으면 active 목록, 있으면 active post의 masked title/body와 현재 author display를 대상으로 대소문자 구분 없는 단순 부분 문자열 검색을 수행한다.
- ACTIVE author는 current nickname, WITHDRAWN author는 고정 표시 의미인 “탈퇴 사용자”만 검색 대상이며 과거 nickname은 검색하지 않는다.
- SQL wildcard `%`, `_`와 escape 문자는 literal 처리하고 parameter binding을 강제한다.
- 페이지 간 전체 시점 snapshot은 보장하지 않지만 같은 keyset traversal에 중복 item을 만들지 않는다. 동시 hide/delete로 page가 20개보다 짧을 수 있다.

### detail과 concealment

- 일반 list/search/detail은 `ACTIVE` post만 반환한다.
- unknown, `DELETED`, `AUTO_HIDDEN`, `MANUAL_HIDDEN` direct access는 동일 HTTP `404`, `RESOURCE_NOT_FOUND`와 안전한 동일 message shape를 사용한다.
- non-owner update/delete도 같은 404 shape를 사용하고 ownership, state, report count와 current revision을 노출하지 않는다.
- 작성자 moderation 안내가 필요하면 community resource error가 아니라 별도 필수 notification으로 제공한다.

### create

- `POST /api/v1/community/posts` body는 닫힌 `{title,body}`다.
- session, CSRF와 persistent `Idempotency-Key`가 필수다.
- 성공은 `201`과 `CommunityPostView`다.
- raw title/body, 당시 forbidden-word snapshot으로 만든 masked title/body와 internal masking-policy revision을 한 transaction에 저장한다.
- 같은 principal/operation key와 같은 canonical command는 restart/deploy 뒤에도 최초 terminal status/body를 replay하며 post 생성, masking과 rate-limit 계산을 반복하지 않는다.
- 같은 key의 다른 command는 `409 COMMAND_CONFLICT`다.

### PATCH update

- `PATCH /api/v1/community/posts/{postId}`는 session, CSRF와 persistent `Idempotency-Key`가 필수다.
- request는 `{expectedRevision,title?,body?}`의 닫힌 객체이고 title/body 중 최소 하나가 존재해야 하며 present field는 non-null이다.
- unknown field, null과 empty patch는 `400 VALIDATION_FAILED`다.
- field presence가 변경 의도다. omitted field의 raw, masked와 masking-policy revision은 그대로 보존한다.
- present field만 입력 규칙을 검증하고 current forbidden-word snapshot으로 새 masked value와 policy revision을 만든다.
- FE는 edit form에서 dirty field만 전송하며 초기 masked 값을 모든 field에 자동 재전송하지 않는다. dirty field가 없으면 API를 호출하지 않는다.
- owner의 current `ACTIVE` post에서 expectedRevision이 stale이면 value와 무관하게 상태를 바꾸지 않고 `409 POST_REVISION_MISMATCH`와 `currentRevision,resyncRequired:true`를 반환한다.
- stale-same 성공과 masked-equality heuristic은 사용하지 않는다.
- revision이 current이고 모든 present raw가 저장 raw와 실제로 같으면 revision·contentUpdatedAt·masking을 바꾸지 않는 no-op `200`과 current view를 반환한다.
- 하나라도 실제 raw change면 present field만 교체하고 aggregate revision을 한 번 증가시켜 `200` latest view를 반환한다.
- raw equality는 server 내부 판단에만 사용하고 raw/current raw를 response, error와 log에 노출하지 않는다.

### DELETE

- `DELETE /api/v1/community/posts/{postId}`는 session, CSRF, persistent `Idempotency-Key`와 닫힌 body `{expectedRevision}`을 요구한다.
- owner의 current `ACTIVE` post만 `DELETED`로 soft-delete하고 revision을 증가시키며 raw/masked content는 보존한다.
- 성공과 exact replay는 body 없는 `204 No Content`다.
- 새 key로 hidden/deleted/non-owner를 요청하면 동일 404, owned active stale revision만 `409 POST_REVISION_MISMATCH`다.

### idempotency와 권한 검사 순서

- idempotency command fingerprint에는 principal, operation, target, expected revision, field presence와 present raw values가 포함된다.
- 같은 key와 같은 canonical command만 최초 terminal result를 replay하며 field presence/value/revision이 다르면 `409 COMMAND_CONFLICT`다.
- session/account/communication restriction 검증 뒤 exact idempotency receipt를 current resource concealment와 revision 검사보다 먼저 조회한다.
- 따라서 여전히 권한이 유효한 exact PATCH/DELETE replay는 이후 post가 hidden/deleted되어도 과거 command receipt를 반환할 수 있다. 이는 current resource view가 아니다.
- FE는 replay body를 latest list/detail authority로 병합하지 않고 mutation 종료 뒤 관련 query를 refetch한다.
- stale conflict 뒤 수정된 request는 새 idempotency key를 사용하고 mutation을 자동 retry하지 않는다.
- raw key와 raw post content는 log에 기록하지 않는다.

### masking·moderation·ordering

- forbidden-word dictionary 변경은 existing post에 소급하지 않는다. create와 present PATCH field만 해당 시점 snapshot으로 masking한다.
- content change, delete, auto/manual hide와 restore는 같은 post aggregate revision을 전진시킨다.
- `trustsafety`가 report original, per-user deduplication, valid report count와 admin audit을 소유한다.
- 5번째 valid report transaction에서 community 공개 port를 호출해 `AUTO_HIDDEN`을 한 번만 확정한다.
- admin hide/restore도 trustsafety application transaction이 audit original과 community 공개 state-transition port를 함께 호출한다.
- restore는 original `createdAt`과 raw/masked content를 유지하고 원래 keyset 위치로 복귀한다. 새 post처럼 상단으로 올리거나 remask하지 않는다.
- community와 trustsafety는 상대 repository/entity를 직접 참조하지 않는다.

### access와 privacy

- `ACTIVE`: 조회와 own active post mutation 허용.
- `UNVERIFIED`: 모든 community endpoint `403 EMAIL_UNVERIFIED`.
- account suspension: 조회 포함 `403 ACCOUNT_SUSPENDED`.
- communication suspension: 조회 허용, create/PATCH/DELETE/report는 `403 COMMUNICATION_SUSPENDED`.
- withdrawn/anonymous: `401 UNAUTHENTICATED`.
- raw title/body, internal author ID, withdrawn nickname, moderation state/reason, report count/threshold, reporter/admin identity와 forbidden-word metadata는 일반 response/error/log/observability에 포함하지 않는다.
- 일반 오류는 fixed common-error envelope와 status/code mapping을 사용한다.

## 오류 포맷과 사용자 표시 영향

- generated REST client와 TanStack Query가 full masked `CommunityPostView`를 소유한다.
- list presentation만 line clamp하고 detail과 cache의 authoritative values를 변형하지 않는다.
- PATCH adapter는 dirty field를 at-least-one 타입으로 제한하고 conflict에서 local draft를 유지한 채 refetch하며 자동 merge/retry하지 않는다.
- session rotation/logout 때 community query cache를 제거하고 raw form input/search text를 analytics·trace·persistent storage에 기록하지 않는다.

## 구현 메모

- community module은 post raw/masked aggregate, revision, search, idempotency와 user REST adapter를 소유한다.
- trustsafety 공개 port로 dictionary snapshot을 받고 moderation은 trustsafety transaction이 community 공개 port를 호출한다.
- 현재 fixed single RDB/JPA/Flyway/application transaction/module boundary로 구현하며 architecture decision 재개가 필요 없다.

## 테스트/fixture/드리프트 검증

- schema: five endpoints, closed view/author/capability/create/PATCH/delete body와 DELETE 204 exception
- input: Unicode code-point boundaries, whitespace/newline, null/unknown/empty PATCH, HTML plain-text rendering
- list/search: 20×1000 maximum payload, multibyte text, keyset tie, cursor misuse, wildcard literal, no category/comment/like/image
- PATCH: title/body/both dirty, omitted raw preservation, fresh raw-same no-op, stale-same 409, stale-different 409, present-field remasking
- idempotency: restart replay, create/PATCH/delete no duplicate state/rate count, field-presence conflict, receipt-before-concealment after auth
- moderation race: PATCH/delete vs 5th report/admin hide, single auto-hide, restore original position/revision
- privacy/concealment: four unavailable causes and non-owner status/code/message/timing parity, raw/identity/moderation/dictionary absence
- drift gate: OpenAPI, generated client, MSW/runtime schema와 fixture fingerprint mismatch를 차단한다.

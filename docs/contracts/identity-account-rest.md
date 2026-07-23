# Identity Account Rest BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

### 공통 경계

- 이 topic은 자신의 최소 profile, access status, settings와 notification inbox만 소유한다.
- 가입·로그인·session·탈퇴·재활성화는 fixed `auth-rest-oauth`, CSRF·cookie는 fixed `auth-cookie-csrf`를 재사용한다.
- 마이페이지 전적·최근 경기, collection과 deck은 각 fixed endpoint를 FE가 독립 query로 조합한다. 여러 모듈 저장소를 직접 조합하는 대형 `/me` aggregate endpoint를 만들지 않는다.
- 모든 응답 최상위에는 `schemaVersion: "1"`을 두고 모든 객체는 닫힌 schema와 `additionalProperties: false`를 사용한다.
- 모든 `/api/v1/me/**` 응답은 `Cache-Control: no-store`이고 임의 `userId`를 받지 않으며 현재 인증 principal에만 결합된다.

### 최소 profile

- `GET /api/v1/me/profile`
- 응답은 `nickname`과 `signInMethod`만 포함한다.
- `signInMethod`는 `{type:"LOCAL"}` 또는 `{type:"OAUTH",provider:"GOOGLE"|"KAKAO"}` 닫힌 판별 공용체다.
- email, userId, roles, account status, MMR, 약관 동의 정보와 OAuth provider subject는 포함하지 않는다.
- 닉네임은 읽기 전용이며 공개 사용자 profile endpoint와 nickname 변경 endpoint는 MVP에 없다.

### access status

- `GET /api/v1/me/access-status`
- 응답은 `accountStatus`, `requiredActions[]`, `activeRestrictions[]`를 포함한다.
- `accountStatus`는 `ACTIVE | UNVERIFIED | SUSPENDED`다. `WITHDRAWN`은 session을 만들 수 없어 응답 대상이 아니다.
- `requiredActions`는 `VERIFY_EMAIL | COMPLETE_OAUTH_ONBOARDING | ACCEPT_TERMS | ACCEPT_PRIVACY_POLICY`의 중복 없는 닫힌 배열이다.
- restriction은 `type: ACCOUNT_SUSPENSION | COMMUNICATION_SUSPENSION`, `startsAt`, nullable `endsAt`, 사용자 공개용 plain-text `reason`을 가진 닫힌 객체다.
- `/auth/session.activeRestrictions`는 route guard용 종류 집합이고 이 endpoint는 제한 화면의 required action·사유·기간을 소유한다.
- 관리자·신고자·출처 신고·증거·내부 restriction ID와 관리자 메모는 포함하지 않는다.

### settings

- `GET /api/v1/me/settings`는 `revision`, `matchChatVisible`, `optionalInAppNotificationsEnabled`, `serviceEmailNotificationsEnabled` 전체 projection을 반환한다.
- `PUT /api/v1/me/settings`는 같은 세 boolean과 현재 `revision`을 받는 닫힌 전체 교체 request다. session과 CSRF가 필수다.
- 성공 `200`은 증가했거나 현재인 revision을 포함한 전체 최신 projection을 반환한다.
- request revision이 stale이지만 세 설정 값이 현재 값과 모두 같으면 상태를 바꾸지 않고 현재 projection을 `200`으로 반환한다.
- revision이 stale이고 값이 다르면 상태를 바꾸지 않고 `409 SETTINGS_CHANGED`와 `currentRevision`을 반환한다. FE는 settings를 재조회하며 사용자 의도를 자동 재전송하지 않는다.
- 별도 `Idempotency-Key`와 mutation 자동 retry는 사용하지 않는다.
- `matchChatVisible`은 FE 표시 선호이며 채팅 전송·저장·신고 증거·차단 정책을 변경하지 않는다.
- service email 설정은 인증, password reset과 reactivation 같은 필수 보안 mail을 차단하지 않는다.
- 알 수 없는 field와 userId, email, nickname, role, accountStatus, MMR 같은 민감 field가 있으면 `400 VALIDATION_FAILED`로 요청 전체를 거부하고 일부 설정도 반영하지 않는다.

### notification inbox 조회

- `GET /api/v1/me/notifications?cursor={opaque}`를 사용한다. cursor만 선택적이고 client 지정 limit·sort·filter는 없다.
- `(createdAt DESC, notificationId DESC)` keyset ordering과 사용자 결합 opaque cursor를 사용하며 한 응답은 최대 20개다.
- 응답은 `items[]`와 nullable `nextCursor`를 포함한다.
- 각 item은 `notificationId`, `notificationType`, `createdAt`, 종류별 닫힌 `content`를 가진다.
- `REPORT_RESOLVED` content는 자신의 opaque `reportId`와 `result: ACTION_TAKEN | NO_ACTION`만 포함하고 대상자 제재 상세는 포함하지 않는다.
- `ADMIN_ANNOUNCEMENT` content는 opaque `announcementId`, `importance: NORMAL | IMPORTANT`, plain-text `title`, plain-text `body`를 포함한다. HTML로 해석하지 않는다.
- `ACCOUNT_RESTRICTION` content는 `restrictionType`, `startsAt`, nullable `endsAt`, 사용자 공개용 plain-text `reason`을 포함한다.
- 신고자, 처리 관리자, 대상 사용자의 identity·제재 상세, 증거·원문·내부 메모, email, provider subject와 MMR은 포함하지 않는다.
- 잘못되거나 다른 사용자에게 결합된 cursor는 `400 VALIDATION_FAILED`이며 FE는 기존 목록에 임의 병합하지 않고 첫 페이지부터 다시 조회한다.

### notification 선택·필수와 보관

- `optionalInAppNotificationsEnabled=false`로 바뀌어도 이미 생성된 inbox 항목은 유지하며 client-side에서 숨기지 않는다.
- 설정 비활성화 이후 신고 처리 결과와 관리자 공지 원본은 해당 소유 모듈에 계속 보존한다.
- 비활성화 이후 `REPORT_RESOLVED`와 `importance: NORMAL`인 `ADMIN_ANNOUNCEMENT`는 해당 사용자의 새 inbox 항목을 생성하지 않는다.
- `ACCOUNT_RESTRICTION`과 `importance: IMPORTANT`인 `ADMIN_ANNOUNCEMENT`는 필수 알림으로 설정과 무관하게 inbox 항목을 생성한다.
- MVP inbox는 읽기 전용 시간순 목록이다. 읽음 상태, unread count·badge, mark-read, 사용자 삭제와 자동 만료를 제공하지 않고 생성된 항목을 계속 보관한다.
- 보관 기간이나 삭제가 필요해지면 PRD에서 기간·조건·필수 알림 예외를 먼저 확정한 뒤 계약을 확장한다.

### admin announcement producer 연결

- `ADMIN_ANNOUNCEMENT` original은 trust-safety-admin의 `POST /api/v1/admin/announcements`가 생성한다.
- NORMAL은 optional setting enabled account에만, IMPORTANT는 setting과 관계없이 recipient inbox row를 생성한다.
- eligible population은 transaction snapshot 시점의 모든 non-WITHDRAWN account다. UNVERIFIED, ACCOUNT_SUSPENDED와 관리자도 포함하며 현재 access restriction을 우회해 inbox를 열람시키지는 않는다.
- identity는 trustsafety 공개 application port 호출로 user setting을 적용하고 inbox deduplication을 보장한다.
- update, recall/delete와 schedule은 MVP에 없다.

### 접근 matrix와 오류

- `ACTIVE`: profile, access-status, settings GET/PUT와 notifications 허용.
- `UNVERIFIED`: access-status와 fixed auth 허용 route만 허용. 그 외 identity endpoint는 `403 EMAIL_UNVERIFIED`.
- `SUSPENDED`: access-status와 fixed auth 허용 route만 허용. 그 외 identity endpoint는 `403 ACCOUNT_SUSPENDED`.
- communication suspension만 활성인 `ACTIVE`: 모든 identity endpoint를 허용한다.
- `WITHDRAWN`: session을 만들 수 없으므로 보호 endpoint는 `401 UNAUTHENTICATED`로 수렴한다.
- 공통 오류 envelope와 `401`, `403`, `400 VALIDATION_FAILED`, `409 SETTINGS_CHANGED`, `429 RATE_LIMITED`, `500 INTERNAL_ERROR` 의미는 fixed common-error 계약을 따른다.

### transaction과 모듈 경계

- 신고 처리·제재·관리자 공지 업무 원본은 `trustsafety`가 소유한다.
- account 상태, settings, 사용자 공개용 access-status projection과 notification inbox는 `identity`가 소유한다.
- trustsafety application service가 transaction을 열고 identity 공개 application port를 호출한다. 상대 모듈 repository를 직접 접근하지 않는다.
- 필수 알림과 account restriction projection은 원본 확정과 같은 RDB transaction에 참여한다. identity가 trustsafety 원본을 역조회하지 않는다.
- inbox 중복 방지 key는 `recipientAccountId + sourceType + sourceId + notificationType`이며 client가 아니라 신뢰된 producer만 source identity를 전달한다.
- 현재 단일 RDB transaction으로 구현하며 비동기 queue/outbox는 도입하지 않는다. 다중 인스턴스 또는 대규모 공지 fan-out이 필요할 때 architecture decision으로 재검토한다.

## 오류 포맷과 사용자 표시 영향

- 마이페이지는 profile, access-status, settings, notifications, match-history와 card/deck query를 독립적으로 조합한다.
- settings conflict는 refetch 후 사용자 안내로 처리하고 mutation을 자동 재전송하지 않는다.
- session rotation, logout과 withdrawal 때 모든 `/me/**` TanStack Query cache를 제거한다.
- notification item은 generated discriminated union으로만 렌더링하고 plain text를 HTML로 해석하지 않는다.

## 구현 메모

- identity module은 principal 전용 profile/access/settings/notification adapter와 공개 notification/restriction application port를 제공한다.
- revision 비교, same-value replay, source deduplication과 optional/required inbox 생성을 transaction 안에서 강제한다.
- 사용자 공개용 projection과 업무 원본 저장소의 모듈 경계를 유지한다.

## 테스트/fixture/드리프트 검증

- OpenAPI: endpoint별 닫힌 request/response, profile sign-in method, access required action/restriction, settings와 notification content 공용체
- access: `ACTIVE|UNVERIFIED|SUSPENDED|WITHDRAWN`와 communication suspension matrix
- settings: 정상 교체, stale-same `200`, stale-different `409`, unknown/sensitive property 원자 거부, CSRF와 no auto-retry
- notification: 20개/빈/마지막 페이지, 동시각 tie, cursor 변조·타 사용자 재사용, plain text, 닫힌 content
- policy: optional-disabled 원본 유지·inbox 미생성, required inbox 생성, 기존 inbox 유지, duplicate producer event 단일 row
- privacy-negative: 신고자·관리자·증거·대상자 상세 제재·email·provider subject·MMR와 자유 payload 부재
- drift gate: OpenAPI, generated client, MSW와 fixture fingerprint 불일치를 차단한다.

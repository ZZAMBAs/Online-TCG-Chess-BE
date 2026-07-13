---
name: negotiate-fe-be-contract
description: Online-TCG-Chess-BE를 중심으로 FE/BE 전체 계약 협상을 완료해야 할 때 사용한다. canonical GitHub FE/BE 저장소와 요구사항·아키텍처를 확인해 REST API, STOMP/WebSocket, 인증/CSRF/cookie, 오류 코드, 상태 동기화, projection, contract test 주제를 도출하고, 주제별 FE/BE 서브에이전트 검토와 최종 전체 커버리지 검증을 거쳐 모든 계약을 fixed로 만든 뒤 docs/negotiation session을 completed로 닫아야 할 때 사용한다.
---

# Negotiate FE/BE Contract

## 개요

BE 저장소를 요구사항과 계약 협상의 중심으로 삼아 FE/BE 계약을 한 주제씩 중재하되, 기본 실행은 전체 통신·프로토콜·공유 계약 후보가 모두 끝날 때까지 계속한다. 메인 에이전트는 중재자와 기록자이며, FE와 BE 서브에이전트는 주제별 검토자와 최종 커버리지 검토자로만 사용한다.

## 기본 원칙

- 모든 질문, 분석, 기록은 한국어로 작성한다.
- `docs/spec/spec-fixed.md`를 요구사항 source of truth로 둔다.
- FE 저장소 기준은 `https://github.com/ZZAMBAs/Online-TCG-Chess-FE`로 둔다.
- BE 저장소 기준은 `https://github.com/ZZAMBAs/Online-TCG-Chess-BE`로 둔다.
- 로컬 체크아웃은 읽기 최적화용 실행 위치일 뿐 저장소 식별자나 산출물 참조가 아니다.
- 협상 문서에는 로컬 절대 경로, sibling 상대 경로, 임시 clone 경로를 기록하지 않는다. FE/BE 자료는 canonical GitHub URL과 repo-relative path, 확인한 commit으로 참조한다.
- FE repo에는 BE 요구사항 원문이나 권위 계약 전문을 복사하지 않는다.
- 메인 에이전트는 BE 구현 편의가 아니라 요구사항, FE/BE의 확정 아키텍처, FE 구현 가능성, 보안, 테스트 가능성, 사용자 승인 상태를 기준으로 중재한다.
- FE 아키텍처는 BE 아키텍처와 동등한 협상 입력이다. FE의 라우팅, 상태 관리, API/STOMP client 경계, 디자인 기준, 배포·보안 제약, 테스트·contract-drift 하네스와 충돌하는 계약을 임의로 확정하지 않는다.
- 사용자 판단이 필요한 계약은 사용자 승인 전 `fixed`로 표시하지 않는다.
- 제품 정책, 보안 수준, UX, 범위, 개인정보/비공개 정보 노출, 운영 정책, 게임 밸런스처럼 사용자 판단이 필요한 사항은 `needs_user_decision`으로 멈춘다.
- 요구사항과 기존 아키텍처에 이미 부합하고 FE/BE 검토에서 이견이 없는 단순 기술 계약은 메인 에이전트가 `fixed`로 확정할 수 있다.
- 협상 중 FE/BE 서브에이전트는 read-only 검토자로 사용한다. production code, spec, PRD/TRD, 계약 문서를 직접 수정하게 하지 않는다.
- 서브에이전트 호출이 불가능하거나 허용되지 않으면 메인 에이전트가 대체 검토하지 않고 협상을 중단한다.
- 메인 에이전트는 topic별 협상 과정과 결과만 기록한다. 서브에이전트에게 별도 repo 기록 작성을 지시하지 않는다.

## 입력 확인

먼저 존재하는 자료만 읽는다.

- BE 요구사항: `docs/spec/spec-fixed.md`
- BE 공통 계약/기술 문서: `docs/websocket-spec.md`, `docs/trd.md`, `docs/traceability.md`, `docs/features/*/trd.md`
- BE 아키텍처: `docs/architecture/current-fixed.md`를 먼저 읽고, 가리키는 `impl-fixed.md`, `infra-fixed.md`, `harness-fixed.md`와 관련 `docs/architecture/*`
- BE 이슈 산출물(존재하는 경우만): `docs/features/*/issues/*/issue.md`, `docs/issue-map.md`, `docs/adr-index.md`
- 기존 협상 기록: `docs/negotiation/session.md`, `docs/negotiation/*/summarize.md`, `docs/negotiation/*/[0-9]*.md`
- BE 구현/테스트 근거: `src/main`, `src/test`, `build.gradle`, `settings.gradle`
- FE 요구사항 동기화 지침: FE repo의 `AGENTS.md`, `.codex/skills/spec-read/SKILL.md`
- FE 아키텍처 지침: FE repo의 `.codex/skills/architecture-decision/SKILL.md`, `.codex/skills/architecture-interview/SKILL.md`, `.codex/skills/architecture-review/SKILL.md`
- FE 아키텍처: FE repo의 `docs/architecture/current-fixed.md`를 먼저 읽고, 가리키는 `impl-fixed.md`, `infra-fixed.md`, `harness-fixed.md`와 관련 `docs/architecture/*`
- FE 이슈 산출물(존재하는 경우만): FE repo의 `docs/features/*/issues/*/issue.md`, `docs/issue-map.md`, `docs/adr-index.md`
- FE 산출물/구현 근거: FE repo의 `docs`, `src`, `package.json`, lockfile, 설정·CI·테스트 관련 파일

FE 자료는 다음 순서로 읽는다.

1. 사용자/호출자가 제공한 checkout 또는 BE sibling checkout이 있으면 remote가 canonical FE URL과 일치하는지 확인하고 읽기 전용 입력으로 사용한다.
2. 유효한 로컬 checkout이 없으면 GitHub app/connector, `gh api`, 또는 canonical FE repo의 read-only 임시 shallow clone을 사용한다.
3. `git ls-remote` 또는 GitHub API로 canonical remote commit을 확인한다. 로컬 HEAD가 remote commit과 다르거나 필요한 자료가 미커밋 상태면 그 로컬 내용은 확정 근거로 사용하지 않고 canonical remote snapshot을 읽는다.
4. 어떤 방식이든 확인한 FE remote commit을 기록하고, 산출물에는 `https://github.com/ZZAMBAs/Online-TCG-Chess-FE/blob/{commit}/{repo-relative-path}` 형태를 사용한다.
5. 로컬 FE가 없다는 이유만으로 중단하지 않는다. canonical FE repo 원격 조회도 실패할 때만 stale 위험을 기록하고 협상을 중단하거나 `needs_user_decision`으로 둔다.

BE 자료도 산출물에서 필요하면 `https://github.com/ZZAMBAs/Online-TCG-Chess-BE/blob/{commit}/{repo-relative-path}`로 참조한다. commit을 아직 확인하지 못한 과정 기록은 canonical repo URL과 repo-relative path를 함께 적고, 로컬 경로는 적지 않는다.

FE 요구사항 판단이 필요하면 FE repo의 `$spec-read` 원칙을 존중한다. 원격 최신성 확인 실패 시 캐시 기준으로 추정하지 말고 협상을 중단하거나 `needs_user_decision`으로 기록한다.

### 아키텍처와 이슈 산출물의 준비 상태

- `current-fixed.md`가 있으면 반드시 먼저 읽고 포인터가 가리키는 fixed 문서의 상태와 제약을 협상 근거로 기록한다. 포인터나 대상 fixed 문서가 깨졌거나 `fixed` 상태가 아니면 해당 repo의 아키텍처를 확정된 사실처럼 취급하지 않는다.
- FE 또는 BE의 아키텍처가 없을 수 있다. 이 자체가 모든 협상의 실패 조건은 아니지만, 선택한 topic이 없는 아키텍처 결정을 전제하거나 그 결정을 새로 만들어야 하면 협상으로 대신 결정하지 않는다. 해당 repo의 `$architecture-decision` 실행이 필요하다고 `needs_user_decision` 또는 다음 행동에 남기고 중단한다.
- 두 repo의 fixed architecture와 충돌하는 계약 후보는 `fixed`로 만들지 않는다. 충돌은 각 repo의 architecture decision에서 해결한 뒤 협상을 재개한다.
- 이슈 산출물은 협상 선행 조건이 아니다. 협의는 PRD, 확정 아키텍처, 기존 계약/기술 문서와 현재 구현 근거만으로 시작할 수 있다.
- 존재하는 이슈는 이미 구현된 surface, 의존성, 테스트/fixture 및 과거 협상 결정을 확인하는 보조 근거다. 다른 기능의 이전 이슈가 있다는 사실만으로 현재 topic의 범위·정책·계약을 추정하거나 잠그지 않는다.
- 이슈가 없으면 입력과 과정 기록에 `이슈 산출물: 없음(초기 협상)`이라고 명시하고, 이후 `create-issues-adr`가 확정 계약을 입력으로 이슈를 만들도록 handoff만 남긴다. 협상 과정에서 이슈를 생성하거나 수용 기준을 임의로 확정하지 않는다.

## 협의 주제 도출

다음 범위를 우선 검토해 협의 후보를 만든다.

- REST API 명세, endpoint 후보, request/response envelope
- STOMP/WebSocket destination, event envelope, client command, server event
- 세션 쿠키, CSRF, Origin/CORS, OAuth/email callback 흐름
- 공통 오류 코드, REST/STOMP 오류 포맷, 사용자 표시 가능 메시지
- 계정 상태와 제재별 FE 접근 제어
- pending, rollback, `actionId`, `commandId`, `stateVersion`, 재동기화
- 재접속, 중복 탭, disconnect, timeout, forfeit 처리
- 빠른 매치 상태, 취소 가능 시점, 게임 화면 전환
- 공개/비공개 projection, 레전드 카드/RNG/MMR/차단 관계 노출 제한
- contract test, OpenAPI, JSON Schema, fixture, mock sync
- pagination, 검색, 정렬, 시간/날짜 표현, rate limit UX
- 프로모션, 항복, 드로우 실패, 서버 abort 같은 게임 특수 입력
- 채팅/커뮤니티 masking, HTML escape, 신고/차단/제재 화면 계약
- 전적/기보 replay, trace/request ID

협의 후보는 한 번에 하나의 topic만 선택해 진행한다. 선택한 topic은 `docs/negotiation/session.md`와 topic별 과정 기록에만 남긴다.

topic 디렉터리 이름은 소문자 ASCII kebab-case로 제한한다. 예: `auth-cookie-csrf`, `game-state-sync`, `matchmaking-cancel`.

### 전체 협상 캠페인

- 인자 없이 실행하면 위 후보 범위와 실제 spec/PRD/architecture/구현 표면에서 필요한 topic 전체를 동적으로 도출하고 하나씩 끝까지 협상한다.
- topic 하나가 `fixed`여도 전체 협상이 끝난 것이 아니다. 나머지 후보를 다시 도출해 다음 위험도 높은 topic으로 즉시 이어간다.
- 사용자가 특정 topic만 지정하면 그 topic만 처리할 수 있지만, 종료 상태는 `idle`이며 전체 동기화 가능 상태인 `completed`로 표시하지 않는다.
- 모든 후보가 `fixed`로 보이면 새 FE/BE 서브에이전트를 열어 요구사항, 양쪽 fixed architecture, 구현 표면과 전체 `summarize.md`를 독립적으로 대조하는 최종 커버리지 검토를 수행한다.
- 최종 FE/BE 검토에서 누락된 endpoint, destination, lifecycle, projection, 오류, fixture 또는 drift gate가 하나라도 나오면 새 topic을 열고 협상을 계속한다.
- 최종 검토에서 누락이 없고 모든 `summarize.md`가 `fixed`일 때만 `session.md`를 `completed`로 바꾼다.
- `$sync-be-contracts`와 FE측 동기화는 `session.md`가 `completed`가 된 뒤에만 수행한다. topic별 부분 sync를 다음 단계로 안내하지 않는다.

## 기록 구조

다음 구조만 사용한다.

```text
docs/negotiation/
  session.md
  {topic}/
    yyyymmdd-HHMMSS.md
    summarize.md
```

- `session.md`: 현재 또는 마지막 협상 재개 포인터다. 하나만 둔다.
- `{topic}/yyyymmdd-HHMMSS.md`: 협의 과정 스냅샷이다. append-only 성격으로 새 파일을 추가한다.
- `{topic}/summarize.md`: 해당 topic의 현재 최종 합의 요약이다. 후속 논의로 덮어쓸 수 있다.

`session.md`에는 다음 필드만 둔다.

```markdown
# Negotiation Session

status: idle | in_progress | needs_user_decision | completed
active_topic: {topic 또는 없음}
current_round: {숫자 또는 없음}
current_step: {현재 단계}
last_completed_artifact: {최신 과정 기록 경로 또는 없음}
next_action: {재개 시 수행할 다음 행동}
```

`started_at`, `updated_at`은 기록하지 않는다. 과정 시각은 timestamp 파일명과 git 이력으로 추적한다.

## 재개 규칙

- 새 작업을 시작하면 `docs/negotiation/session.md`를 가장 먼저 읽는다.
- `status`가 `in_progress` 또는 `needs_user_decision`이면 새 topic을 시작하지 말고 `active_topic`, `last_completed_artifact`, `next_action`을 따라 이어간다.
- `status`가 `idle`이고 전체 협상이 요청되면 기존 fixed topic을 제외하고 후보를 다시 도출해 `in_progress`로 전환한다.
- `status: completed`는 최종 FE/BE 커버리지 검토까지 통과한 전체 협상 완료 상태로만 사용한다.
- 서브에이전트 호출 전에 반드시 `session.md`에 호출 대상, 질문 요약, 기대 출력이 드러나도록 `next_action`을 기록한다.
- 서브에이전트 호출이 불가능하거나 허용되지 않으면 가능한 경우 `session.md`를 `needs_user_decision`으로 갱신하고 중단 사유를 `next_action`에 남긴다.
- 서브에이전트 응답을 받으면 즉시 `{topic}/yyyymmdd-HHMMSS.md`를 생성한다.
- 의미 있는 상태 변화가 있으면 `session.md`를 갱신한다.
- 서브에이전트 응답 뒤 기록 전에 종료된 경우, 재개 시 `next_action`을 다시 수행한다.
- `summarize.md`는 합의안 또는 사용자 결정 결과가 생겼을 때만 갱신한다.

## 협상 절차

1. `session.md`를 읽고 중단된 협상이 있으면 재개한다.
2. 기존 topic별 `summarize.md`를 읽어 이미 `fixed`된 주제를 제외한다.
3. 요구사항, 각 repo의 현재 fixed architecture와 구현 근거, 기존 이슈(있을 때만)를 읽어 협의 후보를 도출하거나 갱신한다. 이슈 부재는 후보 도출을 막지 않는다.
4. 사용자 또는 문맥이 특정 topic을 지정하지 않았으면 가장 위험도가 높은 topic 하나를 선택한다.
5. topic 성격에 따라 시작 순서를 정한다.
   - FE-first: UX, 상태 표시, API 소비, STOMP client, mock/fixture, route guard 영향이 큰 topic
   - BE-first: 도메인 불변식, 보안, 트랜잭션, 권한, persistence, rate limit 영향이 큰 topic
6. 서브에이전트 호출 전 `session.md`를 갱신한다.
7. 첫 번째 서브에이전트 의견을 받은 즉시 과정 기록을 남긴다.
8. 반대편 서브에이전트에 동일 topic과 상대 의견을 전달해 검토를 받는다.
9. 최대 2~3라운드만 왕복한다.
10. 계약안이 정리되면 사용자 판단이 필요한지 판단한다.
11. 사용자 판단이 필요 없고 FE/BE 검토에서 이견이 없으면 `summarize.md`에 `fixed`로 기록한다.
12. 사용자 판단이 필요하면 `summarize.md`에 `needs_user_decision`으로 기록하고 사용자 승인 또는 결정 질문을 1~3개로 줄인다.
13. 사용자 결정으로 기존 `fixed` 내용이 바뀌면 같은 `summarize.md`를 덮어쓸 수 있다. 이때 `미결정 또는 사용자 결정 이력`에 변경 근거를 요약한다.
14. topic이 끝나면 해당 서브에이전트 context를 닫고 전체 실행이면 남은 후보를 재도출해 다음 topic 포인터로 갱신한다.
15. 특정 topic만 요청된 실행이면 `session.md`를 `idle`로 바꾸고 전체 협상은 완료되지 않았음을 `next_action`에 남긴다.
16. 남은 후보가 없으면 새 FE/BE 서브에이전트로 최종 커버리지 검토를 수행한다.
17. 커버리지 누락이 있으면 새 topic으로 돌아가고, 누락이 없으며 모든 요약이 `fixed`이면 `session.md`를 `completed`로 전환한다.

## 서브에이전트 지시 원칙

각 topic마다 FE/BE 서브에이전트를 새로 연다. 이전 topic의 상세 context를 그대로 넘기지 말고 필요한 입력 문서, topic, 최신 과정 기록, 상대 의견만 전달한다.

FE 서브에이전트에는 다음 관점을 요청한다.

- FE 화면, route guard, server cache, client state, pending/rollback
- FE `current-fixed.md`와 active fixed 문서에 따른 라우팅, 상태, API/STOMP client, 모듈·컴포넌트, 배포·보안, 테스트·contract-drift 제약 및 충돌 여부
- REST/STOMP client 구현 난이도와 mock/fixture 필요
- 사용자에게 보이는 오류/권한/로딩/empty 상태
- 공개/비공개 projection과 노출 위험
- FE 테스트, MSW, Playwright, contract drift 관점

BE 서브에이전트에는 다음 관점을 요청한다.

- 요구사항, 도메인 불변식, 권한, 보안, 상태 불변성
- REST/STOMP handler, transaction, idempotency, concurrency
- persistence, audit/security log, rate limit, observability
- contract/API test, OpenAPI/JSON Schema/fixture 가능성
- 구현 순서와 기존 PRD/TRD/architecture 및 이슈 산출물(있을 때만)과의 충돌

각 서브에이전트 출력은 다음 형식을 요구한다.

```markdown
## 입장 요약
## 제안
## 수용 조건
## 반대 또는 위험
## 사용자 결정 필요
## 중재자 기록 후보
```

## 과정 기록 형식

`docs/negotiation/{topic}/yyyymmdd-HHMMSS.md`는 다음 구조를 사용한다.

```markdown
# {Topic} Negotiation Snapshot

## 상태

- round:
- step:
- status:
- previous_artifact:
- next_action:

## 입력

- 요구사항 근거:
- FE 아키텍처 근거:
- FE 구현/이슈 근거:
- BE 아키텍처 근거:
- BE 구현/이슈 근거:

## 진행 내용

## FE 의견

## BE 의견

## 중재 판단

## 사용자 결정 필요

## 다음 행동
```

## 최종 요약 형식

`docs/negotiation/{topic}/summarize.md`는 다음 구조를 사용한다.

```markdown
# {Topic} Contract Summary

## 상태

- status: proposed | in_review | needs_user_decision | fixed
- source_artifacts:
- supersedes:

## 결정

## FE 구현 영향

## BE 구현 영향

## 계약 테스트/검증

## 미결정 또는 사용자 결정 이력

## 참조 메모 반영 대상
```

상태 의미는 다음과 같다.

- `proposed`: 중재자가 계약 초안을 정리한 상태
- `in_review`: FE/BE 서브에이전트 검토가 진행 중인 상태
- `needs_user_decision`: 사용자 판단이나 사용자 승인이 필요해 확정을 멈춘 상태
- `fixed`: FE/BE 검토상 이견이 없고 사용자 판단이 필요 없거나, 사용자 결정이 반영되어 확정된 상태

`fixed`가 사용자 결정으로 확정된 경우 승인 근거를 `미결정 또는 사용자 결정 이력`에 요약한다. 사용자 판단이 필요 없는 단순 기술 계약을 `fixed`로 확정한 경우에는 그 판단 근거를 같은 섹션에 요약한다.

## Repo별 참조 메모

최종 결정 후 메인 에이전트가 각 repo에 참조 메모를 남길 수 있다.

- 권위 문서: `docs/negotiation/{topic}/summarize.md`
- 참조 메모 내용: summarize 경로, 관련 commit/hash, 적용 범위, 구현 영향, 필요한 테스트 또는 fixture
- 금지: 결정 전문 복사, BE 요구사항 원문 복사, 권위 문서와 다른 표현의 독립 계약 작성

FE repo 참조 메모 위치는 FE repo의 기존 문서 구조를 먼저 확인하고, 없으면 사용자 승인 뒤 최소 문서만 만든다. 참조 메모가 BE 권위 요약을 가리킬 때는 `https://github.com/ZZAMBAs/Online-TCG-Chess-BE/blob/{commit}/docs/negotiation/{topic}/summarize.md`를 사용하고 로컬 경로를 기록하지 않는다. 서브에이전트는 참조 메모를 직접 작성하지 않는다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 진행한 topic
- 생성 또는 갱신한 과정 기록
- 갱신한 `session.md`, `summarize.md`
- 현재 상태: `idle`, `in_progress`, `needs_user_decision`, `completed`
- 전체 협상에서 남은 topic 또는 최종 커버리지 검토 결과
- 사용자 결정이 필요한 질문
- 각 repo 참조 메모 반영 여부

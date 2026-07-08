---
name: security-review
description: TDD BLUE 이후 로컬 feature 이슈의 Java/Spring production 변경을 독립 보안 검증해야 할 때 사용한다. 인자로 auth-1, auth-001, auth-issues-1, xxx-yyy-1처럼 마지막 토큰이 숫자인 이슈 식별자를 받아 issue.md, TDD GREEN 결과, refactor-log.md, 관련 spec/PRD/TRD/architecture, git diff를 확인하고, 서브에이전트에게 보안 verifier 역할을 맡겨 Low/Medium/High finding을 분리한다. Medium 이상은 차단 사항으로 보고 메인 에이전트가 수정 후 재검증하며, 결과는 현재 이슈 디렉터리의 security-review.md에 최신 스냅샷으로 기록한다.
---

# Security Review

## 개요

TDD BLUE로 정리된 production 변경을 같은 세션의 낙관에 기대지 않고 독립 검증한다. 이 스킬은 보안 결함을 찾고, `Medium` 이상 finding을 수정 게이트로 삼고, 검토 결과를 이슈 디렉터리의 `security-review.md`에 남긴다.

## 입력 규칙

- 모든 질문, 분석, 보고는 한국어로 작성한다.
- 사용자는 이슈 식별자 하나를 인자로 제공해야 한다.
- 인자가 없거나 마지막 하이픈 뒤 토큰이 숫자가 아니면 형식 오류를 보고하고 즉시 종료한다.
- 허용 예시는 `auth-1`, `auth-001`, `auth-issues-1`, `xxx-yyy-1`이다.
- 끝에서 두 번째 토큰이 `issues`이면 구분자로만 보고 feature 이름에서 제외한다.
- `xxx-yyy-1`은 feature=`xxx-yyy`, issue number=`1`로 해석한다.
- 이슈 번호 입력은 0-padding 없이 받아들이되, 이슈 디렉터리 탐색은 번호의 정수값으로 비교한다.
- 이슈 디렉터리는 `docs/features/{feature}/issues/{feature}-{nnn}-{slug}/` 계열에서 정확히 하나만 찾아야 하며, 그 안의 `issue.md`를 이슈 문서로 본다.
- 이슈 탐색은 먼저 `scripts/find_issue.py`를 실행해 검증한다.

```bash
python3 .codex/skills/security-review/scripts/find_issue.py auth-1 --root .
```

## 읽을 문서

다음 순서로 존재하는 문서만 읽는다.

1. `scripts/find_issue.py`가 찾은 `issue.md`
2. 현재 이슈의 `depends_on`, 직전 번호 이슈, `## 의존 관계`에 적힌 선행 이슈 문서
3. 현재 이슈의 `## TDD RED 결과`와 `## TDD GREEN 결과`
4. 현재 이슈 디렉터리의 `refactor-log.md`
5. 이슈 frontmatter 또는 본문에 적힌 PRD/TRD/architecture/traceability/websocket 관련 문서
6. 보안 원천 요구사항 확인을 위한 `docs/spec/spec-fixed.md`
7. 현재 `src/main`, `src/test`, `build.gradle`, 설정 파일, WebSocket/CORS/Security/Actuator 관련 구현
8. 이번 이슈 변경 범위 확인을 위한 `git diff --name-only`, `git diff`, 필요 시 `git diff --cached`
9. 보안 체크리스트인 `references/security-checklist.md`
10. 도구 사용 정책인 `references/tooling-policy.md`
11. 로그 기록 계약인 `references/security-review-contract.md`

PRD/TRD, GREEN 결과, BLUE 결과, 변경 파일, 보안 요구사항을 확인할 수 없으면 추측하지 말고 `security-blocked`로 기록한다.

## 진입 게이트

- 현재 이슈에 `TDD GREEN 결과`가 없으면 검토하지 말고 `security-blocked`로 기록한다.
- GREEN 결과가 `green-pass`가 아니면 검토하지 말고 `security-blocked`로 기록한다.
- `refactor-log.md`가 없거나 BLUE 상태가 `blue-pass` 또는 `blue-noop`가 아니면 검토하지 말고 `security-blocked`로 기록한다.
- 대상 파일은 GREEN 결과의 production 파일, BLUE 변경 파일, 현재 `git diff` 중 이슈 관련 production/resource 파일로 제한한다.
- 대상 파일을 특정할 수 없으면 `security-blocked`로 기록한다.
- 선행 이슈가 있으면 해당 이슈의 AC 충족, 테스트 통과, BLUE 완료 또는 BLUE 불필요가 문서상 확인되는지 확인한다.

## 변경 허용 범위

기본 검토 단계에서는 서브에이전트가 파일을 수정하지 않는다. 메인 에이전트만 아래 범위에서 수정할 수 있다.

- 현재 이슈의 GREEN/BLUE 변경 범위 안의 `src/main/java/**/*.java`
- 현재 이슈의 GREEN/BLUE 변경 범위 안에서 보안 결함 수정에 꼭 필요한 `src/main/resources`
- 현재 이슈 디렉터리의 `security-review.md`
- 사용자가 승인한 경우의 보안 도구 설정 파일 또는 Gradle 설정

다음은 기본 보안 검토에서 금지한다.

- 새 기능 추가
- `src/test`를 보안 결함 은폐 목적으로 수정
- 이슈 범위를 벗어난 광범위 보안 리팩터링
- 사용자 승인 없는 새 보안 도구 의존성 또는 CI 설정 도입
- 아키텍처 문서에 없는 인증/인가 구조 재결정
- `Low` finding만 있는 상태에서 불필요한 production 수정

## 서브에이전트 위임 규칙

- 서브에이전트는 보안 verifier로만 사용한다.
- 서브에이전트에게는 원자료 경로, 이슈 식별자, 검토 범위, 금지 사항만 전달한다.
- 서브에이전트에게 메인 에이전트의 결론이나 기대 finding을 알려주지 않는다.
- 서브에이전트는 production 코드를 수정하지 않고 findings를 반환한다.
- findings는 `Low`, `Medium`, `High` 중 하나로 분류하고, 각 항목에 근거 파일과 보안 영향을 적는다.
- `Medium` 이상 finding이 하나라도 있으면 메인 에이전트가 차단 사항으로 보고 수정 가능 범위 안에서 고친다.
- 수정 후에는 관련 테스트와 보안 검토를 다시 실행한다.

서브에이전트 프롬프트는 다음 구조를 따른다.

```text
Use the security-review skill at .codex/skills/security-review as a verifier for {issue-id}.
Do not edit files. Read the issue document, GREEN result, refactor-log.md, relevant spec/architecture docs, and the current diff.
Return only security findings grouped by Low, Medium, High, with file references and whether each finding should block completion.
```

## 보안 검토 절차

1. `scripts/find_issue.py`로 이슈 디렉터리와 `issue.md`를 찾는다.
2. GREEN/BLUE 결과와 변경 파일을 확인한다.
3. `references/security-checklist.md`와 `docs/spec/spec-fixed.md`에서 이번 이슈에 적용되는 보안 요구사항을 추린다.
4. `references/tooling-policy.md`에 따라 기존 테스트와 이미 존재하는 보안/정적 분석 도구를 실행한다.
5. 필요한 새 보안 도구가 있으면 즉시 도입하지 말고 후보, 이유, 예상 변경 범위를 기록한다. 사용자가 승인한 경우에만 설정을 변경한다.
6. 서브에이전트에게 독립 보안 검토를 맡긴다.
7. 서브에이전트 finding을 검토하되, 근거가 없는 항목은 별도 확인 후 제외한다.
8. `Medium` 또는 `High` finding이 있으면 허용 범위 안에서 수정하고 관련 테스트를 재실행한다.
9. 수정 후 같은 범위로 보안 검토를 다시 수행한다.
10. `security-review.md`를 최신 스냅샷으로 갱신한다.

## 심각도 기준

- `High`: 인증/인가 우회, 타 사용자 데이터 접근, 서버 권위 게임 상태 조작, 토큰/비밀번호/세션 노출, 관리자 기능 오남용, 원격 코드 실행, SQL/명령 주입처럼 즉시 악용 가능한 결함
- `Medium`: 특정 조건에서 권한/소유권 검증이 약해지거나, rate limit/CSRF/CORS/STOMP 검증/오류 정보 노출/감사 로그 누락으로 실제 악용 경로가 생길 수 있는 결함
- `Low`: 직접 악용 가능성은 낮지만 보안 관측성, 메시지 품질, 방어적 검증, 설정 명확성을 개선할 수 있는 항목

`Medium` 이상은 차단한다. `Low`만 있으면 production을 수정하지 않고 `security-low-only`로 완료할 수 있다.

## 실행 명령

테스트 실행은 현재 Gradle 프로젝트에 맞춰 수행한다.

```bash
./gradlew test --tests 'fully.qualified.TestClass.method_name'
./gradlew test
```

보안/정적 분석 도구가 이미 구성되어 있으면 해당 프로젝트 명령을 사용한다. 새 도구 실행이 네트워크, 권한, 설치 문제로 막히면 원인을 분리해 `security-blocked` 또는 도구 후보로 기록한다.

## 로그 기록

현재 이슈 디렉터리의 `security-review.md`를 만들거나 갱신한다. `references/security-review-contract.md`를 읽고 그 계약의 항목과 상태 의미를 따른다.

- `security-pass`, `security-low-only`, `security-blocked`, `security-failed`는 실행 이력을 누적하지 말고 최신 스냅샷만 남긴다.
- `Medium` 이상 finding이 수정되어 재검증까지 통과하면 최종 상태는 `security-pass`로 기록하고, 수정된 finding과 재검증 결과를 남긴다.
- `Medium` 이상 finding이 남아 있으면 `security-failed`로 기록한다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 사용한 이슈 문서
- 검토 대상 production/resource 파일
- 서브에이전트 보안 검토 수행 여부
- 발견한 `Low`/`Medium`/`High` 항목 수
- `Medium`/`High` 수정 파일과 재검증 결과
- `security-review.md` 갱신 상태: `security-pass`, `security-low-only`, `security-blocked`, `security-failed`
- 실행한 테스트와 보안/정적 분석 명령
- 새 보안 도구 도입 후보가 있으면 사용자 승인 필요 여부

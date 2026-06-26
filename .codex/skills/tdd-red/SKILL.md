---
name: tdd-red
description: 로컬 feature 이슈 문서의 사용자 시나리오와 Given-When-Then AC를 Java/Spring 테스트 코드로 옮겨 TDD RED 단계를 수행해야 할 때 사용한다. 인자로 auth-1, auth-001, auth-issues-1, xxx-yyy-1처럼 마지막 토큰이 숫자인 이슈 식별자를 받아 docs/features/{feature}/issues의 이슈와 선행 이슈 상태를 확인하고, src/test/java 테스트와 현재 이슈 문서의 TDD RED 결과만 생성·수정하며 src/main, production skeleton, build.gradle, CI, 정적 분석 도구 설정, production resource는 수정하지 않는다.
---

# TDD RED

## 개요

로컬 이슈의 사용자 시나리오와 AC를 실패 가능한 RED 테스트로 옮긴다. RED 단계에서는 테스트 코드와 현재 이슈 문서의 RED 결과 기록만 작성하고, production 구현, production skeleton, 하네스 도입은 하지 않는다.

## 입력 규칙

- 모든 질문, 분석, 보고는 한국어로 작성한다.
- 사용자는 이슈 식별자 하나를 인자로 제공해야 한다.
- 인자가 없거나 마지막 하이픈 뒤 토큰이 숫자가 아니면 형식 오류를 보고하고 즉시 종료한다.
- 허용 예시는 `auth-1`, `auth-001`, `auth-issues-1`, `xxx-yyy-1`이다.
- 끝에서 두 번째 토큰이 `issues`이면 구분자로만 보고 feature 이름에서 제외한다.
- `xxx-yyy-1`은 feature=`xxx-yyy`, issue number=`1`로 해석한다.
- 이슈 번호 입력은 0-padding 없이 받아들이되, 이슈 파일 탐색은 번호의 정수값으로 비교한다. 예를 들어 `1`과 `001`은 같은 이슈 번호다.
- 이슈 문서는 `docs/features/{feature}/issues/{feature}-{nnn}-{slug}.md` 계열 파일에서 정확히 하나만 찾아야 한다. 없거나 여러 개면 추측하지 말고 종료한다.
- 이슈 탐색은 먼저 `scripts/find_issue.py`를 실행해 검증한다.

```bash
python3 .codex/skills/tdd-red/scripts/find_issue.py auth-1 --root .
```

## 읽을 문서

다음 순서로 존재하는 문서만 읽는다.

1. `scripts/find_issue.py`가 찾은 로컬 이슈 문서
2. 현재 이슈의 `depends_on`, 직전 번호 이슈, `## 의존 관계`에 적힌 선행 이슈 문서
3. 이슈 frontmatter 또는 본문에 적힌 PRD/TRD/architecture/traceability/websocket 관련 문서
4. FE/API 계약 영향을 확인하기 위한 `docs/spec/spec-fixed.md`, `docs/websocket-spec.md`, CORS/OpenAPI/JSON Schema/fixture 흔적
5. 테스트 대상 패키지와 기존 테스트 패턴을 파악하기 위한 `src/main/java`와 `src/test/java`

PRD/TRD가 없거나 이슈 내용만으로 테스트 대상, 패키지, 테스트 파일명을 결정할 수 없으면 사용자에게 확인을 요청한다.

## 선행 이슈 게이트

- 현재 이슈의 frontmatter `depends_on`과 본문 `## 의존 관계`를 먼저 확인한다.
- `depends_on`이 비어 있고 이슈 번호가 2 이상이면 같은 feature의 직전 번호 이슈를 암묵적 선행 후보로 본다.
- 선행 이슈가 있으면 해당 이슈의 AC 충족, 테스트 통과, `TDD RED 결과` 이후 진행 상태가 문서상 확인되는지 확인한다.
- 선행 이슈 완료 여부가 확인되지 않으면 테스트를 작성하지 말고 `blocked`로 보고한다.
- 현재 이슈 문서에 독립 이슈, 병렬 가능, 또는 선행 이슈 없음이 명시되어 있으면 직전 번호 이슈가 있어도 진행할 수 있다.

## 변경 허용 범위

- 원칙적으로 `src/test/java/**/*.java`만 생성하거나 수정한다.
- 다음 단계 전달을 위해 현재 이슈 문서에 `## TDD RED 결과` 섹션만 짧게 생성하거나 갱신할 수 있다.
- 기존 테스트 파일에 같은 책임의 테스트 클래스가 명확히 있으면 그 파일을 보완한다.
- 새 테스트 파일은 구현 코드 패키지와 동일한 패키지를 `src/test/java` 아래에 만든다.
- 파일명은 기본적으로 `{TargetClass}Test.java` 형식을 쓴다.
- 테스트 파일명이 중복되거나 대상 클래스·패키지가 불명확하면 작업을 멈추고 확인을 요청한다.
- `src/test/resources` fixture가 꼭 필요하면 사용자 확인 전에는 만들지 않는다.

다음은 RED 단계에서 금지한다.

- `src/main` 수정
- production 빈 클래스, 빈 메서드, 패키지 skeleton 생성
- production resource 수정
- `build.gradle`, `settings.gradle`, Gradle wrapper, CI 설정 수정
- ArchUnit, SpotBugs, PMD, Checkstyle, JaCoCo 같은 정적 분석 도구나 하네스 의존성 도입
- feature 구현을 위해 domain, service, controller, repository, DTO, entity를 추가하거나 수정

이미 하네스가 존재하는 경우에만 RED 테스트에서 그 하네스를 사용할 수 있다. 하네스가 없으면 `harness-missing`으로 보고하고 이 스킬에서 도입하지 않는다.

## 테스트 작성 규칙

- 이슈의 `관련 사용자 시나리오`, `Acceptance Criteria`, `테스트`, `구현 메모`를 기준으로 테스트 후보를 만든다.
- `[정상]`, `[경계]`, `[예외]` AC는 각각 독립 테스트 후보로 옮긴다.
- REST 또는 STOMP가 사용자나 FE에 보이는 결과이면 단위 테스트만 만들지 말고 API/계약 테스트 후보를 우선 검토한다.
- OpenAPI, JSON Schema, fixture, contract-test 하네스가 필요하지만 없으면 테스트 도입을 추측하지 말고 `harness-missing`으로 기록한다.
- 하나의 테스트 메서드는 하나의 관찰 가능한 행위나 상태 불변성을 검증한다.
- 테스트 메서드명은 snake_case로 작성한다.
- 성공해야 하는 시나리오는 `success_` 접두어를 붙인다.
- 실패, 예외, 거부, 검증 실패를 기대하는 시나리오는 `fail_` 접두어를 붙인다.
- 메서드명 마지막에는 `_given_{간단한_선행상황}`을 붙인다.
- 예: `success_find_user_board_given_queen_captured`
- 테스트 안에서는 `given`, `when`, `then` 구획이 드러나도록 배치한다.

## RED 절차

각 시나리오마다 아래 순서를 반복한다.

1. 테스트 껍데기를 먼저 작성한다.
   - `@Test` 메서드, 테스트명, given/when/then 주석 또는 구조만 만든다.
   - assertion이나 production 호출을 넣기 전, 해당 테스트만 실행한다.
   - 이 단계는 JUnit discovery, 컴파일, fixture 초기화 확인이 목적이므로 통과해야 한다.
2. 같은 테스트에 AC 기반 검증을 추가한다.
   - 정상 AC는 결과, 상태 변화, 응답 값을 검증한다.
   - 경계 AC는 제한, 상태 불변성, 동시성·멱등성 조건을 검증한다.
   - 예외 AC는 오류 응답, 예외 타입, 상태 불변성, 감사·보안·운영 로그 필요 여부를 검증한다.
3. 해당 테스트만 다시 실행한다.
   - 구현이 없어서 실패하면 정상 RED로 기록한다.
   - production 타입, 메서드, 패키지 skeleton이 없어서 컴파일되지 않으면 production을 만들지 말고 `compile-blocked`로 기록한다.
   - 테스트 코드 오탈자, 잘못된 import, 잘못된 fixture 때문에 실패하면 테스트 코드를 수정한다.
   - 기존 구현 때문에 통과하면 `already-green`으로 기록하고 테스트가 실제 AC를 검증하는지 재확인한다.
4. 다음 시나리오로 넘어간다.

모든 테스트를 작성한 뒤 가능한 범위에서 전체 테스트를 실행한다. 보고할 때는 기존 테스트 실패, 테스트 코드 오류, 의도된 RED 실패, `already-green`, `compile-blocked`, `harness-missing`을 구분한다.

## RED 결과 기록

현재 이슈 문서에 `## TDD RED 결과` 섹션을 만들거나 갱신한다. 긴 해설을 쓰지 말고 다음 항목만 남긴다.

- 테스트 파일
- 테스트 메서드와 연결 AC
- 상태: `skeleton-pass`, `red-fail`, `already-green`, `compile-blocked`, `harness-missing`, `blocked`
- 실행한 명령
- 실패 또는 차단 요약

## 실행 명령

테스트 실행은 현재 Gradle 프로젝트에 맞춰 수행한다.

```bash
./gradlew test --tests 'fully.qualified.TestClass.method_name'
./gradlew test
```

테스트 실행이 환경 문제로 실패하면 원인을 분리해 보고한다. 네트워크, 권한, 포트, DB 같은 외부 원인 때문에 검증할 수 없으면 테스트 파일 작성 결과와 미검증 항목을 명확히 남긴다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 사용한 이슈 문서
- 생성 또는 수정한 테스트 파일
- 갱신한 `TDD RED 결과`
- 추가한 테스트 메서드와 연결된 AC
- 각 테스트의 상태: `skeleton-pass`, `red-fail`, `already-green`, `compile-blocked`, `harness-missing`, `blocked`
- 전체 테스트 실행 결과
- 확인이 필요한 대상 클래스, 파일명, fixture, 하네스 이슈가 있으면 그 이유

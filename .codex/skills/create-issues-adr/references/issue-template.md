# Issue Template

로컬 이슈는 기능 PRD/TRD의 사용자 시나리오를 실제 구현 가능한 수직 슬라이스로 분리하기 위한 문서다. 요구사항 원문을 수정하지 않고, 출처와 테스트 가능성을 유지한다.

## 파일 경로

```text
docs/features/{feature}/issues/{feature}-{nnn}-{slug}.md
```

예:

```text
docs/features/matchmaking/issues/matchmaking-001-enter-matchmaking-queue.md
```

## Frontmatter

```yaml
---
id: "{feature}-{nnn}"
feature: "{feature}"
title: "{title}"
status: "draft"
slice_type: "vertical"
github_issue: null
github_url: null
source_documents:
  - "docs/features/{feature}/prd.md"
  - "docs/features/{feature}/trd.md"
source_scenarios: []
related_adrs: []
depends_on: []
---
```

`depends_on`은 참고용 링크가 아니라 TDD 시작 전 실행 게이트다. 같은 feature의 후속 번호 이슈는 기본적으로 이전 번호 이슈의 AC 충족과 테스트 통과를 전제로 하며, 독립 또는 병렬 가능 이슈만 빈 배열을 사용할 수 있다.

## 본문 형식

```markdown
# [{feature}-{nnn}] {title}

## 목적

이 이슈가 사용자 가치, 서버 책임, 운영 요구 중 무엇을 끝까지 연결해 달성하는지 적는다.

## 수직 슬라이스

- 사용자 관점의 시작점:
- 서버/도메인 행위:
- 저장 또는 외부 연동:
- 사용자 또는 호출자에게 보이는 결과:

계층별 수평 작업만 나열하지 않는다. 필요한 Controller, Service, Domain, Repository, Event, Test 작업은 이 슬라이스를 완성하기 위한 구현 메모로만 적는다.

## 관련 사용자 시나리오

PRD의 관련 사용자 시나리오를 인용 또는 요약한다.

- 출처:
- 시나리오:
- 이 이슈로 충족하는 부분:
- 이 이슈에서 제외하는 부분:

## 범위

- 구현할 항목을 체크 가능한 단위로 적는다.

## 제외 범위

- 이번 이슈에서 의도적으로 제외하는 항목을 적는다.

## Acceptance Criteria

AC는 PRD 사용자 시나리오에서 도출하고 Given-When-Then으로 작성한다. 각 항목은 반드시 `[정상]`, `[경계]`, `[예외]` 중 하나로 시작한다.

- [정상] Given {정상 선행 조건}, When {사용자 또는 시스템 행위}, Then {기대 결과와 상태 변화}
- [경계] Given {경계 조건}, When {사용자 또는 시스템 행위}, Then {기대 결과와 상태 불변성 또는 제한}
- [예외] Given {예외 선행 조건}, When {사용자 또는 시스템 행위}, Then {오류 응답, 상태 불변성, 감사/보안/운영 로그 필요 여부}

## TDD 진행 순서

1. 선행 이슈의 AC 충족과 테스트 통과 여부를 확인한다.
2. 실패하는 테스트를 먼저 작성하고 `TDD RED 결과`에 테스트 파일, 메서드, 상태를 기록한다.
3. `[정상]` AC를 통과하는 최소 구현을 작성한다.
4. `[경계]` AC를 통과하도록 상태 검증, 제한, 동시성, 멱등성 조건을 보강한다.
5. `[예외]` AC를 통과하도록 오류 응답과 상태 불변성을 보장한다.
6. 리팩터링 후 정적 분석, 아키텍처 규칙, 테스트 하네스 검사를 실행한다.

## 테스트

- 단위 테스트:
- 통합 테스트:
- 계약/API 테스트: REST/STOMP가 사용자 또는 외부 호출자에게 보이는 결과이면 OpenAPI, JSON Schema, fixture, contract-test 필요 여부를 적는다.
- 동시성/멱등성 테스트:
- 정적 분석 또는 하네스 검사: 하네스가 없으면 기능 이슈에 묻지 말고 별도 선행 작업 또는 미확정 사항으로 분리한다.
- 필요 시 수동 검증:

## 구현 메모

- 관련 도메인, 계층, API, 저장소, 이벤트, 설정, 마이그레이션 고려사항을 적는다.
- ADR이 필요한 판단은 관련 ADR로 분리하고 링크한다.
- 관측성, 로깅, 메트릭, 알림 조건이 필요하면 테스트 또는 운영 검증과 연결한다.

## 의존 관계

- 선행 이슈: 없으면 독립 또는 병렬 가능 사유를 적는다.
- 선행 이슈 완료 조건: AC 충족, 테스트 통과, 후속 이슈가 기대하는 구현 surface를 적는다.
- 후행 이슈:
- 관련 ADR:

## TDD RED 결과

- 테스트 파일:
- 테스트 메서드와 연결 AC:
- 상태: `skeleton-pass`, `red-fail`, `already-green`, `compile-blocked`, `harness-missing`, `blocked`
- 실행한 명령:
- 실패 또는 차단 요약:

## 관련 문서

- PRD/TRD/architecture/traceability 문서 경로와 관련 섹션을 적는다.

## 미확정 사항

- PRD/TRD만으로 AC를 확정할 수 없는 내용은 여기에 적고 사용자 확인 대상으로 남긴다.
```

## 분리 기준

- 하나의 이슈는 한 PR에서 검토 가능한 수직 슬라이스 크기로 유지한다.
- 사용자 시나리오 하나가 너무 크면 "정상 흐름", "권한/상태 경계", "예외/실패 처리", "운영 관측성"처럼 독립 검증 가능한 수직 슬라이스로 나눈다.
- 공통 기반 작업은 기능 이슈에 묻지 말고 별도 이슈로 만든다. 단, 그 이슈도 가능한 한 TDD 가능한 결과와 검증 기준을 가져야 한다.
- 후속 번호 이슈는 기본적으로 이전 번호 이슈 완료 후 진행한다. 병렬 가능 이슈는 의존 관계 섹션에 독립 사유를 남긴다.
- 수용 기준을 Given-When-Then으로 독립 검증할 수 없으면 더 작게 나눈다.
- 경계와 예외 AC가 없는 이슈는 기본적으로 불완전한 이슈로 간주한다. 근거가 부족하면 미확정 사항으로 남긴다.
- GitHub Issue 제목과 본문에는 항상 로컬 ID `{feature}-{nnn}`를 사용한다. 파일명 slug는 사람이 읽기 위한 보조 정보일 뿐이다.

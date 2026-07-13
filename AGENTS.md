# Backend Agent Guide

## 기본 원칙

- `docs/spec/spec-fixed.md`가 요구사항의 최우선 원천이다.
- 문서가 충돌하면 상위 산출물을 따르고 충돌 내용을 보고한다.
- 하위 산출물에서 상위 산출물에 없는 정책을 임의로 확정하지 않는다.
- 코드, 문서, 경로 또는 작업 흐름이 바뀌면 이 파일도 함께 갱신한다.
- 세부 정책은 원천 문서에만 기록하고 이 파일에는 진입점과 공통 규칙만 둔다.

## 필수 워크플로

```text
$spec-interview -> $spec-review -> $create-prd -> $architecture-decision -> $negotiate-fe-be-contract -> $sync-be-contracts -> $create-trd -> $create-issues-adr -> $tdd-workflow -> $create-pr
```

- 요구사항 변경은 인터뷰와 리뷰를 거친다.
- 아키텍처 선택 또는 확정 사항 변경은 `$architecture-decision`으로 재검토한다.
- FE 공유 계약은 REST·STOMP·인증·오류·상태 동기화·projection·fixture 등 전체 협상 topic이 `fixed`이고 `docs/negotiation/session.md`가 `completed`가 된 뒤에만 BE 계약 문서로 동기화한다. topic별 부분 sync는 하지 않는다.
- TRD 작성 후 이슈와 ADR을 만들고, 선행 조건이 충족된 이슈만 구현한다.
- `$tdd-workflow` 완료와 전체 검증 후 PR을 생성한다.
- 유효한 상위 산출물이 있으면 불필요하게 이전 단계를 반복하지 않는다.

## 문서 경로

### 요구사항과 제품

- `docs/spec/spec-original.md`: 최초 원자료와 재인터뷰 입력
- `docs/spec/spec-fixed.md`: 확정 요구사항
- `docs/prd.md`: 전체 PRD 허브
- `docs/features/*/prd.md`: 기능별 PRD
- `docs/traceability.md`: 요구사항 추적성

### 아키텍처

- `docs/architecture/current-fixed.md`: 현재 확정본 포인터. 아키텍처 확인 시 가장 먼저 읽는다.
- `docs/architecture/fixed-*/`: 구현, 인프라, CI/CD, 하네스 확정본
- `docs/architecture/interview-*/`: 결정 과정과 승인 기록
- `docs/architecture/*.md`: 서버 구조, 인프라, 배포, CI/CD, 하네스, 추적성과 리뷰 기록
- `docs/architecture/adr/`, `docs/architecture/adr-index.md`: 서버 구조·인프라·CI/CD·하네스 선택지의 채택·제외 이유와 대체 관계

클라우드 제공자, 자동 배포, 분산 시스템, 트래픽 목표, 비용 상한, SLO 등 미확정 사항이 필요해지면 임의 결정하지 않고 `$architecture-decision`을 다시 수행한다.

### 계약과 기술 설계

- `docs/negotiation/{topic}/`: FE/BE 계약 협상 기록
- `docs/contracts/{topic}.md`: 확정된 BE 구현 계약
- `docs/trd.md`: 전체 TRD 허브
- `docs/features/*/trd.md`: 기능별 TRD
- `docs/websocket-spec.md`: 실시간 통신 공통 규약
- `docs/milestones.md`: 구현 순서와 마일스톤

### 이슈와 ADR

- `docs/features/*/issues/`: 구현 이슈, AC, 테스트 관점과 TDD 결과
- `docs/issue-map.md`: 이슈 순서와 의존성
- `docs/adr/`, `docs/adr-index.md`: 기능별 기술 결정과 대안

아직 없는 경로는 해당 워크플로 단계에서 생성하며 빈 문서를 미리 만들지 않는다.

## 코드 경계

상세 기준은 `current-fixed.md`가 가리키는 `impl-fixed.md`를 따른다.

- feature-first 모듈러 모놀리스와 헥사고날/클린 원칙을 적용한다.
- 기능 모듈은 `domain`, `application`, `adapter/in`, `adapter/out`, `configuration` 경계를 따른다.
- 도메인은 Spring, JPA, 웹, 메시징 등 외부 기술에 의존하지 않는다.
- 모듈 간 협력은 공개 애플리케이션 포트 또는 도메인 이벤트를 사용한다.
- 전역 계층 패키지, 모듈 간 직접 저장소 접근과 우회 의존성을 만들지 않는다.
- DB 스키마 변경은 Flyway 마이그레이션으로 관리한다.

## 검증과 하네스

- 필수 로컬 게이트: `./gradlew spotlessCheck test`
- 포맷 수정: `./gradlew spotlessApply`
- 빌드 설정: `build.gradle`
- CI: `.github/workflows/backend-ci.yml`
- 구조 검사: `src/test/java/org/zzambas/tcgonlinechessbe/architecture/ArchitectureTest.java`
- 하네스 규칙: `docs/architecture/harness-guardrails.md`와 현재 `harness-fixed.md`
- 산출물 최신성: `.codex/artifact-state.json`, `.codex/scripts/artifact-state.py`
- 스킬 계약: `.codex/skills/*/SKILL.md`
- 에이전트 역할: `.codex/agents/`

테스트, 포맷, ArchUnit, 보안 검토와 저장소 훅을 우회하지 않는다. 문서만 변경해도 관련 검사와 `git diff --check`를 수행한다.

## 작업 규칙

- 시작 전 `git status --short`로 기존 변경을 확인하고 관련 없는 변경을 되돌리지 않는다.
- 구현 범위와 AC는 현재 이슈 문서를 기준으로 제한한다.
- 외부 계약이 필요한 이슈는 `docs/contracts/`의 확정 상태를 먼저 확인한다.
- 하위 산출물을 만들기 전 출처 상태를 검증하고, stale이면 해당 산출물을 다시 생성한 뒤 상태를 기록한다.
- `$tdd-workflow`의 RED, GREEN, BLUE, 보안 검토와 AC 검증 순서를 따른다.
- 요구사항, 계약 또는 아키텍처 충돌은 코드를 맞추기 전에 상위 단계에서 해결한다.
- 커밋은 `$git-commit`으로 응집된 작업 단위별로 기록한다.
- PR에는 검증 결과와 근거가 있는 동일 저장소 이슈만 연결한다.

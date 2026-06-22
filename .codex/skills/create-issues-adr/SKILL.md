---
name: create-issues-adr
description: PRD/TRD와 아키텍처 산출물을 바탕으로 구현 가능한 로컬 이슈를 수직 슬라이싱하고 ADR을 작성해야 할 때 사용한다. docs/features/{feature}/prd.md, trd.md, docs/architecture/*, 기존 issues/adr 문서를 읽어 PRD 사용자 시나리오별 Given-When-Then AC를 [정상]/[경계]/[예외]로 포함한 docs/features/{feature}/issues/{feature}-{nnn}.md와 docs/features/{feature}/adr/adr-{nnn}-{slug}.md를 한국어로 생성·갱신하고, 선택적으로 GitHub Issue 번호를 로컬 문서에 연결해야 할 때 사용한다. create-prd 이후 issue 분리, TDD 가능한 수직 슬라이스 이슈 작성, ADR 작성, ADR 대안 비교, 로컬 이슈와 GitHub Issue 매핑, issue-map/adr-index 갱신에 사용하며 spec/prd/trd 원문은 수정하지 않는다.
---

# Create Issues ADR

## 기본 원칙

- 모든 질문, 분석, 문서는 한국어로 작성한다.
- `docs/spec/*`, `docs/prd.md`, `docs/trd.md`, `docs/features/{feature}/prd.md`, `docs/features/{feature}/trd.md`는 입력 문서로만 취급하고 수정하지 않는다.
- 기존 `docs/features/{feature}/issues/*`, `docs/features/{feature}/adr/*`, `docs/issue-map.md`, `docs/adr-index.md`가 있으면 먼저 읽고 중복 생성 대신 보완한다.
- 로컬 문서를 원천 추적 기준으로 삼는다. GitHub Issue 생성은 사용자가 명시적으로 요청하고 승인한 경우에만 수행한다.
- 이슈는 PRD 사용자 시나리오와 수용 기준을 구현 가능한 수직 슬라이스로 나눈다. 계층별 수평 작업만 나열하는 이슈는 만들지 않는다.
- 각 수직 슬라이스 이슈는 TDD로 구현할 수 있어야 하며, 실패 테스트 작성에서 시작할 수 있을 만큼 AC와 테스트 관점을 구체화한다.
- ADR은 단순 결론 문서가 아니다. 반드시 현재 프로젝트 상황, 비교 대안, 선택 이유, 선택 결과를 기록한다.

## 입력 확인

우선 존재하는 문서만 읽는다.

- 공통 산출물: `docs/prd.md`, `docs/trd.md`, `docs/milestones.md`, `docs/traceability.md`, `docs/websocket-spec.md`
- 기능 산출물: `docs/features/{feature}/prd.md`, `docs/features/{feature}/trd.md`
- 아키텍처 산출물: `docs/architecture/*`
- 기존 후속 산출물: `docs/features/{feature}/issues/*`, `docs/features/{feature}/adr/*`, `docs/issue-map.md`, `docs/adr-index.md`

기능명이 명시되지 않으면 `docs/features/*/prd.md`와 `trd.md`를 기준으로 대상 feature를 도출하고, 범위가 너무 넓으면 사용자에게 한 번에 하나의 범위 질문을 한다.

## 이슈 작성 규칙

자세한 형식은 `references/issue-template.md`를 읽고 따른다.

- 로컬 이슈 파일은 `docs/features/{feature}/issues/{feature}-{nnn}.md` 형식으로 작성한다.
- `{feature}`는 기존 feature 디렉터리명을 그대로 사용한다.
- `{nnn}`은 feature별 001부터 시작하고, 기존 번호가 있으면 다음 번호를 사용한다.
- 각 이슈는 `{feature}-{nnn}` 접두어를 가진 하나의 Markdown 파일이어야 한다.
- 이슈는 사용자에게 관찰 가능한 가치 또는 시스템 행위가 끝까지 연결되는 수직 슬라이스로 나눈다.
- 계층별 수평 이슈, 예를 들어 "엔티티만 작성", "Repository만 작성", "Controller만 작성" 같은 단독 이슈는 피한다. 다만 마이그레이션, 하네스, 공통 인프라처럼 독립 선행 작업이 불가피하면 별도 이슈로 만들고 의존 관계를 명시한다.
- 각 이슈에는 PRD의 관련 사용자 시나리오를 인용 또는 요약하고, 그 시나리오에서 AC를 도출한다.
- AC는 Given-When-Then 형식으로 작성하고 각 항목 앞에 `[정상]`, `[경계]`, `[예외]` 중 하나를 붙인다.
- 정상 상황뿐 아니라 경계 조건과 예외 상황을 반드시 포함한다. PRD/TRD에 근거가 부족하면 "미확정 사항"으로 표시하고 사용자 확인이 필요하다고 적는다.
- 각 이슈에는 TDD 진행 순서를 포함한다. 먼저 실패해야 할 테스트를 쓰고, 최소 구현, 리팩터링, 하네스/정적 분석 검증 순으로 적는다.
- 수용 기준과 테스트는 PRD/TRD의 요구사항과 연결될 만큼 구체적으로 작성한다.

## ADR 작성 규칙

자세한 형식은 `references/adr-template.md`를 읽고 따른다.

- ADR 파일은 `docs/features/{feature}/adr/adr-{nnn}-{slug}.md` 형식으로 작성한다.
- ADR 본문은 반드시 4요소를 유지한다.
  - `Status`
  - `Context`
  - `Decision`
  - `Consequences`
- `Context`에는 결정 배경뿐 아니라 대안 비교 표를 포함한다.
- 대안 비교 표에는 대안, 장점, 단점, 현재 프로젝트 상황에서의 적합성, 최종 선택 여부 또는 제외 이유를 적는다.
- `Decision`에는 선택된 대안이 현재 요구사항, 기존 코드, 아키텍처 문서, 비용, 운영 부담, 구현 범위와 어떻게 맞물리는지 설명한다.
- 선택되지 않은 대안도 충분히 검토한다. "복잡함", "불필요함" 같은 단정만 쓰지 말고 현재 상황과 연결된 이유를 적는다.
- ADR이 필요하지 않은 단순 구현 판단은 이슈의 구현 메모에 남기고 ADR로 승격하지 않는다.

## GitHub Issue 연결

GitHub Issue 연결을 요청받으면 `references/github-issue-policy.md`를 읽고 따른다.

- 기본 동작은 로컬 Markdown 생성이다.
- GitHub Issue 생성 또는 갱신은 사용자가 명시적으로 요청하고 승인한 경우에만 수행한다.
- GitHub Issue 제목은 `[{feature}-{nnn}] {title}` 형식을 사용한다.
- 생성 후 로컬 이슈 frontmatter와 `docs/issue-map.md`에 GitHub Issue 번호와 URL을 기록한다.
- GitHub Issue 본문에는 로컬 이슈 문서 경로, 관련 ADR, 주요 수용 기준을 포함한다.

## 중복 검사

- 문서 생성 전후에 가능하면 `scripts/scan_issue_ids.py`를 실행해 로컬 이슈 ID, ADR ID, GitHub Issue 연결 중복을 검사한다.
- 이 스크립트는 읽기 전용이어야 하며, 결과가 실패면 중복 원인을 먼저 보고하고 문서 생성 또는 연결을 보류한다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 생성 또는 수정한 이슈 문서 목록
- 생성 또는 수정한 ADR 문서 목록
- GitHub Issue 연결 여부
- 남은 미확정 사항 또는 사용자의 승인이 필요한 항목

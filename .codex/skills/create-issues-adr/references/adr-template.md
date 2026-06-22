# ADR Template

ADR은 Architecture Decision Record다. 이 스킬에서 ADR은 반드시 4요소를 중심으로 작성한다.

## 파일 경로

```text
docs/features/{feature}/adr/adr-{nnn}-{slug}.md
```

예:

```text
docs/features/matchmaking/adr/adr-001-use-redis-for-queue-state.md
```

## Frontmatter

```yaml
---
id: "ADR-{FEATURE}-{nnn}"
feature: "{feature}"
status: "proposed"
related_issues: []
source_documents:
  - "docs/features/{feature}/prd.md"
  - "docs/features/{feature}/trd.md"
---
```

`{FEATURE}`는 feature 디렉터리명을 대문자와 하이픈 유지 형태로 적는다. 예: `MATCHMAKING`, `GAME-ROOM`.

## 본문 형식

```markdown
# ADR-{FEATURE}-{nnn}. {결정 제목}

## Status

{proposed | accepted | superseded | deprecated}

## Context

현재 결정이 필요한 배경을 적는다. 다음 항목을 포함한다.

- 관련 요구사항과 기능 범위
- 기존 코드와 아키텍처 상태
- 운영, 비용, 성능, 확장성, 테스트, 하네스 제약
- 지금 결정하지 않으면 생기는 위험

### Alternatives

| 대안 | 장점 | 단점 | 현재 프로젝트 상황에서의 적합성 | 최종 선택 여부 또는 제외 이유 |
| --- | --- | --- | --- | --- |
| {대안 A} | {장점} | {단점} | {현재 요구사항, 코드, 운영 상황과의 연결} | {선택 또는 제외 이유} |
| {대안 B} | {장점} | {단점} | {현재 요구사항, 코드, 운영 상황과의 연결} | {선택 또는 제외 이유} |

## Decision

선택한 대안을 명확히 적는다. 선택 이유는 현재 프로젝트의 요구사항, 기존 구현 범위, 아키텍처 문서, 팀 운영 부담, 비용, 테스트 가능성과 연결해 설명한다.

## Consequences

이 결정으로 생기는 결과를 적는다.

- 긍정적 영향
- 감수해야 할 비용과 복잡도
- 선택받지 않은 대안 대비 잃는 것
- 구현 이슈와 테스트에 반영할 사항
- 재검토 조건
```

## ADR 승격 기준

다음 중 하나라도 해당하면 ADR 후보로 본다.

- 서버 구조, 모듈 경계, 계층 의존성, 데이터 저장 방식, 메시징, 캐시, 배포/운영 방식에 영향을 준다.
- 되돌리기 어렵거나 여러 이슈에 반복 영향을 준다.
- 비용, 운영 복잡도, 성능, 확장성, 테스트 하네스에 의미 있는 차이를 만든다.
- 여러 대안이 실질적으로 가능하고 선택 이유를 남겨야 한다.

단순 구현 세부사항, 일회성 리팩터링, 요구사항에 이미 명시된 결론은 ADR이 아니라 이슈 구현 메모에 남긴다.

---
name: create-prd
description: docs/spec/spec-fixed.md를 원천 명세로 읽고 현재 요구사항에 맞는 feature 단위를 유동적으로 도출한 뒤 docs/prd.md, docs/trd.md, docs/traceability.md, docs/milestones.md, docs/websocket-spec.md와 docs/features/{feature}/prd.md, trd.md 초안을 한국어로 생성해야 할 때 사용한다. PRD/TRD 분리, feature별 사용자 시나리오와 엣지 케이스 재배치, 권한/상태별 제한, 실패 시 상태 불변성, 동시성/멱등성, 오류 코드, 테스트 관점, 원천 섹션 추적, WebSocket 공통 계약 초안, 마일스톤 초안 작성에 사용하며 spec-fixed.md 수정, 요구사항 인터뷰, 스펙 리뷰, issue 분리, ADR 작성은 하지 않는다.
---

# Create PRD

## 개요

`docs/spec/spec-fixed.md`를 원천 명세로 삼아 PRD/TRD 문서 세트를 생성한다. feature 단위는 고정 목록을 쓰지 않고, 현재 명세의 사용자 가치, 구현 책임, 데이터/상태 경계, API/STOMP 경계, 테스트 가능성을 기준으로 매번 도출한다.

## 기본 원칙

- 모든 질문, 분석, 문서 초안은 한국어로 작성한다.
- 먼저 `docs/spec/spec-fixed.md`를 끝까지 읽고 큰 번호 섹션 목록을 확인한다.
- `docs/spec/spec-fixed.md`는 읽기 전용 원천 문서로 취급하고 수정하지 않는다.
- `spec-interview`처럼 요구사항을 새로 인터뷰하거나 원천 명세를 보완하지 않는다.
- `spec-review`처럼 큰 번호 섹션별 리뷰나 검토 확정 절차를 수행하지 않는다.
- issue 파일과 ADR 파일은 생성하지 않는다. 이 작업은 추후 별도 스킬 범위로 남긴다.
- feature 목록을 하드코딩하지 않는다. 단, 도출한 feature 이름은 소문자 hyphen-case 영문 폴더명으로 정한다.
- 전체 `docs/prd.md`와 `docs/trd.md`는 긴 상세 문서가 아니라 허브/요약/링크 문서로 작성한다.
- 상세 제품/기술 요구사항은 `docs/features/{feature}/prd.md`와 `docs/features/{feature}/trd.md`에 작성한다.
- 원천 명세의 큰 번호 섹션은 feature 폴더명으로 쓰지 않고 `source_sections`와 `docs/traceability.md`로 추적한다.

## 진행 절차

1. `docs/spec/spec-fixed.md` 전체를 읽는다.
2. `scripts/extract_spec_sections.py --file docs/spec/spec-fixed.md --list`로 큰 번호 섹션 목록과 라인 번호를 확인한다.
3. 원천 섹션을 다음 기준으로 분류한다.
   - 공통 문서에 반영할 전역 섹션: 개요, 문서 목적, 용어, MVP 범위, 수용 기준, 확장 후보, 공통 API 원칙, 공통 데이터 저장 원칙 등
   - feature로 분리할 기능 섹션: 사용자 기능, 게임 기능, 관리자/운영 기능처럼 구현 책임과 수용 기준을 가질 수 있는 도메인
   - 공통 계약 문서로 분리할 섹션: STOMP/WebSocket destination, 이벤트, 재접속, 실시간 오류 등
4. feature 후보를 도출한다. feature는 다음 조건을 만족해야 한다.
   - 하나 이상의 사용자 또는 운영자 가치가 있다.
   - 관련 PRD와 TRD를 독립 문서로 작성할 만큼 응집도가 있다.
   - 구현 issue로 나눌 수 있는 책임 경계가 있다.
   - 다른 feature와 중복되는 내용은 traceability에서 연결하고, 본문은 한쪽을 기준 문서로 삼는다.
5. 원천 명세의 `예외 및 엣지 케이스`, `핵심 수용 기준`, `구현 전 필수 확정 사항`, `MVP 제외 및 이후 확장 후보`를 feature별로 재배치할 후보를 표시한다.
6. 사용자가 feature 분할안을 요구했거나 분할이 모호하면 파일 작성 전에 세션에서 feature map을 제시하고 확인한다. 명확하면 합리적 기준으로 진행한다.
7. 아래 문서 구조와 작성 기준을 따른다.
8. 다음 공통 문서를 생성하거나 갱신한다.
   - `docs/prd.md`
   - `docs/trd.md`
   - `docs/traceability.md`
   - `docs/milestones.md`
   - `docs/websocket-spec.md`
9. 각 feature마다 다음 문서를 생성하거나 갱신한다.
   - `docs/features/{feature}/prd.md`
   - `docs/features/{feature}/trd.md`
10. 작성 후에는 생성/수정한 파일, 도출한 feature 목록, 남은 모호함, 원천 섹션 추적 방식을 간단히 보고한다.

## Feature 도출 기준

feature를 만들 때는 `spec-fixed.md`의 큰 번호 섹션을 그대로 폴더로 옮기지 않는다. 섹션은 문서 설명 순서이고, feature는 구현과 협업의 경계다.

다음 경우는 feature보다 공통 문서에 가깝다.

- 문서 목적과 범위
- 용어 정의
- MVP 포함/제외 범위
- 전체 사용자 시나리오
- 공통 API 또는 인터페이스 원칙
- 공통 데이터 저장 원칙
- 전체 수용 기준
- 구현 전 확정 사항
- 이후 확장 후보

다음 경우는 feature 후보로 검토한다.

- 사용자나 관리자가 직접 사용하는 독립 기능
- 별도 도메인 모델 또는 상태 전이를 갖는 기능
- REST API 또는 STOMP 이벤트 계약이 독립적으로 필요한 기능
- 별도 테스트 시나리오와 수용 기준을 가질 수 있는 기능
- FE 프로젝트가 독립 화면/흐름으로 참고할 가능성이 높은 기능

## 문서 작성 규칙

- 원천 명세에서 확정된 요구사항과 추론을 구분한다. 추론은 "원천 명세로부터의 정리" 또는 "문서화 가정"으로 표시한다.
- 전체 `docs/prd.md`와 `docs/trd.md`는 상세 본문이 아니라 목적, 원천 문서, 전체 원칙, feature 문서 링크를 담는 허브로 작성한다.
- feature PRD에는 대상 사용자, 사용자 가치, 포함/제외 범위, 주요 흐름, 상세 사용자 시나리오, 상태/권한별 엣지 케이스, FE 표시 기대, 수용 기준, 미확정 사항을 작성한다.
- feature TRD에는 서버 책임, 도메인 상태와 불변식, 데이터 저장, 명령/데이터 흐름, REST/STOMP 영향, 권한/검증, 동시성/멱등성, 오류 코드와 상태 불변성, 운영/관측 영향, 테스트 시나리오, 미확정 사항을 작성한다.
- feature PRD의 상세 사용자 시나리오는 최소 2개 이상 작성한다. 성공 흐름만 쓰지 말고 실패, 제한, 경계 조건 중 적어도 1개를 포함한다.
- feature TRD는 원천 명세의 `예외 및 엣지 케이스`와 `핵심 수용 기준`을 해당 feature로 재배치해 구현자가 테스트 조건을 바로 도출할 수 있게 작성한다.
- 실패 흐름에는 사용자에게 보이는 결과와 서버에서 변경되면 안 되는 상태를 함께 적는다.
- 원천 명세에 없는 endpoint, payload, DB schema, 정책값은 임의 확정하지 않고 "계약 후보" 또는 "미확정 사항"으로 표시한다.
- WebSocket 상세 계약은 feature TRD에 중복해 길게 쓰지 않고 `docs/websocket-spec.md`를 기준 문서로 둔다.
- feature TRD에는 관련 실시간 계약이 있으면 `docs/websocket-spec.md` 링크와 이벤트 이름 수준만 적는다.
- 마일스톤은 구현 순서와 의존 관계를 확인하기 위한 상위 단계로 작성하고, issue 목록은 만들지 않는다.

## 문서 구조

다음 구조만 생성한다.

```text
docs/
  prd.md
  trd.md
  traceability.md
  milestones.md
  websocket-spec.md
  features/
    {feature}/
      prd.md
      trd.md
```

다음 구조는 생성하지 않는다.

```text
docs/features/{feature}/issues/
docs/features/{feature}/adr/
```

## Feature PRD 필수 섹션

feature별 `prd.md`는 다음 섹션을 포함한다.

- `# {Feature Name} PRD`
- `## 목적`
- `## 원천 섹션`
- `## 대상 사용자`
- `## 범위`
- `## 주요 사용자 흐름`
- `## 상세 사용자 시나리오`
- `## 상태/권한별 엣지 케이스`
- `## FE 표시 기대`
- `## 수용 기준`
- `## 미확정 사항`
- `## 관련 문서`

상세 사용자 시나리오는 다음 형식을 따른다.

```markdown
### 시나리오 N. {성공, 실패, 제한, 경계 흐름 이름}

- 시작 조건: {계정 상태, 데이터 상태, 경기/콘텐츠 상태}
- 사용자 행동: {사용자가 수행하는 행동}
- 서버 반응: {서버가 검증하고 확정하는 내용}
- 사용자에게 보이는 결과: {FE가 표시해야 하는 서버 확정 결과}
- 완료 조건: {성공 조건 또는 변경되지 않아야 하는 상태}
```

## Feature TRD 필수 섹션

feature별 `trd.md`는 다음 섹션을 포함한다.

- `# {Feature Name} TRD`
- `## 목적`
- `## 원천 섹션`
- `## 서버 책임`
- `## 데이터와 상태`
- `## 도메인 상태와 불변식`
- `## 명령/데이터 흐름`
- `## 인터페이스 영향`
- `## 권한과 검증`
- `## 예외 처리`
- `## 동시성 및 멱등성`
- `## 오류 코드와 상태 불변성`
- `## 운영 및 관측 영향`
- `## 테스트 시나리오`
- `## 미확정 사항`
- `## 관련 문서`

`오류 코드와 상태 불변성`에는 관련 공통 오류 코드, 실패 시 변경되면 안 되는 도메인 상태, 실패해도 저장될 수 있는 보안 로그/감사 로그/Rate Limit 카운터를 구분해 작성한다.

## 보조 리소스

- 큰 번호 섹션 목록 추출과 단일 섹션 발췌에는 `scripts/extract_spec_sections.py`를 사용한다.

## 검증

문서 생성 후 다음을 확인한다.

- `docs/spec/spec-fixed.md`가 수정되지 않았다.
- `docs/features/{feature}/issues` 또는 `adr`가 생성되지 않았다.
- feature 목록이 스킬에 하드코딩된 기본값이 아니라 현재 원천 명세 분석 결과로 설명된다.
- `docs/traceability.md`에서 원천 섹션과 산출 문서의 연결을 추적할 수 있다.
- 전체 PRD/TRD는 허브 문서이고, 상세 요구사항은 feature별 PRD/TRD에 위치한다.
- 각 feature PRD에 최소 2개 이상의 상세 사용자 시나리오가 있다.
- 각 feature PRD에 상태/권한별 엣지 케이스와 FE 표시 기대가 있다.
- 각 feature TRD에 실패 시 상태 불변성, 동시성/멱등성, 오류 코드, 테스트 시나리오가 있다.
- 원천 명세의 24번 예외와 25번 수용 기준이 공통 문서에만 머물지 않고 관련 feature 문서에 재배치되어 있다.

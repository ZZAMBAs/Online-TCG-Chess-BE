---
name: architecture-decision
description: architecture-interview와 architecture-review를 하나의 승인 게이트형 워크플로로 묶어 서버 구현 아키텍처, 인프라, CI/CD, AI 하네스 결정을 확정해야 할 때 사용한다. 인터뷰 후 리뷰를 수행하고, 리뷰에서 수정 사항이 나오면 최대 3회까지 인터뷰 방식으로 재결정하고 재리뷰하며, docs/architecture/interview-{yyyymmdd}, docs/architecture/fixed-{yyyymmdd}, 현재 fixed 포인터 문서를 남겨야 할 때 사용한다.
---

# Architecture Decision

## 개요

`architecture-interview`로 아키텍처 결정을 구체화하고 `architecture-review`로 독립 검토한 뒤, 필요한 재결정 루프를 제한적으로 반복해 확정본을 남긴다. 이 스킬은 두 스킬의 상세 질문·검토 규칙을 복사하지 않고, 실행 순서와 산출물 계약을 강제한다.

## 기본 원칙

- 모든 질문, 요약, 문서는 한국어로 작성한다.
- 먼저 `.codex/skills/architecture-interview/SKILL.md`와 `.codex/skills/architecture-review/SKILL.md`를 끝까지 읽고 그 규칙을 따른다.
- 기존 `docs/architecture/*` 문서와 현재 구현·설정 파일을 읽어 이미 확정된 결정을 재사용한다.
- 기능 상세, API payload, DB column, 도메인 정책값, 화면 문구처럼 PRD/TRD 또는 feature 문서가 소유하는 항목은 직접 확정하지 않는다.
- 파일 작성 전에는 반영 예정 요약을 세션에 제시하고 사용자 승인을 받는다.
- production 기능 코드, controller/service/repository 기능 구현, 도메인 정책 구현은 작성하지 않는다.
- 승인된 아키텍처·하네스·CI 결정이 문서만으로 후속 작업을 막는 경우에만 기존 두 스킬이 허용한 repo 설정 범위 안에서 반영한다.

## 날짜와 경로

워크플로 시작일의 로컬 날짜를 `yyyymmdd`로 정한다. 같은 날 같은 워크플로를 이어가면 같은 디렉터리를 갱신하고, 다른 날 새 확정본을 만들면 새 날짜 디렉터리를 만든다.

```text
docs/architecture/
  interview-{yyyymmdd}/
    interview-log.md
    review-loop-01.md
    review-loop-02.md
    review-loop-03.md
    final-summary.md
  fixed-{yyyymmdd}/
    infra-fixed.md
    impl-fixed.md
    harness-fixed.md
    *.html
  current-fixed.md
```

- `interview-{yyyymmdd}/interview-log.md`: 질문, 추천안, 사용자 답변, 승인 여부, 미확정 사항, 상위 산출물 재검토 필요 항목을 시간순으로 기록한다.
- `review-loop-{nn}.md`: 각 리뷰 라운드의 검토 범위, 핵심 이슈, 재결정 질문, 사용자 승인, 재리뷰 결과를 기록한다. 해당 루프가 없으면 만들지 않는다.
- `final-summary.md`: 전체 루프 수, 최종 확정 여부, 남은 미확정·재검토 항목, 후속 스킬 연계 항목을 기록한다.
- `fixed-{yyyymmdd}/infra-fixed.md`: 클라우드/호스팅, 컴퓨팅, 네트워크/TLS/CDN, DB/캐시/메시징/파일 저장소, secret, 환경 전략, 관측·운영, capacity/cost guardrail 확정본을 기록한다.
- `fixed-{yyyymmdd}/impl-fixed.md`: 서버 아키텍처 스타일, 기술 스택, 패키지·모듈 경계, 의존성 방향, 어댑터 배치, 트랜잭션 책임, 저장·확장 전략 확정본을 기록한다.
- `fixed-{yyyymmdd}/harness-fixed.md`: CI/CD, release gate, operational readiness gate, observability gate, quality gate, AI 하네스와 정적 분석 도구의 Hard gate/Conditional gate/Advisory 분류를 기록한다.
- `fixed-{yyyymmdd}/*.html`: 이해를 돕는 Mermaid 다이어그램이 유용할 때만 추가한다. HTML은 문서 산출물이며 앱 런타임 의존성으로 만들지 않는다.
- `current-fixed.md`: 현재 적용 중인 확정본을 짧게 가리키는 포인터 문서로 유지한다. 최소한 `current_fixed: fixed-{yyyymmdd}`, `interview_source: interview-{yyyymmdd}`, `updated_at`, `scope`, `status`를 적는다.

## 실행 순서

1. 컨텍스트를 수집한다.
   - 기존 spec/prd/trd/websocket/architecture 문서, build 설정, src/main, src/test, CI/CD·인프라 설정 중 존재하는 파일만 읽는다.
   - 기존 `current-fixed.md`가 있으면 현재 적용 중인 fixed 디렉터리를 확인한다.
   - 기존 `architecture-review-ledger.md`가 있으면 리뷰 생략 가능 영역과 재검토 조건을 확인한다.

2. 인터뷰를 수행한다.
   - `architecture-interview` 방식으로 한 번에 하나의 질문만 한다.
   - 각 질문은 추천 답변, 추천 이유, 영향받는 문서, 상위 산출물 재검토 필요 여부를 포함한다.
   - 사용자가 "추천대로", "계속", "알아서"처럼 위임하면 추천 답변을 채택한다.
   - 충분한 답변이 모이면 파일 작성 전 요약을 제시하고 승인을 받는다.

3. 인터뷰 산출물을 기록한다.
   - 승인된 결정과 미확정 사항을 `interview-{yyyymmdd}/interview-log.md`에 기록한다.
   - 승인 범위 안에서 기존 `docs/architecture/*` 문서와 필요한 repo 설정을 갱신한다.

4. 리뷰를 수행한다.
   - `architecture-review` 방식으로 변경 영향 기반 리뷰를 수행한다.
   - 생략한 영역도 생략 사유와 재검토 조건을 남긴다.
   - 리뷰 결과를 세션에 제시하고, 문서·repo 설정 보완 전 사용자 승인을 받는다.

5. 리뷰 수정 루프를 판단한다.
   - 리뷰에서 수정할 사항이 없거나 Advisory 수준의 후속 작업만 남으면 확정 단계로 이동한다.
   - 리뷰에서 아키텍처 결정 수정이 필요하면 `architecture-interview` 질문 형식으로 다시 묻고, 승인된 수정만 반영한 뒤 `architecture-review`로 재리뷰한다.
   - 리뷰 기반 재결정 루프는 최대 3회만 허용한다. 루프 번호는 1부터 센다.
   - 3회 후에도 차단 이슈가 남으면 확정 완료로 말하지 않는다. 남은 이슈와 필요한 사용자 판단을 `final-summary.md`에 기록하고 멈춘다.

6. 확정본을 작성한다.
   - 모든 차단 이슈가 해소되면 `fixed-{yyyymmdd}/infra-fixed.md`, `impl-fixed.md`, `harness-fixed.md`를 작성하거나 갱신한다.
   - 각 문서에는 확정된 결정, 문서화 가정, 미확정 또는 상위 산출물 재검토 필요 항목, 후속 스킬 연계 항목을 구분한다.
   - 필요한 경우 Mermaid를 포함한 HTML 다이어그램을 같은 `fixed-{yyyymmdd}` 디렉터리에 둔다.
   - 기존 날짜의 fixed 디렉터리를 조용히 덮어쓰지 말고, 같은 날짜 워크플로의 승인된 갱신인지 확인한다.

7. 현재 포인터를 갱신한다.
   - 사용자 승인 후 `docs/architecture/current-fixed.md`에 현재 적용 중인 `fixed-{yyyymmdd}`를 기록한다.
   - 미해결 차단 이슈가 있으면 `status: partial` 또는 `status: blocked`로 표시하고, 확정본으로 오인될 표현을 피한다.
   - 차단 이슈가 없으면 `status: fixed`로 표시한다.

8. 아키텍처 산출물의 출처 상태를 기록한다.

```bash
python3 .codex/scripts/artifact-state.py record architecture \
  --input docs/spec/spec-fixed.md \
  --input docs/prd.md \
  --input docs/traceability.md \
  --output-glob 'docs/architecture/*.md' \
  --output-glob 'docs/architecture/fixed-*/*.md'
```

`docs/prd.md` 또는 `docs/traceability.md`가 아직 없는 경우에는 기록하지 않고, 다음 아키텍처 결정 전에 PRD 생성부터 요청한다.

## 리뷰 루프 기록 형식

각 `review-loop-{nn}.md`는 다음 구조를 유지한다.

```markdown
# Architecture Review Loop {nn}

## 리뷰 입력

- 기준 인터뷰: interview-{yyyymmdd}/interview-log.md
- 기준 문서:
- 기준 repo 설정:

## 리뷰 결과

- 검토 범위:
- 생략 범위와 사유:
- 핵심 이슈:
- 재결정 필요 항목:

## 재인터뷰 결정

- 질문:
- 추천 답변:
- 사용자 답변:
- 승인 여부:
- 반영 문서/설정:

## 재리뷰 결과

- 해소됨:
- 남은 이슈:
- 다음 조치:
```

## 확정 문서 작성 규칙

- `infra-fixed.md`, `impl-fixed.md`, `harness-fixed.md`는 현재 적용 가능한 확정 사항 중심으로 작성한다.
- 기존 `server-architecture.md`, `infrastructure-architecture.md`, `cicd-architecture.md`, `deployment-view.md`, `harness-guardrails.md`, `architecture-traceability.md`, `architecture-review-ledger.md`와 충돌하지 않게 갱신하거나, 충돌이 남으면 drift로 명시한다.
- 원천 문서에 없는 값은 임의 확정하지 않는다.
- 비용 큰 인프라 구성 요소(Redis, managed DB, CDN, Kubernetes, queue 등)는 확정되지 않았다면 MVP 확정 구성처럼 쓰지 않는다.
- CI에서 실패시킬 수 있는 하드 게이트와 보조·권고 도구를 구분한다.
- Mermaid HTML을 만들 때는 다이어그램이 어떤 결정을 설명하는지 상단에 짧게 적고, 원본 Markdown 문서에서 해당 HTML 파일을 링크한다.

## 완료 조건

- 인터뷰 로그가 존재한다.
- 리뷰 결과와 필요한 루프 기록이 존재한다.
- 차단 이슈가 없으면 세 fixed 문서와 `current-fixed.md`가 현재 확정본을 가리킨다.
- 차단 이슈가 남으면 `current-fixed.md`가 확정 상태를 과장하지 않고, `final-summary.md`가 남은 판단을 명확히 적는다.
- 가능하면 관련 검증 명령을 실행하고, 실행하지 못했으면 이유를 기록한다.

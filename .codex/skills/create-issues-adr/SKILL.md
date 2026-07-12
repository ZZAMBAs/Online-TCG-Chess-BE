---
name: create-issues-adr
description: docs/spec/spec-fixed.md와 존재하는 feature PRD/TRD, architecture 산출물, 필요 시 확정된 docs/contracts/{topic}.md를 기준으로 특정 {feature} 또는 전체 feature의 순차 의존성을 가진 수직 슬라이스 로컬 이슈, feature 단위 ADR, read-only 이슈 검증, GitHub Issue 연결을 한국어로 생성·갱신해야 할 때 사용한다. create-prd와 create-trd 이후 issue 분리, Given-When-Then AC, TDD 가능한 테스트 시나리오/테스트 관점 도출, depends_on 실행 게이트, REST/STOMP 계약 테스트 관점, ADR 대안 비교 표, docs/issue-map.md와 docs/adr-index.md 갱신, GitHub Issue 제목 접두어 [{feature}-{nnn}], .github/ISSUE_TEMPLATE/feature-implementation.md 적용, gh CLI 및 GitHub MCP/app connector fallback에 사용하며 spec/prd/trd 원문 수정, PRD/TRD 생성, 요구사항 인터뷰, 스펙 리뷰, issue template 작성은 하지 않는다.
---

# Create Issues ADR

## 개요

존재하는 feature PRD/TRD와 확정된 BE 구현 계약을 구현 가능한 수직 슬라이스 이슈로 분해하고, 각 이슈의 테스트 시나리오와 테스트 관점을 도출한다. 중요한 결정은 feature 단위 ADR로 남긴다. 로컬 이슈 ID는 `{feature}-{nnn}`이고 GitHub Issue 번호와 다르므로, 모든 상호 참조는 로컬 ID를 기준으로 유지한다.

## 기본 원칙

- 모든 질문, 분석, 문서, GitHub Issue 본문은 한국어로 작성한다.
- `docs/spec/*`, `docs/prd.md`, `docs/trd.md`, `docs/features/{feature}/prd.md`, `docs/features/{feature}/trd.md`는 입력 문서로만 취급하고 수정하지 않는다.
- PRD/TRD 파일이 없거나 `python3 .codex/scripts/artifact-state.py verify prd`, `verify architecture`, `verify trd`가 실패하면 이슈 생성을 멈추고 해당 산출물 생성 또는 갱신을 요청한다.
- `docs/contracts/*.md`가 있으면 이슈 생성 전에 `python3 .codex/scripts/artifact-state.py verify contracts`를 실행한다.
- 외부 REST/STOMP, 인증/CSRF/cookie, 오류 포맷, 상태 동기화, projection, fixture처럼 FE/BE 협상 대상인 계약은 `docs/contracts/{topic}.md`의 `implementation_status: ready` 내용을 이슈 AC와 테스트 관점에 반영한다.
- 기존 `docs/features/{feature}/issues/*`, `docs/features/{feature}/adr/*`, `docs/issue-map.md`, `docs/adr-index.md`가 있으면 먼저 읽고 중복 생성 대신 보완한다.
- 로컬 문서를 원천 추적 기준으로 삼는다. GitHub Issue 생성은 사용자가 명시적으로 요청하고 승인한 경우에만 수행한다.
- 이슈는 PRD 사용자 시나리오와 수용 기준을 구현 가능한 수직 슬라이스로 나눈다. 계층별 수평 작업만 나열하는 이슈는 만들지 않는다.
- 같은 feature의 이슈는 기본적으로 낮은 번호부터 순차 진행한다. 후속 이슈는 이전 이슈의 AC 충족과 테스트 통과를 전제로 작성한다.
- 각 수직 슬라이스 이슈는 TDD로 구현할 수 있어야 하며, 실패 테스트 작성에서 시작할 수 있을 만큼 AC와 테스트 관점을 구체화한다.
- 테스트 시나리오 생성 책임은 이 스킬에 있다. 단, 새 제품 요구사항이나 정책값을 발명하지 않고 PRD/TRD/contracts/architecture에서 도출 가능한 테스트 관점만 이슈에 기록한다.
- 이슈/ADR 초안은 확정 전에 read-only 검증을 통과해야 하며, 검증 에이전트는 원천 문서와 초안을 수정하지 않는다.
- ADR은 단순 결론 문서가 아니다. 현재 프로젝트 상황, 비교 대안, 선택 이유, 선택 결과를 꼼꼼히 기록한다.
- issue template 파일은 작성하지 않는다. GitHub Issue 본문에는 기존 `.github/ISSUE_TEMPLATE/feature-implementation.md`를 적용한다.

## 대상 범위

사용자가 `{feature}` 인자를 주면 해당 feature만 처리한다. 예를 들어 `$create-issues-adr matchmaking`처럼 요청하면 `docs/features/matchmaking/prd.md`와 `docs/features/matchmaking/trd.md`를 기준으로 이슈와 ADR을 생성한다.

인자가 없으면 전체 feature를 기준으로 후보를 탐색한다. 사용자의 문맥이 특정 feature를 가리키면 그 feature만 처리하고, 범위가 불명확하거나 너무 넓으면 `docs/features/*/prd.md`와 `trd.md`가 모두 있는 feature 목록을 제시해 처리 범위를 확정한다.

지정된 `{feature}`에 PRD/TRD가 없으면 유사한 feature 폴더를 추측해 진행하지 말고, 누락된 경로를 보고하고 중단한다.

## 입력 확인

우선 존재하는 문서만 읽는다.

- 공통 산출물: `docs/prd.md`, `docs/trd.md`, `docs/milestones.md`, `docs/traceability.md`, `docs/websocket-spec.md`
- 기능 산출물: `docs/features/{feature}/prd.md`, `docs/features/{feature}/trd.md`
- BE 구현 계약 산출물: `docs/contracts/*.md`
- 아키텍처 산출물: `docs/architecture/*`
- 기존 후속 산출물: `docs/features/{feature}/issues/*`, `docs/features/{feature}/adr/*`, `docs/issue-map.md`, `docs/adr-index.md`

## 진행 절차

1. `{feature}` 인자가 있는지 확인하고 처리 범위를 확정한다.
2. 입력 문서와 기존 후속 산출물을 읽는다.
3. 가능하면 `scripts/scan_issue_ids.py --root .`를 실행해 기존 로컬 이슈 ID, ADR ID, GitHub Issue 연결 중복을 확인한다.
4. feature별 사용자 시나리오, 서버 책임, 데이터/상태 경계, REST/STOMP 영향, 관련 `docs/contracts/{topic}.md`, 운영 요구, 테스트 가능성을 기준으로 이슈 후보를 도출한다.
5. ADR이 필요한 결정 후보를 별도로 도출한다.
6. 사용자에게 feature별 issue map, 순차 의존 관계, 병렬 가능 이슈, ADR 후보를 제시하고 확정받는다.
7. 확정된 범위에 따라 로컬 이슈 문서, ADR 문서, `docs/issue-map.md`, `docs/adr-index.md`를 생성하거나 갱신한다.
8. `.codex/agents/issue-verifier.md`와 `references/issue-verification-contract.md`를 읽고 대상 feature 이슈/ADR 초안을 read-only로 검증한다.
9. 검증 결과를 `docs/features/{feature}/issues/issue-verification.md`에 기록한다. `revision_required`이면 이슈/ADR 초안만 보완하고 한 번 더 검증한다. `blocked`이거나 두 번째 검증도 `revision_required`이면 사용자 결정 없이 확정하지 않는다.
10. 검증이 `passed`이면 이슈별 `verification_status`를 `passed`로 갱신하고, 이슈/ADR 초안을 요약해 사용자 확정을 받는다. 사용자 수정으로 초안이 바뀌면 출처 상태 기록 전에 검증을 다시 수행한다.
11. 아래 명령으로 생성한 이슈/ADR 산출물의 출처 상태를 기록한다.

```bash
python3 .codex/scripts/artifact-state.py record issues-{feature} \
  --input docs/spec/spec-fixed.md \
  --input docs/prd.md \
  --input docs/trd.md \
  --input docs/traceability.md \
  --input docs/features/{feature}/prd.md \
  --input docs/features/{feature}/trd.md \
  --input-glob 'docs/architecture/*.md' \
  --input-glob 'docs/architecture/fixed-*/*.md' \
  --optional-input-glob 'docs/contracts/*.md' \
  --output-glob 'docs/features/{feature}/issues/*/issue.md' \
  --output 'docs/features/{feature}/issues/issue-verification.md' \
  --optional-output-glob 'docs/features/{feature}/adr/*.md' \
  --output docs/issue-map.md \
  --output docs/adr-index.md
```

12. GitHub Issue 생성 요청이 있으면 `references/github-issue-policy.md`를 읽고 승인 게이트를 진행한다.
13. 최종적으로 생성/수정 파일, 검증 결과, GitHub Issue 연결 여부, 남은 미확정 사항을 보고한다.

## 이슈 작성 규칙

자세한 형식은 `references/issue-template.md`를 읽고 따른다.

- 로컬 이슈 디렉터리는 `docs/features/{feature}/issues/{feature}-{nnn}-{slug}/` 형식으로 작성하고, 본문은 그 안의 `issue.md`에 작성한다.
- 로컬 이슈 ID는 `{feature}-{nnn}`이고, 디렉터리명 slug는 내용을 설명하는 소문자 hyphen-case 영문으로 작성한다.
- `{feature}`는 기존 feature 디렉터리명을 그대로 사용한다.
- `{nnn}`은 feature별 001부터 시작하고, 기존 번호가 있으면 다음 번호를 사용한다.
- 같은 feature의 `{nnn}`은 실행 순서를 의미한다. 병렬 가능 또는 독립 이슈가 아니라면 후속 번호 이슈는 이전 번호 이슈를 선행 조건으로 둔다.
- 각 이슈는 사용자에게 관찰 가능한 가치 또는 시스템 행위가 끝까지 연결되는 수직 슬라이스로 나눈다.
- 계층별 수평 이슈, 예를 들어 "엔티티만 작성", "Repository만 작성", "Controller만 작성" 같은 단독 이슈는 피한다. 다만 마이그레이션, 하네스, 공통 인프라처럼 독립 선행 작업이 불가피하면 별도 이슈로 만들고 의존 관계를 명시한다.
- 각 이슈의 `depends_on`은 참고 링크가 아니라 TDD 시작 전 실행 게이트다. 선행 이슈가 있으면 선행 이슈의 AC 충족, 테스트 통과, 후속 이슈가 기대하는 구현 surface를 명시한다.
- 병렬 가능한 이슈만 `depends_on: []`으로 두고 본문 `## 의존 관계`에 독립 또는 병렬 가능 사유를 적는다.
- 각 이슈에는 PRD의 관련 사용자 시나리오를 인용 또는 요약하고, 그 시나리오에서 AC를 도출한다.
- 관련 `docs/contracts/{topic}.md`가 있으면 이슈 frontmatter와 `## 관련 문서`에 연결하고, BE가 지켜야 할 결정, REST/STOMP 계약, 인증/보안/노출 제한, 상태 동기화, 오류 포맷, fixture/drift 검증을 AC 또는 테스트 관점에 반영한다.
- 관련 계약 문서가 필요하지만 없거나 `implementation_status: ready`가 아니면 구현 가능한 이슈처럼 확정하지 말고 미확정 사항 또는 선행 계약 동기화 작업으로 남긴다.
- AC는 Given-When-Then 형식으로 작성하고 각 항목 앞에 `[정상]`, `[경계]`, `[예외]` 중 하나를 붙인다.
- 정상 상황뿐 아니라 경계 조건과 예외 상황을 반드시 포함한다. PRD/TRD에 근거가 부족하면 "미확정 사항"으로 표시하고 사용자 확인이 필요하다고 적는다.
- 각 이슈에는 `## 테스트 시나리오`를 작성해 `$tdd-red`가 새 시나리오를 만들지 않고 바로 테스트 코드로 옮길 수 있게 한다. 각 테스트 시나리오는 연결 AC, 테스트 종류, given/when/then, 관찰·검증할 결과, 필요한 fixture/하네스/계약 문서를 포함한다.
- 각 이슈에는 TDD 진행 순서를 포함한다. 먼저 실패해야 할 테스트를 쓰고, 최소 구현, 리팩터링, 하네스/정적 분석 검증 순으로 적는다.
- `verification_status: passed`가 아닌 이슈는 TDD 시작 가능한 이슈로 취급하지 않는다.
- REST/STOMP가 사용자 또는 외부 호출자에게 보이는 결과이면 단위 테스트뿐 아니라 계약/API 테스트 관점을 포함한다. 하네스가 아직 없으면 기능 이슈에 묻지 말고 하네스 선행 작업 또는 `미확정 사항`으로 분리한다.
- 수용 기준과 테스트는 PRD/TRD의 요구사항과 연결될 만큼 구체적으로 작성한다.

## ADR 작성 규칙

자세한 형식은 `references/adr-template.md`를 읽고 따른다.

- ADR 파일은 `docs/features/{feature}/adr/adr-{nnn}-{slug}.md` 형식으로 작성한다.
- ADR 상태는 YAML frontmatter의 `status`에 둔다.
- ADR 본문은 반드시 4개 섹션만 기본 구조로 유지한다.
  - `Context`
  - `Decision`
  - `Alternatives`
  - `Consequences`
- `Alternatives`는 표 형식으로 작성하고, 대안별 장점, 단점/위험, 현재 프로젝트 상황에서의 적합성, 선택 또는 제외 이유를 적는다.
- `Decision`에는 선택된 대안이 현재 요구사항, 기존 코드, 아키텍처 문서, 비용, 운영 부담, 구현 범위, 테스트 가능성과 어떻게 맞물리는지 설명한다.
- 선택되지 않은 대안도 충분히 검토한다. "복잡함", "불필요함" 같은 단정만 쓰지 말고 현재 상황과 연결된 이유를 적는다.
- ADR이 필요하지 않은 단순 구현 판단은 이슈의 구현 메모에 남기고 ADR로 승격하지 않는다.

## GitHub Issue 연결

GitHub Issue 연결을 요청받으면 `references/github-issue-policy.md`를 읽고 따른다.

- GitHub Issue 생성 또는 갱신은 사용자가 명시적으로 요청하고 승인한 경우에만 수행한다.
- GitHub Issue 제목은 `[{feature}-{nnn}] {title}` 형식을 사용한다.
- `.github/ISSUE_TEMPLATE/feature-implementation.md`가 있으면 GitHub Issue 본문 구조로 적용한다.
- template 파일이 없으면 GitHub Issue 생성을 중단하고 로컬 문서만 생성·갱신한다.
- GitHub 연결은 `gh` CLI를 먼저 시도하고, 실패하면 GitHub MCP/app connector를 탐색해 시도한다.
- `gh` CLI와 GitHub MCP/app connector가 모두 실패하거나 사용할 수 없으면 GitHub Issue 생성은 건너뛰고 로컬-only 상태로 보고한다.
- 생성 후 로컬 이슈 frontmatter와 `docs/issue-map.md`에 GitHub Issue 번호와 URL을 기록한다.

## 중복 검사

- 문서 생성 전후에 가능하면 `scripts/scan_issue_ids.py`를 실행해 로컬 이슈 ID, ADR ID, GitHub Issue 연결 중복을 검사한다.
- 이 스크립트는 읽기 전용이어야 하며, 결과가 실패면 중복 원인을 먼저 보고하고 문서 생성 또는 연결을 보류한다.
- 스크립트가 감지하지 못하는 새 디렉터리명 규칙이나 frontmatter 누락이 의심되면 이슈 디렉터리명, `issue.md`, 본문 제목을 직접 확인한다.

## Read-only 이슈 검증

상세 절차와 판정 처리는 `references/issue-verification-contract.md`를 따른다.

- 검증 에이전트를 사용할 수 없으면 독립 검증을 수행했다고 주장하지 않고 이슈 확정을 중단한다.
- 검증은 이슈별 출처, AC, 테스트, 계약 상태, 의존 관계, ADR 경계를 확인한다.
- 검증 보고서는 대상 feature의 `issues/issue-verification.md`에 최신 결과만 유지한다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 생성 또는 수정한 이슈 문서 목록
- 생성 또는 수정한 ADR 문서 목록
- `docs/issue-map.md`, `docs/adr-index.md` 갱신 여부
- GitHub Issue 연결 여부와 사용한 경로: `gh`, GitHub MCP/app connector, 또는 local-only
- 남은 미확정 사항 또는 사용자의 승인이 필요한 항목

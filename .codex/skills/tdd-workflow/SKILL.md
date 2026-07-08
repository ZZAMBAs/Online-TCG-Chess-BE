---
name: tdd-workflow
description: Online-TCG-Chess-BE의 로컬 feature 이슈를 대상으로 TDD 전체 흐름을 오케스트레이션해야 할 때 사용한다. 인자로 auth-1, auth-001, auth-issues-1, xxx-yyy-1처럼 마지막 토큰이 숫자인 이슈 식별자를 받아 tdd-red, tdd-green, tdd-blue, security-review를 순서대로 실행하고, 마지막에는 .codex/agents/ac-verifier.md 기반 서브에이전트로 AC 충족 여부를 독립 검증한다. 요구사항과 기존 테스트는 수정하지 않으며, 위험 지점은 사용자 게이트로 멈추고, AC 검증 실패 시 RED부터 재진입하되 총 AC 검증 횟수는 3회로 제한한다.
---

# TDD Workflow

## 개요

로컬 feature 이슈 하나를 RED, GREEN, BLUE, 보안 검토, AC 독립 검증까지 끝까지 진행한다. 이 스킬은 하위 스킬을 대신 구현하지 않고, 각 단계 스킬의 계약을 읽어 순서, 게이트, 중단 조건, 재시도 횟수를 관리하는 오케스트레이터다.

## 입력 규칙

- 모든 질문, 분석, 보고는 한국어로 작성한다.
- 사용자는 하위 TDD 스킬들이 받는 것과 같은 이슈 식별자 하나를 인자로 제공해야 한다.
- 인자 형식과 이슈 디렉터리 해석은 하위 스킬의 입력 규칙을 반복하지 않고 `scripts/find_issue.py`로 검증한다.
- 이슈를 정확히 하나로 찾을 수 없으면 하위 단계를 실행하지 않고 형식 오류 또는 `workflow-blocked`로 종료한다.

```bash
python3 .codex/skills/tdd-workflow/scripts/find_issue.py auth-1 --root .
```

## 읽을 문서

오케스트레이션에 필요한 문서만 직접 읽고, 단계별 세부 문서와 변경 규칙은 각 하위 스킬 계약에 위임한다.

1. `scripts/find_issue.py`가 찾은 `issue.md`
2. 현재 이슈의 `## Acceptance Criteria`
3. 하위 단계 계약인 `.codex/skills/tdd-red/SKILL.md`
4. 하위 단계 계약인 `.codex/skills/tdd-green/SKILL.md`
5. 하위 단계 계약인 `.codex/skills/tdd-blue/SKILL.md`
6. 하위 단계 계약인 `.codex/skills/security-review/SKILL.md`
7. AC 검증 에이전트인 `.codex/agents/ac-verifier.md`
8. 워크플로우 로그 계약인 `references/workflow-log-contract.md`

하위 스킬이 요구하는 문서나 선행 이슈 검증은 해당 스킬 실행 시 그 스킬의 계약을 따른다. 워크플로우 차원의 필수 문서가 없거나 서로 충돌하면 추측하지 말고 사용자 게이트로 멈춘다.

## 워크플로우 제한

이 제한은 하위 스킬 계약 위에 추가로 적용한다.

- 요구사항 원천 문서, PRD, TRD, architecture, issue AC를 수정하지 않는다.
- 기존 테스트 파일을 수정하지 않는다.
- 하위 스킬이 테스트 보정이나 기존 테스트 수정을 허용하더라도 `tdd-workflow` 실행 중에는 적용하지 않는다.
- 사용자가 직접 승인해야 하는 위험 지점에서는 자동 진행하지 않는다.

## 사용자 게이트

다음 경우는 AI가 자동 진행하지 않고 `workflow-user-gated`로 멈춘다.

- 요구사항, AC, PRD/TRD, architecture 문서가 서로 충돌하거나 해석이 필요한 경우
- 외부 REST/STOMP 계약이 FE 제안, BE 검토, 사용자 승인, freeze를 거치지 않은 경우
- 기존 테스트를 수정해야만 진행 가능한 경우
- 요구사항 문서 수정이 필요해 보이는 경우
- 새 보안 도구, Gradle 설정, CI 설정 도입이 필요한 경우
- AC verifier가 구현 문제가 아니라 요구사항, 테스트, 계약 자체의 불일치를 지적한 경우
- 하위 스킬의 차단 사유가 사용자 의사결정 없이는 해소될 수 없는 경우

사용자 게이트로 멈출 때는 `tdd-workflow.md`에 이유, 필요한 결정, 자동 진행하지 않은 근거를 기록한다.

## 단계 순서

워크플로우는 항상 아래 순서로 진행한다.

1. `$tdd-red {issue-id}`
2. `$tdd-green {issue-id}`
3. `$tdd-blue {issue-id}`
4. `$security-review {issue-id}`
5. `.codex/agents/ac-verifier.md` 기반 서브에이전트 AC 검증

각 단계 전 해당 스킬 또는 에이전트 정의를 읽고 현재 워크플로우 제한과 충돌하지 않는 범위에서 따른다.

## 단계 게이트

- RED 결과가 `blocked`이면 다음 단계로 가지 않고 `workflow-blocked` 또는 `workflow-user-gated`로 멈춘다.
- RED 결과의 `red-fail`, `compile-blocked`, `already-green`은 GREEN 진입 가능 상태로 본다.
- GREEN 결과가 `green-pass`가 아니면 BLUE로 가지 않고 `workflow-blocked` 또는 `workflow-failed`로 멈춘다.
- BLUE 결과가 `blue-pass` 또는 `blue-noop`가 아니면 security-review로 가지 않고 멈춘다.
- security-review 결과가 `security-pass` 또는 `security-low-only`가 아니면 AC verifier로 가지 않고 멈춘다.
- AC verifier 결과가 전체 통과이면 `workflow-pass`로 완료한다.
- AC verifier 결과에 `부분 충족`, `미충족`, `검증 불가`가 있으면 사유를 기록하고 RED부터 재진입한다.

## AC 검증 반복 제한

- AC verifier 실행은 총 3회까지만 허용한다.
- 1회차는 최초 검증이고, 2회차와 3회차는 재시도다.
- 1회차 또는 2회차에서 실패하면 `tdd-workflow.md`에 AC 갭과 재진입 사유를 기록하고 RED부터 전체 흐름을 다시 진행한다.
- 3회차에서도 AC가 전체 통과하지 못하면 더 반복하지 않고 `workflow-ac-retry-exhausted`로 중단한다.
- 반복마다 같은 결론을 맹목적으로 재사용하지 말고 새 RED/GREEN/BLUE/security 산출물과 현재 코드를 다시 확인한다.

## 서브에이전트 AC 검증

AC 검증은 메인 에이전트가 직접 결론내리지 않고 서브에이전트에 위임한다. 서브에이전트에는 `.codex/agents/ac-verifier.md`를 전달하고, production/test/document 파일을 수정하지 말라고 명시한다.

서브에이전트 프롬프트는 다음 구조를 따른다.

```text
Use the AC verifier agent definition at .codex/agents/ac-verifier.md to verify {issue-id}.
Do not edit files. Read the local issue, RED/GREEN results, refactor-log.md, security-review.md, related spec/PRD/TRD/architecture docs, tests, and implementation.
Return whether every Acceptance Criteria is satisfied. Classify each AC as 충족, 부분 충족, 미충족, or 검증 불가, and include file-based evidence.
```

메인 에이전트는 서브에이전트 응답에서 전체 상태, 차단 AC, 추가 테스트 제안, 구현/문서 갭을 추출해 `tdd-workflow.md`에 반영한다.

## 워크플로우 로그

현재 이슈 디렉터리의 `tdd-workflow.md`를 만들거나 갱신한다. `references/workflow-log-contract.md`를 읽고 그 계약의 항목과 상태 의미를 따른다.

- 실행 이력을 길게 누적하지 말고 최신 스냅샷으로 덮어쓴다.
- AC 검증 재시도 사유는 현재 스냅샷에 회차별로 남긴다.
- 사용자 게이트, 차단, 실패, 재시도 소진 상태는 사용자가 다음 행동을 결정할 수 있도록 구체적으로 기록한다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 사용한 이슈 문서
- 최종 워크플로우 상태
- RED/GREEN/BLUE/security-review 상태
- AC verifier 실행 횟수와 최종 판정
- 수정한 production/resource 파일과 새로 만든 테스트 파일
- 요구사항 또는 기존 테스트를 수정하지 않았는지 여부
- 사용자 게이트 또는 재시도 소진이 있으면 필요한 사용자 결정
- 실행한 테스트와 보안/정적 분석 명령

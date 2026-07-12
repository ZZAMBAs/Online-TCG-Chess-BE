# Issue Verification Contract

`$create-issues-adr`는 이슈/ADR 초안을 만든 뒤 `.codex/agents/issue-verifier.md`를 사용해 read-only 검증을 수행한다.

## 실행 규칙

- 검증 에이전트에는 원천 문서와 대상 feature 초안만 전달한다.
- 검증 에이전트는 파일을 수정하지 않는다.
- 결과는 `docs/features/{feature}/issues/issue-verification.md`에 기록한다.
- 이슈별 frontmatter의 `verification_status`는 `pending`, `passed`, `blocked` 중 하나로 유지한다.

## 판정 처리

- `passed`: 모든 이슈 frontmatter를 `passed`로 갱신하고 사용자 확정 단계로 진행한다.
- `revision_required`: 메인 에이전트가 이슈/ADR 초안만 보완한 뒤 검증을 한 번 더 수행한다.
- `blocked`: 원천 요구사항, 계약, 아키텍처 또는 사용자 판단이 필요한 이유를 기록하고 이슈 확정을 멈춘다.
- 두 번째 검증에서도 `revision_required`이면 자동 반복하지 않고 사용자에게 남은 쟁점을 보고한다.

## 금지 사항

- 검증 결과만으로 spec, PRD, TRD, architecture, 계약 원문을 수정하지 않는다.
- 검증 에이전트가 제안한 새 정책값이나 인터페이스를 근거 없이 이슈에 반영하지 않는다.
- `blocked` 또는 `pending` 이슈를 TDD 시작 가능 상태로 보고하지 않는다.

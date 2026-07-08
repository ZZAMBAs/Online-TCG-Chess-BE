# Workflow Log Contract

`tdd-workflow`는 현재 이슈 디렉터리의 `tdd-workflow.md`에 전체 TDD 워크플로우 결과를 기록한다. 모든 설명은 한국어로 쓴다.

## 상태

- `workflow-pass`: RED, GREEN, BLUE, security-review, AC verifier가 모두 완료되었고 전체 AC가 충족되었다.
- `workflow-blocked`: 환경 문제, 선행 이슈 미완료, 필수 문서 부재, 대상 파일 불명확 등으로 자동 진행할 수 없다.
- `workflow-failed`: 허용 범위 안에서 RED/GREEN/BLUE/security 단계 또는 AC 갭 해소에 실패했다.
- `workflow-ac-retry-exhausted`: AC verifier 총 3회 실행 후에도 전체 AC를 충족하지 못했다.
- `workflow-user-gated`: 사용자 직접 검토 또는 승인이 필요한 위험 지점이 있어 자동 진행을 멈췄다.

## 기록 규칙

- 실행 이력을 장황하게 누적하지 말고 최신 스냅샷으로 덮어쓴다.
- 각 단계의 세부 결과는 해당 단계 산출물에 두고, 이 파일에는 전체 흐름과 중단 판단만 요약한다.
- AC verifier는 총 3회까지만 기록한다.
- 사용자 게이트는 필요한 결정과 자동 진행하지 않은 이유를 반드시 적는다.
- 요구사항 문서와 기존 테스트 파일 수정 여부를 명시한다.

## 필드

- 대상 이슈
- 상태
- 이슈 문서
- 워크플로우 시작 조건
- 사용자 게이트 여부
- 사용자 게이트 사유
- RED 상태와 산출물
- GREEN 상태와 산출물
- BLUE 상태와 산출물
- security-review 상태와 산출물
- AC verifier 실행 횟수
- AC verifier 최종 판정
- AC 검증 재시도 요약
- 새로 만든 테스트 파일
- 수정한 production/resource 파일
- 요구사항 문서 수정 여부
- 기존 테스트 수정 여부
- 실행한 테스트 명령
- 실행한 보안/정적 분석 명령
- 차단 또는 실패 요약
- 다음 사용자 결정 또는 후속 작업

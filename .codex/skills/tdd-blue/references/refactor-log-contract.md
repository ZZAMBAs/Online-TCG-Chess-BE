# Refactor Log Contract

`tdd-blue`는 현재 이슈 디렉터리의 `refactor-log.md`에 BLUE 결과를 기록한다. 모든 설명은 한국어로 쓴다.

## 상태

- `blue-pass`: 리팩터링을 수행했고 baseline 및 회귀 테스트가 통과했다.
- `blue-noop`: 리팩터링 후보를 검토했지만 수정할 부분이 없어 production 파일을 변경하지 않았다.
- `blue-blocked`: baseline 실패, GREEN 결과 부재, 대상 파일 불명확, 아키텍처/계약 미확정, 환경 문제 등으로 BLUE를 시작하거나 검증할 수 없다.
- `blue-failed`: 최대 3회 리팩터링 시도 후에도 회귀 테스트를 통과하지 못해 중단했다.

## 기록 규칙

- `blue-pass`, `blue-noop`, `blue-blocked`는 최신 스냅샷으로 덮어쓴다.
- `blue-failed`는 실패한 시도 내역을 누적 가능하게 기록한다.
- 실패 시도에는 시도 번호, 변경 요약, 실패한 명령, 실패 요약, rollback 여부를 남긴다.

## 필드

- 대상 이슈
- 상태
- 리팩터링 대상 파일
- 변경한 production 파일
- 수행한 리팩터링 요약
- 실행한 baseline 테스트 명령
- 실행한 회귀 테스트 명령
- 실패 또는 차단 요약
- rollback 여부
- 남은 리팩터링 후보

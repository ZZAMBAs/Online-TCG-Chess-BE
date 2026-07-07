# GREEN Result Contract

`tdd-green`은 현재 이슈 문서의 `## TDD GREEN 결과` 섹션에 최신 GREEN 단계 요약만 기록한다. 실행 이력을 누적하지 말고 기존 섹션을 현재 스냅샷으로 갱신한다. 일반 확인용 재실행, CI 재실행, BLUE 이후 회귀 테스트 로그는 이슈 문서에 누적하지 않는다. 모든 설명은 한국어로 쓴다.

- 통과시킨 테스트 파일과 메서드
- 생성 또는 수정한 production 파일
- 보정한 test/resource 파일
- 상태: `green-pass`, `test-invalid`, `blocked`, `green-failed`
- 실행한 명령
- 실패 또는 차단 요약: 설명이 필요 없으면 `없음`으로 기록한다.
- 남은 실패 또는 후속 BLUE 후보

## 상태 의미

- `green-pass`: 대상 RED 테스트가 통과했다. 최소 production 구현 후 통과했는지, production 변경 전부터 통과했는지는 변경 파일과 실패 또는 차단 요약에 기록한다.
- `test-invalid`: RED 테스트가 AC, PRD/TRD, 아키텍처 문서와 맞지 않아 production을 억지로 맞추면 안 된다.
- `blocked`: 선행 이슈 미완료, 아키텍처 문서 부재/미확정, 계약 미확정, 구현 대상 불명확, 하네스 부재, 외부 환경 문제 등으로 production 구현 또는 검증을 진행할 수 없다.
- `green-failed`: GREEN을 시도했지만 허용 범위 안에서 대상 테스트를 통과시키지 못했고 다른 차단 분류에 속하지 않는다.

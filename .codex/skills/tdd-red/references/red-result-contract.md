# RED Result Contract

`tdd-red`는 현재 이슈 문서의 `## TDD RED 결과` 섹션에 최신 RED 단계 요약만 기록한다. 실행 이력을 누적하지 말고 기존 섹션을 현재 스냅샷으로 갱신한다. 모든 설명은 한국어로 쓴다.

- 테스트 파일
- 테스트 메서드와 연결 AC
- 상태: `red-fail`, `compile-blocked`, `already-green`, `blocked`
- 실행한 명령
- 실패 또는 차단 요약: 설명이 필요 없으면 `없음`으로 기록한다.

## 상태 의미

- `red-fail`: 테스트가 AC를 검증하고, production 구현 부족 때문에 기대한 RED 실패가 발생했다.
- `compile-blocked`: production type, method, package skeleton이 없어 테스트 컴파일이 막혔다. RED는 production을 만들지 않는다.
- `already-green`: 기존 구현으로 테스트가 이미 통과했다. 테스트가 실제 AC를 검증하는지 재확인해야 한다.
- `blocked`: 선행 이슈 미완료, 요구사항/패키지/테스트 대상 불명확, 계약 미확정, 하네스 부재 등으로 RED를 진행할 수 없다.

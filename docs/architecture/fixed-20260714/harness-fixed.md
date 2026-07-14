# Harness Architecture Fixed

## 확정된 결정

### Hard Gate

- `fixed-20260710/harness-fixed.md`의 `./gradlew spotlessCheck test`, Spotless, ArchUnit과 GitHub Actions required check를 유지한다.
- 카드 catalog 검증 task가 구현되는 즉시 구조, 식별자·버전 중복, 활성 버전 참조와 같은 버전 불변성 검증을 Hard gate로 전환한다.
- fixed FE/BE 카드 계약과 effect registry가 구현되는 즉시 활성화·롤백 가능한 모든 버전의 정의·효과 처리·선택·공개 결과·fixture 완결성 검증을 Hard gate로 전환한다.

### Conditional Gate

- 카드 persistence 구현 시 Testcontainers MySQL로 새 버전 추가, 같은 버전 충돌 시 기동 실패, 활성 버전 전환과 경기별 버전 고정을 검증한다.
- 기존 PMD, SpotBugs/FindSecBugs, JaCoCo, dependency locking/verification, Spring Security Test와 OpenAPI/STOMP contract test의 Conditional 분류를 유지한다.

### Advisory

- 오래된 비활성 카드 버전의 재활성화 필요성과 효과 처리 보존 범위를 릴리즈마다 검토한다.
- catalog 동기화 실패와 활성 버전 롤백 절차는 CD 확정 시 release readiness gate로 승격한다.

## 문서화 가정

- 현재는 기능 구현 전이므로 새 Gradle task, Testcontainers와 production 동기화 코드를 이번 결정에서 추가하지 않는다.
- 하네스 구현 시 기존 `spotlessCheck test` required check에 통합한다.

## 미확정 또는 상위 산출물 재검토

- 카드 catalog validator와 effect registry의 상세 구현
- fixed 계약 fixture의 FE 공유 방식
- provider/CD 기반 배포·rollback·post-deploy gate

## 후속 스킬 연계

- `negotiate-fe-be-contract`: fixed schema와 fixture 확정
- `create-trd`: 검증 task와 통합 테스트 경계 설계
- `tdd-workflow`: 이슈별 gate 활성화

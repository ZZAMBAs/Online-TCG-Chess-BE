# Harness Architecture Fixed

## 확정된 결정

### Hard Gate

- `./gradlew spotlessCheck test`
- Spotless Java format과 Gradle whitespace/newline 검사
- ArchUnit module/hexagonal dependency rule
- GitHub Actions PR 및 `master` push CI
- JUnit XML과 HTML test report artifact 보존

### Conditional Gate

- Spring Security Test: security 관련 test가 생기는 즉시 필수
- Testcontainers MySQL: Flyway/JPA/transaction 통합 test 도입 시
- PMD: production code와 rule set 확정 시
- SpotBugs/FindSecBugs: 인증·세션·권한 production code 도입 시
- JaCoCo: 핵심 모듈 coverage 기준 승인 시
- dependency locking/verification: 외부 의존성 고정 필요 시
- REST OpenAPI/STOMP schema fixture contract test: FE/BE 합의 시
- Actuator/Prometheus endpoint 접근 경계 검증: 운영 설정 도입 시

### Advisory

- SLO, alert threshold, dashboard, flaky test trend
- analytics read model 재집계 운영

## 문서화 가정

- ArchUnit rule은 기능 모듈 생성 전에는 빈 package를 허용하고, 생성 후 즉시 해당 package를 검증한다.

## 미확정 또는 상위 산출물 재검토

- PMD/SpotBugs/JaCoCo의 상세 기준
- contract fixture와 FE workflow
- operational readiness/observability gate의 provider별 구현

## 후속 스킬 연계

- security 관련 production 변경 뒤 `security-review`
- provider/CD/분산 전환 뒤 `architecture-decision`

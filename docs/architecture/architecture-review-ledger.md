# Architecture Review Ledger

## 목적

아키텍처 영역별 검토 기준, fingerprint, 재검토 조건을 기록한다.

## 리뷰 영역 요약

| area | last_reviewed_at | decision_summary | skipped_this_run | skip_reason |
| --- | --- | --- | --- | --- |
| server-architecture-style | 2026-07-10 | 모듈러 모놀리스 + 헥사고날 | false | 최초 및 재리뷰 |
| project-package-structure | 2026-07-10 | 기능 우선 8개 모듈 | false | 최초 및 재리뷰 |
| module-boundaries | 2026-07-10 | application port와 ArchUnit 강제 | false | ArchUnit test 반영 |
| adapter-placement | 2026-07-10 | 모듈 내부 inbound/outbound | false | 최초 및 재리뷰 |
| cloud-hosting | 2026-07-10 | 제공자 미확정 | false | 최초 및 재리뷰 |
| compute-deployment-unit | 2026-07-10 | 단일 인스턴스, 실행 JAR | false | 최초 및 재리뷰 |
| network-tls-cdn | 2026-07-10 | same-origin reverse proxy, CDN 없음 | false | 최초 및 재리뷰 |
| data-cache-messaging-storage | 2026-07-10 | MySQL/JPA/Flyway, Redis 없음 | false | Flyway 의존성 반영 |
| security-secret-boundary | 2026-07-10 | Security session, profile/env secret | false | Security 의존성 반영 |
| operations-observability-infra | 2026-07-10 | Actuator/Prometheus/log, platform 미확정 | false | 최초 및 재리뷰 |
| cicd | 2026-07-10 | GitHub Actions CI, CD 보류 | false | workflow 반영 |
| harness-guardrails | 2026-07-10 | ArchUnit/Spotless Hard, 나머지 Conditional | false | Hard gate 반영 |
| scalability-transition | 2026-07-10 | 정성적 trigger 후 재인터뷰 | false | 최초 및 재리뷰 |

## 영역별 상세

### server-architecture-style

- last_reviewed_at: 2026-07-10
- source_documents: `docs/spec/spec-fixed.md`, `docs/prd.md`, `docs/features/*/prd.md`
- source_fingerprint: 최초 baseline, 후속 review에서 계산
- implementation_paths: `src/main/java`, `build.gradle`
- implementation_fingerprint: Spring Boot skeleton baseline
- decision_summary: 기능 우선 모듈러 모놀리스와 헥사고날 의존성 방향
- skip_conditions: PRD 기능 경계, Java/Spring 의존성, 모듈 package가 변하지 않음
- re_review_triggers: 기능 모듈 추가/병합, Gradle 멀티모듈 전환, framework 의존성 변경
- latest_result: 초기 ArchUnit test와 Hard gate를 반영했고 `./gradlew spotlessCheck test` 통과

### data-cache-messaging-storage

- last_reviewed_at: 2026-07-10
- source_documents: `docs/spec/spec-fixed.md`, `docs/features/gameplay/prd.md`, `docs/features/match-history/prd.md`
- source_fingerprint: 최초 baseline, 후속 review에서 계산
- implementation_paths: `build.gradle`, `src/main`, `src/main/resources`
- implementation_fingerprint: JPA/MySQL/Flyway/Security dependency 선언, 구현 없음
- decision_summary: MySQL/JPA/Flyway, GameEvent/Snapshot, 메모리 활성 경기, Redis/queue 미도입
- skip_conditions: 단일 인스턴스·단일 writer·저장 요구와 관련 의존성이 변하지 않음
- re_review_triggers: Redis/queue/NoSQL/Testcontainers/Flyway 도입, 다중 인스턴스, active-game 복구 요구, analytics storage 변경
- latest_result: analytics 요구가 spec과 관련 PRD에 동기화됨. provider와 backup 세부는 미확정

### harness-guardrails

- last_reviewed_at: 2026-07-10
- source_documents: `docs/architecture/harness-guardrails.md`, `build.gradle`, `.githooks/*`
- source_fingerprint: 최초 baseline, 후속 review에서 계산
- implementation_paths: `build.gradle`, `src/test`, `.github/workflows`
- implementation_fingerprint: ArchUnit test, Spotless, GitHub Actions CI, 실행 가능한 Gradle wrapper 반영
- decision_summary: ArchUnit/Spotless Hard, PMD/SpotBugs/JaCoCo/dependency verification/Testcontainers/contract test Conditional
- skip_conditions: tool 설정과 CI workflow가 변하지 않음
- re_review_triggers: Gradle plugin/dependency, CI workflow, security code, persistence integration test, FE/BE contract 추가
- latest_result: `./gradlew spotlessCheck test`와 CI workflow로 Hard gate 반영 완료

### cloud-hosting

- last_reviewed_at: 2026-07-10
- source_documents: `docs/spec/spec-fixed.md`, `docs/architecture/infrastructure-architecture.md`
- source_fingerprint: 최초 baseline, 후속 review에서 계산
- implementation_paths: `Dockerfile`, `infra`, `deploy`, `k8s`, `.github/workflows`
- implementation_fingerprint: 배포 설정 없음
- decision_summary: provider, compute, CD, backup detail 미확정
- skip_conditions: 제공자와 배포 설정이 없음
- re_review_triggers: cloud provider, compute, registry, Secret Manager, RPO/RTO, SLO, cost/trafﬁc target 확정
- latest_result: 재인터뷰 대기

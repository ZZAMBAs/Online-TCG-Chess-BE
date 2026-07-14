# Architecture Review Ledger

## 목적

아키텍처 영역별 검토 기준, fingerprint, 재검토 조건을 기록한다.

## 리뷰 영역 요약

| area | last_reviewed_at | decision_summary | skipped_this_run | skip_reason |
| --- | --- | --- | --- | --- |
| server-architecture-style | 2026-07-10 | 모듈러 모놀리스 + 헥사고날 | true | 스타일·기술 스택 입력 변화 없음 |
| project-package-structure | 2026-07-10 | 기능 우선 8개 모듈 | true | 기능 모듈 목록과 물리 구조 변화 없음 |
| module-boundaries | 2026-07-14 | cardcollection 공개 port로 카드·팩 catalog 동기화와 활성 조회 제공 | false | 카드팩 catalog 책임 경계 추가 검토 |
| adapter-placement | 2026-07-10 | 모듈 내부 inbound/outbound | true | adapter 배치 원칙 변화 없음 |
| cloud-hosting | 2026-07-10 | 제공자 미확정 | true | 제공자 입력·설정 변화 없음 |
| compute-deployment-unit | 2026-07-10 | 단일 인스턴스, 실행 JAR | true | 배포 단위 변화 없음 |
| network-tls-cdn | 2026-07-10 | same-origin reverse proxy, CDN 없음 | true | 네트워크 입력 변화 없음 |
| data-cache-messaging-storage | 2026-07-14 | docs/cards·docs/card-packs 작성 원천, RDB 불변 버전·활성 버전 실행 원천 | false | 기존 미확정 카드팩 저장 방식 확정 |
| security-secret-boundary | 2026-07-10 | Security session, profile/env secret | true | 보안·secret 정책 변화 없음 |
| operations-observability-infra | 2026-07-10 | Actuator/Prometheus/log, platform 미확정 | true | 관측 요구·설정 변화 없음 |
| cicd | 2026-07-14 | 카드·카드팩 catalog와 effect 완결성 required check 조건 확정 | false | 카드팩 배포 검증 경계 추가 |
| harness-guardrails | 2026-07-14 | 카드·카드팩 catalog·effect·RDB 동기화 gate 추가 | false | 카드팩 검증 gate 분류 |
| scalability-transition | 2026-07-10 | 정성적 trigger 후 재인터뷰 | true | 분산·확장 요구 변화 없음 |

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

- last_reviewed_at: 2026-07-14
- source_documents: `docs/spec/spec-fixed.md`, `docs/prd.md`, `docs/features/gameplay/prd.md`, `docs/features/card-collection-deck/prd.md`, `docs/features/match-history/prd.md`, `docs/architecture/interview-20260714/interview-log.md`
- source_fingerprint: spec `6ac09a695776`, PRD hub `a5d3839d1075`, card collection `3f1e10deee90`, server architecture `d640ccea8672`
- implementation_paths: `build.gradle`, `src/main`, `src/main/resources`
- implementation_fingerprint: `src/main` `f09984c6fec4`, JPA/MySQL/Flyway 의존성 선언, 카드 persistence 구현 없음
- decision_summary: `docs/cards`와 `docs/card-packs` 작성·배포 원천, RDB의 모든 배포 불변 버전과 각 활성 버전 실행·조회, `GameEvent` 당시 결과 재현
- skip_conditions: 카드·팩 정의 원천, 불변 버전, 활성 전환, 경기 pinning과 관련 의존성이 변하지 않음
- re_review_triggers: RDB 직접 authoring, 운영 UI 카드·팩 편집, 외부 catalog/object storage, 다중 app version 동시 배포, historical replay 재계산 요구
- latest_result: ARCH-ADR-002·003과 fixed-20260714에 확정. 제품 정책은 PRD로 분리했고 상세 persistence는 후속 TRD/TDD로 이관

### harness-guardrails

- last_reviewed_at: 2026-07-14
- source_documents: `docs/architecture/harness-guardrails.md`, `docs/architecture/cicd-architecture.md`, `docs/architecture/interview-20260714/interview-log.md`, `build.gradle`, `.github/workflows/backend-ci.yml`
- source_fingerprint: harness `70772321d297`, cicd `bd706d31ba7b`
- implementation_paths: `build.gradle`, `src/test`, `.github/workflows`
- implementation_fingerprint: ArchUnit test, Spotless, GitHub Actions CI, 실행 가능한 Gradle wrapper 반영
- decision_summary: 기존 Hard/Conditional 분류 유지, 카드·카드팩 catalog와 effect 완결성은 구현 즉시 Hard, RDB 동기화는 persistence 구현 시 Testcontainers 검증
- skip_conditions: 카드·팩 catalog validator, effect registry, fixed contract와 persistence 구현이 아직 없고 관련 CI 설정이 변하지 않음
- re_review_triggers: 카드·팩 catalog validator/effect registry/persistence 구현, FE/BE 계약 fixed, Testcontainers 또는 CI workflow 변경
- latest_result: 문서 gate를 확정했고 기능 코드·Gradle 설정 변경은 후속 TDD로 이관

### module-boundaries

- last_reviewed_at: 2026-07-14
- source_documents: `docs/architecture/server-architecture.md`, `docs/architecture/interview-20260714/interview-log.md`
- source_fingerprint: server architecture `d640ccea8672`
- implementation_paths: `src/main/java`, `src/test/java/org/zzambas/tcgonlinechessbe/architecture`
- implementation_fingerprint: 기능 package 구현 없음, 기존 ArchUnit baseline
- decision_summary: `cardcollection`이 카드·팩 catalog 동기화와 활성 버전 공개 port를 소유하고 `gameplay`는 카드 port로 조회해 경기 버전을 고정
- skip_conditions: 카드·팩 catalog 소유권과 module API가 변하지 않고 직접 repository 참조가 없음
- re_review_triggers: 카드·팩 처리 소유권 변경, module API 변경, cardcollection/gameplay 저장소 직접 참조, 별도 서비스 분리
- latest_result: 기존 모듈러 모놀리스 의존성 방향과 일치하며 차단 이슈 없음

### cicd

- last_reviewed_at: 2026-07-14
- source_documents: `docs/architecture/cicd-architecture.md`, `docs/architecture/harness-guardrails.md`, `docs/architecture/interview-20260714/interview-log.md`
- source_fingerprint: cicd `bd706d31ba7b`, harness `70772321d297`
- implementation_paths: `.github/workflows/backend-ci.yml`, `build.gradle`
- implementation_fingerprint: 현재 `spotlessCheck test`, catalog 검증 task 미구현
- decision_summary: 카드·팩 활성 manifest·catalog와 카드 effect·contract 완결성은 구현 시 required check, RDB 충돌은 기동 차단
- skip_conditions: 카드·팩 catalog 관련 구현과 배포 workflow가 아직 없고 기존 CI가 변하지 않음
- re_review_triggers: 카드·팩 catalog task, CD, application startup sync, migration/rollback workflow 구현
- latest_result: gate 정책 확정, repo 설정 변경은 후속 구현으로 이관

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

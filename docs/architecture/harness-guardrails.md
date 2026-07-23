# Harness Guardrails

## 목적

서버 구조, 품질, 보안, 테스트, 운영 readiness에 대한 자동 검증 경계를 정의한다.

## Hard Gate

- Gradle compile/test
- Spotless format check
- ArchUnit module/hexagonal dependency test
- GitHub Actions PR required check

## Conditional Gate

- PMD: production 코드와 규칙셋 확정 뒤 Hard 전환
- SpotBugs/FindSecBugs: 인증·세션·권한 production 코드 도입 뒤 Hard 전환
- JaCoCo: 핵심 모듈 테스트와 기준 승인 뒤 Hard 전환
- Gradle dependency locking/verification: 의존성 고정 필요 시 Hard 전환
- Testcontainers MySQL: Flyway/JPA/transaction 통합 테스트 도입 뒤 활성화
- Spring Security Test: 인증·CSRF·계정 상태·제재 테스트가 생기는 즉시 필수
- OpenAPI/STOMP contract test: FE/BE 계약 fixture 합의 뒤 활성화
- Actuator/Prometheus endpoint와 민감 정보 제외: 운영 설정 도입 뒤 검증
- 카드 catalog 구조·식별자/버전 중복·활성 버전 참조 검증: 검증 task 구현 즉시 Hard gate로 전환
- 활성화·롤백 가능한 모든 카드 버전의 정의·효과 처리·선택·공개 결과·fixture 완결성: fixed 계약과 registry 구현 즉시 Hard gate로 전환
- 카드 버전 불변 동기화와 경기별 활성 버전 고정: persistence 구현 시 Testcontainers MySQL 검증에 포함
- 카드팩 catalog schema·버전 중복·활성 manifest·카드 참조·fingerprint 검증: validator 구현 즉시 Hard gate로 전환
- 카드팩 버전 불변 동기화와 manifest 기반 활성 전환: persistence 구현 시 Testcontainers MySQL 검증에 포함
- BE canonical OpenAPI 3.1·STOMP JSON Schema·fixture·manifest fingerprint 재계산: 계약 번들 생성 즉시 Hard gate로 전환
- FE의 pin된 BE commit·checked-in bundle·생성 TypeScript/validator/fixture 일치 검증: FE 계약 동기화 즉시 FE Hard gate로 전환

## Advisory 도구

- SLO/alert threshold 검토
- dashboard와 alert routing 검토
- 테스트 실행 시간·flakiness 추세 검토
- card analytics read model 재집계 운영 검토

## Backend 강제 규칙

- domain은 adapter와 framework에 의존하지 않는다.
- application은 adapter 구현체를 참조하지 않는다.
- 기능 모듈 간 내부 package 참조를 금지한다.
- inbound adapter는 application use case로만 진입한다.
- outbound adapter는 port를 구현한다.
- `shared`는 최소 공통 커널로 제한한다.

## Frontend 강제 규칙

- FE 계약이 합의되기 전에는 적용하지 않는다.
- BE 저장소의 canonical 계약 번들을 소유 원천으로 사용하고 FE는 적용할 BE git commit을 명시적으로 pin한다.
- BE의 version-controlled OpenAPI·STOMP schema와 authored fixture 원본만 사람이 수정하는 단일 작성 정본이며 manifest, fingerprint와 언어별 생성 산출물은 결정적 파생물이다.
- FE에는 pin된 commit의 bundle을 checked-in copy로 두며 독립적인 계약 원천을 만들지 않는다.
- FE 채택 metadata는 allowlist canonical BE repository identity, full 40-character commit, bundle root와 expected root fingerprint를 함께 고정한다.
- FE 일반 build·test는 checked-in copy만 사용한다. 별도 contract-drift CI job만 최신 branch를 탐색하지 않고 정확히 pin된 BE commit을 read-only checkout해 protected default branch 승인 여부와 canonical bundle bytes, copy, manifest, fingerprint의 drift를 검증한다.
- BE는 빈 임시 디렉터리에서 canonical source→bundle을 재생성하고 FE는 manifest allowlist data file만 빈 staging directory로 복사한 뒤 FE의 lockfile-pinned generator를 clean temp에서 실행한다. stale/unmanifested/missing file, 직접 수정한 generated output, pin-only/copy-only 변경과 fetched BE script 실행은 금지한다.

## CI Required Check

- compile/test, Spotless, ArchUnit, 활성화된 Conditional gate

현재 `backend-ci.yml`은 `spotlessCheck test`로 Spotless, compile, ArchUnit, JUnit을 실행한다.

## 테스트 실행 리포트와 메트릭

- JUnit XML, coverage report, 실패 로그를 artifact로 보존한다.
- 실행 시간, 실패, skipped, retry 여부를 확인한다.

## Release Readiness Gate

- CD 설계 전까지 수동 승인만 가능하다.
- provider 확정 후 Flyway migration, smoke test, rollback, post-deploy metric check를 정의한다.
- BE commit pin은 runtime 호환성 협상이 아니다. production 최초 배포 뒤 기존 closed validator를 깨는 변경은 parallel version 또는 expand-contract 없이 활성화하지 않는다.
- FE·BE artifact의 adopted bundle root fingerprint compatibility gate는 CD 확정 뒤 추가한다. 그 전에는 post-launch breaking contract activation을 허용하지 않는다.
- 전체 REST/STOMP/오류/fixture manifest closure가 fixed되는 `contract-schema-closure` 뒤 계약 bundle gate를 활성화한다.

## Operational Readiness Gate

- Actuator health/readiness/liveness와 Prometheus endpoint 접근 경계가 구성되면 검증한다.
- backup/PITR restore 검증은 provider 선택과 RPO/RTO 확정 뒤 gate로 추가한다.

## Observability Gate

- 민감 정보가 로그·메트릭·오류 응답에 없는지 검증한다.
- 운영 메트릭과 card analytics read model을 분리한다.

## 도입 전 PoC 항목

- Spring Security session/CSRF/STOMP interceptor 통합 테스트
- Flyway와 Testcontainers MySQL migration 테스트
- 카드·카드팩 catalog 불변 동기화, 활성 버전 전환과 경기별 버전 고정 통합 테스트
- ArchUnit module boundary rule
- Spotless Gradle integration

## 후속 스킬 연계

- security-review: 인증·세션·STOMP 구현 후 독립 보안 검증
- architecture-decision: provider/CD/distributed system 전환 시 재실행

## 미확정 사항

- PMD/SpotBugs/JaCoCo의 세부 rule와 threshold
- 카드·카드팩 catalog 검증 task와 효과 처리 registry 구현 시점
- SLO/alert/RPO/RTO 기준

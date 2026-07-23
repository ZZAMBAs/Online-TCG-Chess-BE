# CI/CD Architecture

## 목적

MVP의 PR 품질 게이트와 제공자 확정 전 배포 보류 원칙을 정의한다.

## 원천 산출물

- `docs/architecture/interview-20260710/interview-log.md`
- `docs/spec/spec-fixed.md`

## 브랜치와 머지 정책

- `main` 병합 전 GitHub Pull Request required checks를 통과해야 한다.
- branch protection의 실제 GitHub 설정은 저장소 운영 권한과 함께 별도 적용한다.

## Required Checks

- Gradle compile/test
- Spotless check
- ArchUnit architecture test
- 활성화된 Conditional tool 검사
- 테스트 XML과 coverage report artifact 업로드

## Backend CI

- GitHub Actions가 Gradle 검증을 실행한다.
- Flyway migration, JPA, MySQL 통합 테스트가 생기면 Testcontainers job을 추가한다.
- Spring Security Test가 필요한 모듈은 인증·CSRF·제재 검증을 포함한다.
- 카드 catalog 검증이 구현되면 구조, 식별자·버전 중복, 활성 버전 참조와 동일 버전 불변성을 required check로 실행한다.
- fixed FE/BE 카드 계약과 효과 처리가 구현되면 활성화·롤백 가능한 모든 버전의 정의·효과 처리·선택·공개 결과·fixture 완결성 검증을 required check로 실행한다.
- 카드팩 catalog 검증이 구현되면 schema, 식별자·버전 중복, 활성 manifest, 카드 식별자·종류 참조, fingerprint와 동일 버전 불변성을 required check로 실행한다.
- canonical 계약 번들이 생성되면 OpenAPI 3.1, STOMP JSON Schema, fixture와 manifest의 fingerprint를 재계산하고 source·manifest·generated output drift를 required check로 실패시킨다.

## Frontend CI

- FE 저장소는 적용할 BE git commit을 명시적으로 pin하고 해당 commit의 canonical 계약 번들을 checked-in copy로 동기화한다.
- FE 계약 동기화 뒤 pin된 commit, bundle manifest/fingerprint, 생성 TypeScript·validator·fixture의 재현성을 required check로 검증한다.
- 일반 FE build와 테스트는 checked-in copy만 사용한다. contract-drift job은 최신 계약을 탐색하지 않고 정확히 pin된 BE commit만 read-only checkout해 canonical bundle bytes와 copy를 비교한다.
- pin checkout은 CI 검증 시점의 개발 의존성이며 runtime, application build artifact와 제품 동작은 BE 원격 조회나 artifact registry에 의존하지 않는다.
- FE 채택 metadata는 allowlist canonical repository identity, full 40-character BE commit, canonical bundle root와 expected root fingerprint를 함께 고정한다. provenance job은 해당 commit이 canonical protected default branch에서 승인되었는지 확인한다.
- BE job은 clean temp regeneration과 manifest closure/per-file hash/root fingerprint/checked-in byte diff를 수행한다. FE job은 빈 staging directory에 manifest allowlist data file만 복사하고 fetched script를 실행하지 않으며 FE lockfile-pinned generator의 clean output을 checked-in output과 byte 비교한다.
- provenance checkout 실패, pin-only/copy-only/fingerprint-only 변경, stale·unmanifested·missing file과 generated output 직접 수정은 required check 실패다.

## 보안과 공급망 검사

- SpotBugs/FindSecBugs는 인증·세션·권한 production 코드 도입 뒤 Hard gate로 전환한다.
- Gradle dependency locking/verification은 의존성 고정과 CI 재현성 필요 시 Hard gate로 전환한다.

## 테스트 리포트와 메트릭 검사

- JUnit XML, 실패 로그, coverage report를 artifact로 보존한다.
- 테스트 실행 시간, 실패, skipped, retry 여부는 CI report에서 추적한다.

## Release Gates

- CD는 클라우드 제공자와 컴퓨팅 방식 확정 전까지 미구성이다.
- 제공자 확정 후 migration 검증, artifact 배포, smoke test, manual approval, post-deploy metric check를 재인터뷰한다.
- FE·BE release artifact에는 adopted contract bundle root fingerprint를 기록한다. CD 확정 뒤 release pair compatibility를 deploy gate로 검증한다.
- production 최초 배포 이후 기존 closed validator를 깨는 계약은 parallel version 또는 expand-contract 없이 활성화하지 않는다. CD gate가 없는 동안 post-launch breaking contract activation은 금지한다.

## Smoke Test

- 배포 환경 미확정으로 현재 정의하지 않는다.

## Rollback Gate

- 배포 방식과 DB migration rollback 정책이 미확정이므로 제공자 확정 후 결정한다.

## Post-deploy Metric Check

- Actuator/Prometheus endpoint와 dashboard/alerting 제품이 연결된 뒤 정의한다.

## Migration 검증과 배포 순서

- Flyway migration 실패는 애플리케이션 기동과 배포 진행을 중단해야 한다.
- 패키징된 카드·카드팩 catalog와 RDB의 같은 식별자·버전 내용이 다르거나 활성 버전이 유효한 정의를 가리키지 않으면 애플리케이션 기동을 중단한다.
- 누락된 새 카드·카드팩 버전과 활성 버전 선택은 각 catalog 검증을 통과한 뒤 반영한다.
- 활성 버전 변경은 각 활성 manifest를 변경한 새 산출물의 배포로만 수행하며 RDB 직접 변경은 배포 절차로 인정하지 않는다.
- 실제 배포 순서와 rollback 가능성은 CD 설계 시 결정한다.

## Artifact와 버전

- versioned Spring Boot executable JAR를 CI artifact로 생성한다.
- container image tagging과 registry 정책은 미확정이다.

## Rollback 정책

- 제공자, 배포 단위, DB migration 정책 확정 후 재인터뷰한다.

## Secret 처리

- CI secret은 GitHub Actions Secrets로 주입한다.
- secret은 repository와 CI log에 평문으로 남기지 않는다.

## Repo 설정 반영

- `.github/workflows/backend-ci.yml`이 PR과 `master` push에서 `./gradlew spotlessCheck test`를 실행한다.
- JUnit XML과 HTML test report를 artifact로 보존한다.

## 후속 스킬 연계

- provider/CD 결정 후 architecture-decision 재실행

## 미확정 사항

- branch protection 실제 설정, release approval, deployment workflow, rollback, post-deploy check

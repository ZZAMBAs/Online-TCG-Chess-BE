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

## Frontend CI

- FE 저장소와 계약이 합의된 뒤 REST OpenAPI, STOMP schema/fixture contract test를 Conditional gate로 추가한다.

## 보안과 공급망 검사

- SpotBugs/FindSecBugs는 인증·세션·권한 production 코드 도입 뒤 Hard gate로 전환한다.
- Gradle dependency locking/verification은 의존성 고정과 CI 재현성 필요 시 Hard gate로 전환한다.

## 테스트 리포트와 메트릭 검사

- JUnit XML, 실패 로그, coverage report를 artifact로 보존한다.
- 테스트 실행 시간, 실패, skipped, retry 여부는 CI report에서 추적한다.

## Release Gates

- CD는 클라우드 제공자와 컴퓨팅 방식 확정 전까지 미구성이다.
- 제공자 확정 후 migration 검증, artifact 배포, smoke test, manual approval, post-deploy metric check를 재인터뷰한다.

## Smoke Test

- 배포 환경 미확정으로 현재 정의하지 않는다.

## Rollback Gate

- 배포 방식과 DB migration rollback 정책이 미확정이므로 제공자 확정 후 결정한다.

## Post-deploy Metric Check

- Actuator/Prometheus endpoint와 dashboard/alerting 제품이 연결된 뒤 정의한다.

## Migration 검증과 배포 순서

- Flyway migration 실패는 애플리케이션 기동과 배포 진행을 중단해야 한다.
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

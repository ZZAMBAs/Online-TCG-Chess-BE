# Harness Architecture Fixed

## 확정된 결정

### Hard Gate

- `fixed-20260710/harness-fixed.md`의 `./gradlew spotlessCheck test`, Spotless, ArchUnit과 GitHub Actions required check를 유지한다.
- 카드 catalog 검증 task가 구현되는 즉시 구조, 식별자·버전 중복, 활성 버전 참조와 같은 버전 불변성 검증을 Hard gate로 전환한다.
- fixed FE/BE 카드 계약과 effect registry가 구현되는 즉시 활성화·롤백 가능한 모든 버전의 정의·효과 처리·선택·공개 결과·fixture 완결성 검증을 Hard gate로 전환한다.
- 카드팩 catalog validator가 구현되는 즉시 schema, 식별자·버전 중복, 활성 manifest 참조, 카드 식별자·종류 참조, fingerprint와 동일 버전 불변성 검증을 Hard gate로 전환한다.
- canonical 계약 번들이 생성되는 즉시 BE CI는 OpenAPI 3.1, STOMP JSON Schema, fixture와 manifest의 fingerprint를 재계산해 불일치·미생성 변경을 실패시킨다.
- FE가 계약 번들을 동기화하는 즉시 FE CI는 pin된 BE commit과 checked-in bundle manifest가 일치하는지, 생성 코드·validator·fixture가 해당 bundle에서 재현되는지 검증한다.

### Conditional Gate

- 카드 persistence 구현 시 Testcontainers MySQL로 새 버전 추가, 같은 버전 충돌 시 기동 실패, 활성 버전 전환과 경기별 버전 고정을 검증한다.
- 카드팩 persistence 구현 시 같은 Testcontainers MySQL 경계에서 새 팩 버전 추가, 동일 버전 충돌 기동 실패와 배포 manifest 기반 활성 전환을 검증한다.
- 기존 PMD, SpotBugs/FindSecBugs, JaCoCo, dependency locking/verification, Spring Security Test와 OpenAPI/STOMP contract test의 Conditional 분류를 유지한다.

### Advisory

- 오래된 비활성 카드 버전의 재활성화 필요성과 효과 처리 보존 범위를 릴리즈마다 검토한다.
- catalog 동기화 실패와 활성 버전 롤백 절차는 CD 확정 시 release readiness gate로 승격한다.

## 문서화 가정

- 현재는 기능 구현 전이므로 새 Gradle task, Testcontainers와 production 동기화 코드를 이번 결정에서 추가하지 않는다.
- 하네스 구현 시 기존 `spotlessCheck test` required check에 통합한다.

## Canonical 계약 번들 공유

- BE 저장소의 version-controlled OpenAPI 3.1·STOMP JSON Schema와 authored fixture 원본만 사람이 수정하는 단일 작성 정본이다. manifest, fingerprint와 언어별 생성 산출물은 이 정본에서 결정적으로 파생하며 직접 수정하거나 별도 의미 원천으로 사용하지 않는다.
- FE 저장소는 적용할 BE git commit을 명시적으로 pin하고 그 commit의 canonical bundle을 checked-in copy로 동기화한다. FE가 독립적으로 같은 계약을 다시 작성하지 않는다.
- FE 계약 채택 metadata는 allowlist로 고정한 canonical BE repository identity, full 40-character commit, canonical bundle root와 expected root fingerprint를 함께 고정한다. manifest 안에 자기 source commit을 넣는 self-reference는 사용하지 않는다.
- BE CI는 canonical source를 빈 임시 디렉터리에 재생성해 manifest file closure, per-file hash와 root fingerprint를 계산하고 checked-in bundle과 byte-for-byte 비교한다. manifest 미참조·누락·stale file과 직접 수정한 파생 산출물은 실패한다.
- FE sync는 manifest가 허용한 data file closure만 빈 staging directory로 복사하고 fetched BE script를 실행하지 않는다. FE repo lockfile로 고정한 generator를 clean temporary directory에서 실행해 checked-in TypeScript·validator·fixture 파생물과 byte-for-byte 비교한다.
- FE provenance gate는 canonical repository의 정확한 pin commit을 read-only checkout하고 protected default branch에서 승인된 commit인지 확인한 뒤 manifest graph와 checked-in copy를 byte-for-byte 비교한다. pin-only, copy-only, fingerprint-only 변경이나 provenance checkout 실패는 모두 실패한다.
- 계약 변경은 BE canonical bundle commit과 FE pin 갱신을 서로 구분되는 리뷰 가능한 변경으로 수행한다. FE pin을 갱신하지 않은 동안 기존 FE build는 기존 pin을 계속 사용한다.
- FE의 일반 build와 테스트는 checked-in copy만 사용해 network 없이 재현한다. FE의 contract-drift CI job은 최신 branch나 HEAD를 조회하지 않고 명시적으로 pin된 BE commit만 read-only checkout해 canonical bundle bytes와 checked-in copy를 비교한다.
- 이 checkout은 CI 검증 시점의 개발 의존성일 뿐 runtime, application build artifact와 제품 동작의 원격 의존성이 아니다. 외부 artifact registry도 사용하지 않는다.

## 계약 호환성과 릴리즈 경계

- BE commit pin은 build provenance이며 runtime protocol negotiation이 아니다.
- production 최초 배포 이후 기존 pin의 closed validator를 실패시키는 field 추가·삭제·의미 변경은 incompatible contract로 분류한다.
- incompatible contract는 기존 endpoint·destination·schema를 유지하는 parallel version 또는 old/new를 함께 수용하는 expand-contract 단계 없이 활성화하지 않는다.
- FE·BE release artifact metadata에는 adopted bundle root fingerprint를 기록한다. CD 확정 뒤 deploy gate가 release pair compatibility를 검사한다.
- provider/CD 전에는 compatibility deploy gate가 미구현이므로 post-launch breaking contract activation을 허용하지 않는다.
- 전체 REST endpoint, STOMP destination, 오류와 fixture가 manifest root closure에 포함되는 `contract-schema-closure`가 fixed된 뒤 이 gate를 활성화한다.

## 미확정 또는 상위 산출물 재검토

- 카드·카드팩 catalog validator와 effect registry의 상세 구현
- provider/CD 기반 배포·rollback·post-deploy gate

## 후속 스킬 연계

- `negotiate-fe-be-contract`: fixed schema와 fixture 확정
- `create-trd`: 검증 task와 통합 테스트 경계 설계
- `tdd-workflow`: 이슈별 gate 활성화

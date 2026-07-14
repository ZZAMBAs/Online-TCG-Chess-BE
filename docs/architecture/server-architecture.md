# Server Architecture

## 목적

TCG Online Chess MVP의 서버 구조, 모듈 경계, 의존성 방향과 저장 책임을 정의한다.

## 원천 산출물

- `docs/spec/spec-fixed.md`
- `docs/prd.md`
- `docs/features/*/prd.md`
- `docs/architecture/interview-20260710/interview-log.md`
- `docs/architecture/interview-20260714/interview-log.md`

## 현재 구현 기준

- 현재는 Spring Boot 애플리케이션 골격과 기본 의존성만 존재한다.
- 기능 패키지, persistence 구현, REST/STOMP handler, CI workflow, architecture test는 아직 없다.

## 기술 스택 결정

- Java 25, Spring Boot 4.0.6
- Spring MVC, Spring WebSocket/STOMP, Spring Security
- Spring Data JPA/Hibernate, MySQL 호환 RDB
- Flyway migration
- Spring Boot Actuator, Micrometer Prometheus registry
- JUnit, Spring Security Test, ArchUnit, Spotless

## 서버 아키텍처 스타일

- 기능 우선 모듈러 모놀리스와 헥사고날/클린 원칙을 사용한다.
- Gradle은 현재 단일 모듈을 유지한다. 기능 모듈이 독립 빌드·배포·확장 요구를 갖기 전에는 Gradle 멀티모듈로 분리하지 않는다.

## 프로젝트 디렉터리 구조

```text
org.zzambas.tcgonlinechessbe
├── identity
├── matchmaking
├── gameplay
├── cardcollection
├── matchhistory
├── matchchat
├── community
├── trustsafety
└── shared
```

각 기능 모듈은 `domain`, `application`, `adapter/in`, `adapter/out`, `configuration`을 가진다.

## 패키지와 모듈 경계

- `identity`: 계정, 세션 인증, OAuth, 이메일 인증, 설정
- `matchmaking`: 대기열, MMR 후보 탐색, 경기 생성 전 확정
- `gameplay`: 체스, 턴, 카드 행동, 마나, 타이머, 재접속, 활성 경기 상태
- `cardcollection`: 버전 카드 catalog, 활성 버전, 컬렉션, 카드팩, 덱 유효성
- `matchhistory`: 결과, 전적, MMR 반영, 기보, 통계 read model
- `matchchat`: 경기 채팅, 마스킹, 전달 제한, 신고 증거
- `community`: 게시글, 검색, 상태, 자동 숨김 결과
- `trustsafety`: 차단, 신고, 제재, 금칙어, 관리자 감사
- `shared`: 공통 primitive, 오류 추상화, 식별자처럼 도메인 중립 요소만 둔다.

## 레이어와 의존성 방향

- domain은 framework와 adapter에 의존하지 않는다.
- application은 domain과 port에 의존하며 use case와 트랜잭션 경계를 소유한다.
- adapter/in은 application use case를 호출한다.
- adapter/out은 application/domain port를 구현한다.
- configuration은 의존성 조립만 담당한다.
- 다른 모듈의 내부 adapter, entity, repository 직접 참조를 금지한다.

## 어댑터 배치 구조

- REST controller와 STOMP handler는 `adapter/in`에 둔다.
- JPA repository 구현, SMTP, OAuth provider, 외부 시간/난수 provider는 `adapter/out`에 둔다.
- REST/STOMP adapter는 인증 문맥, 입력 변환, 오류/이벤트 projection만 담당한다.

## 빌드 모듈 구성

- 단일 Gradle 모듈을 유지한다.
- 모듈 경계는 패키지와 ArchUnit test로 강제한다.
- 독립 배포나 독립 확장 요구가 생기면 Gradle 멀티모듈 또는 서비스 분리를 재검토한다.

## 보안 경계의 코드 배치

- Spring Security 설정과 HTTP session 정책은 configuration에 둔다.
- REST CSRF, STOMP CONNECT/Origin/session 검증은 inbound security adapter에 둔다.
- 계정 상태·제재 검증은 application policy로 두고 REST/STOMP 진입마다 호출한다.

## 저장과 트랜잭션 책임

- MySQL RDB가 계정, 덱, 결과, 기보, 신고, 감사, 집계 read model과 배포된 카드·카드팩 catalog의 실행·조회 원천이다. 카드와 카드팩 정의의 작성·배포 원천은 각각 버전 관리되는 `docs/cards`, `docs/card-packs`다.
- `GameEvent`는 append-only 기보·통계 원천이고 `GameSnapshot`은 복구 보조다.
- 활성 경기는 단일 인스턴스 메모리에서 처리한다.
- 경기 종료는 결과, 전적, MMR, 기보 봉인, 통계 집계를 application service 트랜잭션 경계에서 함께 확정한다.
- 카드 사용·체크메이트 기물·카드 투입/승리 통계는 GameEvent에서 파생한 MySQL read model로 관리한다.

## 카드 catalog와 버전 저장

- `docs/cards`의 버전별 JSON과 별도 활성 버전 목록을 카드 작성 원천으로 사용하고 검증된 빌드 산출물에 포함한다.
- `cardcollection` 모듈이 패키징된 catalog를 읽어 RDB의 카드 정의와 활성 버전을 동기화하는 application port를 소유한다.
- RDB에는 검증·배포된 모든 카드 식별자·버전을 불변으로 보존한다. 동일 식별자·버전의 저장 내용이 다르면 기동을 실패시키고 새 버전만 추가한다.
- 카드별 활성 버전은 버전 정의와 분리한다. 신규 경기 생성 시 `gameplay`는 `cardcollection`의 공개 application port로 활성 버전을 조회해 경기 덱에 고정하고 저장소를 직접 참조하지 않는다.
- 활성 버전은 RDB 운영 수정으로 전환하지 않고 버전 관리되는 활성 버전 목록을 변경한 새 배포에서만 전환한다.
- 활성화하거나 롤백 대상으로 유지하는 모든 카드 버전은 `gameplay`의 효과 처리와 선택·공개 계약·fixture를 함께 제공해야 한다. 기존 효과 처리로 표현할 수 없는 변경에는 새 버전용 처리를 추가한다.
- 과거 기보는 저장된 `GameEvent` 결과와 당시 카드 식별자·버전을 사용하며 최신 효과 처리를 재실행하지 않는다.

## 카드팩 catalog와 확률 버전 저장

- `docs/card-packs`의 버전별 JSON과 별도 활성 버전 manifest를 카드팩 작성 원천으로 사용하고 검증된 빌드 산출물에 포함한다.
- `cardcollection` 모듈이 패키징된 팩 catalog를 읽어 RDB의 팩 정의와 활성 버전을 동기화하는 application port를 소유한다.
- RDB에는 검증·배포된 모든 팩 식별자·버전을 불변으로 보존한다. 동일 식별자·버전의 저장 내용이 다르면 기동을 실패시키고 누락된 새 버전만 추가한다.
- 팩별 활성 버전은 정의와 분리하고, 활성 manifest를 변경한 새 배포에서만 전환한다. 운영 중 RDB 직접 변경은 활성화 절차가 아니다.
- 팩의 제품 schema, 확률값, 지급 결과와 감사 표시 의미는 PRD·계약이 소유하며 architecture 문서에서 다시 확정하지 않는다.

## 정적 분석과 강제 규칙

- ArchUnit: Hard gate. 모듈 경계와 의존성 방향 검증
- Spotless: Hard gate. Java·Gradle 포맷 검증
- PMD: production 코드 규모와 규칙셋 확정 뒤 Hard 전환
- SpotBugs/FindSecBugs: 인증·세션·권한 production 코드 도입 뒤 Hard 전환
- JaCoCo: 핵심 모듈 테스트와 기준 승인 뒤 Hard 전환
- dependency locking/verification: 외부 의존성 고정과 CI 재현성 필요 시 Hard 전환

## 테스트와 품질 게이트

- domain/application은 단위 테스트 중심으로 검증한다.
- Spring Security Test는 인증, CSRF, 계정 상태, 제재 테스트에 필수다.
- Testcontainers MySQL은 Flyway, JPA, transaction, 종료 원자성 통합 테스트가 생기면 활성화한다.
- REST OpenAPI와 STOMP schema/fixture가 합의되면 contract test를 추가한다.

## Repo 설정 반영

- `build.gradle`에 Spring Security, Flyway, ArchUnit, Spotless와 Spring Security Test를 반영했다.
- `src/test/java/.../architecture/ArchitectureTest.java`에 초기 ArchUnit 규칙을 추가했다.
- `.github/workflows/backend-ci.yml`에 Spotless와 테스트를 실행하는 CI workflow를 추가했다.
- `gradlew` 실행 권한을 복구해 local hook과 CI에서 같은 wrapper 명령을 사용할 수 있게 했다.

## 미확정 사항

- 통계 read model의 갱신 시점, 재집계 운영 방식, 사용자 노출 범위

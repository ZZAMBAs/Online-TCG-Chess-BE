# Implementation Architecture Fixed

## 확정된 결정

- Java 25와 Spring Boot 4.0.6 기반 단일 Gradle 모듈을 유지한다.
- 기능 우선 모듈러 모놀리스와 헥사고날/클린 원칙을 사용한다.
- 기능 모듈은 `identity`, `matchmaking`, `gameplay`, `cardcollection`, `matchhistory`, `matchchat`, `community`, `trustsafety`다.
- 각 모듈은 `domain`, `application`, `adapter/in`, `adapter/out`, `configuration` 구조를 사용한다.
- domain은 framework와 adapter에 의존하지 않고, application service가 use case와 트랜잭션 경계를 소유한다.
- REST/STOMP는 inbound adapter, JPA/SMTP/OAuth는 outbound adapter로 배치한다.
- MySQL 호환 RDB와 Spring Data JPA/Hibernate를 사용한다.
- Flyway migration을 schema 변경의 단일 원천으로 하고 production JPA는 `validate`로 제한한다.
- `GameEvent`는 기보와 analytics 원천이며 `GameSnapshot`은 보조 저장소다.
- 활성 경기는 단일 프로세스 메모리에서 처리한다.
- 카드 사용, 카드별 경기 투입/승리, 체크메이트 기물 통계는 GameEvent 기반 집계 read model로 관리한다.
- Spring Security server session, CSRF, Origin, STOMP interceptor 재검증을 사용한다.

## 문서화 가정

- 세부 package 이름과 application port API는 feature 구현과 TRD에서 구체화한다.
- analytics read model의 schema와 갱신 구현은 후속 TRD/issue에서 결정한다.

## 미확정 또는 상위 산출물 재검토

- 카드 통계의 사용자 노출 범위, 집계 기간, 카드 버전별 해석은 관련 PRD/TRD에서 확정한다.
- 카드/팩 master 파일 포맷과 seed 방식은 미확정이다.

## 후속 스킬 연계

- `create-trd`: 상세 persistence, port, contract, analytics read model 설계
- `create-issues-adr`: Flyway, Security, 모듈별 구현 issue 분리
- `tdd-workflow`: issue 단위 구현과 Hard gate 유지

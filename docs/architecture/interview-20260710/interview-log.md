# Architecture Interview Log

## 세션 정보

- 시작일: 2026-07-10
- 기준 원천: `docs/spec/spec-fixed.md`, `docs/prd.md`, 기능별 PRD
- 현재 구현: Spring Boot 4.0.6, Java 25, JPA, MySQL connector, Mail, WebSocket/STOMP, Actuator, Prometheus 의존성 선언만 존재
- 기존 아키텍처 확정본: 없음

## 확정 결정

### 서버 구조

- 모듈러 모놀리스와 헥사고날/클린 원칙을 채택한다.
- 최상위 기능 모듈은 `identity`, `matchmaking`, `gameplay`, `cardcollection`, `matchhistory`, `matchchat`, `community`, `trustsafety`로 둔다.
- 각 모듈은 `domain`, `application`, `adapter/in`, `adapter/out`, `configuration` 구조를 사용한다.
- `shared`는 공통 커널로 최소화하며 기능 모듈의 내부 구현을 담지 않는다.
- controller와 STOMP handler는 inbound adapter로서 입력·인증 문맥·응답 변환만 담당한다.
- application service가 use case 조합과 트랜잭션 경계를 소유한다.
- domain은 Spring MVC, STOMP, JPA, SMTP, OAuth SDK에 직접 의존하지 않는다.
- 모듈 간 직접 adapter/entity/repository 참조를 금지하고 공개 application port 또는 명시적 domain event로만 협력한다.

### 저장과 확장

- MySQL 호환 RDB와 Spring Data JPA/Hibernate를 사용한다.
- schema 변경은 Flyway versioned migration의 단일 원천으로 관리하고 운영 JPA `ddl-auto`는 `validate`로 제한한다.
- 종료 경기와 기보의 원천은 append-only `GameEvent`이며 `GameSnapshot`은 보조 저장소다.
- 활성 경기는 단일 인스턴스 메모리에 두고, 서버 재시작·crash 시 완전 복구를 보장하지 않는다.
- Redis, 캐시, pub/sub, 외부 메시지 브로커, 분산 타이머, 다중 인스턴스 STOMP는 MVP에 도입하지 않는다.
- 카드 사용·카드별 경기 투입/승리·체크메이트 기물 통계는 `GameEvent` 원천과 MySQL 집계 read model로 수집한다. Prometheus에는 해당 분석 데이터를 label로 넣지 않는다.

### 인증과 네트워크

- Spring Security 기반 서버 세션 쿠키 인증을 사용한다.
- 세션 저장소는 단일 인스턴스 메모리로 두며 Redis/JDBC 분산 세션은 후속 재인터뷰 대상이다.
- REST 상태 변경은 CSRF를 검증하고, STOMP `CONNECT`는 HTTP 세션·CSRF·Origin을 검증한다.
- STOMP `SUBSCRIBE`와 `SEND`는 인증·역할·계정 상태·제재를 interceptor에서 재검증한다.
- reverse proxy가 TLS를 종료하고 FE 정적 자산, REST, STOMP를 같은 HTTPS origin으로 라우팅한다.
- CDN은 MVP에 도입하지 않는다.

### CI, 테스트, 하네스

- GitHub Actions PR 검증을 Hard gate로 사용한다. CD는 클라우드 제공자 확정 후 재결정한다.
- compile/test, Spotless, ArchUnit을 Hard gate로 둔다.
- PMD, SpotBugs/FindSecBugs, JaCoCo, Gradle dependency locking/verification은 명시된 도입 조건 이후 Hard gate로 전환하는 Conditional gate다.
- Spring Security Test는 인증·CSRF·계정 상태·제재 테스트에 필수로 사용한다.
- Testcontainers MySQL은 migration, repository, transaction, 경기 종료 원자성 통합 테스트가 생기는 시점부터 Conditional gate다.
- REST는 OpenAPI, STOMP는 JSON Schema와 versioned fixture로 관리하고 FE/BE 계약 합의 뒤 contract test를 Conditional gate로 전환한다.

### 관측과 운영

- Actuator health/readiness/liveness, Prometheus endpoint, 구조화 로그를 MVP 필수로 둔다.
- Actuator와 Prometheus endpoint는 public internet에 직접 노출하지 않는다.
- Grafana, alert routing, log aggregation, 운영 Secret Manager는 클라우드 제공자 확정 후 재인터뷰한다.
- 환경은 `local`, `test`, `prod` Spring profile로 분리하고 secret은 환경 변수와 CI secret으로 주입한다.
- 종료 경기·계정·카드/덱·신고·감사·집계 데이터는 선택된 제공자의 native backup/PITR로 보호한다.

## 미확정 사항

- 클라우드 제공자, 컴퓨팅 런타임, Dockerfile, image registry, DB managed/self-hosted 선택
- backup 보존 기간, RPO/RTO, 복구 훈련 주기
- 트래픽 목표, 비용 상한, SLO, alert 임계치
- Grafana/log aggregation/alerting/Secret Manager 제품
- CD, migration 배포, smoke test, rollback 자동화
- 카드 master 파일 구조와 카드/팩 seed 연결 방식

## 상위 산출물 재검토 필요

- 반영됨: 카드 사용·카드별 경기 투입/승리·체크메이트 기물 통계 수집 요구를 `docs/spec/spec-fixed.md`에 추가했다.
- 재검토 필요: `gameplay`, `match-history`, `card-collection-deck` PRD는 통계의 사용자 노출 범위, 집계 주기, 카드 버전별 해석을 아직 소유하지 않는다.
- 재검토 필요: RPO/RTO, 트래픽 목표, 비용 상한, SLO는 운영 요구사항 확정 시 spec 인터뷰가 필요하다.

## 재인터뷰 트리거

- 클라우드 제공자·컴퓨팅·비용 상한·트래픽/SLO가 확정되는 경우
- 무중단 배포 또는 활성 경기 복구가 제품 요구사항이 되는 경우
- 단일 인스턴스의 CPU·메모리·WebSocket 연결·명령 지연이 운영 목표를 지속적으로 충족하지 못하는 경우
- 다중 인스턴스, load balancer, Redis session, STOMP pub/sub, 분산 lock/queue가 필요한 경우
- 비동기 통계 집계·검색·메일 workload가 사용자 경험을 저해하는 경우

## 파일 반영 전 승인

- 2026-07-10: 사용자가 문서 초안 작성과 도메인 통계 요구의 원천 명세 반영을 승인했다.

# Infrastructure Architecture

## 목적

MVP 인프라의 확정된 경계와 클라우드 제공자 확정 전까지의 보류 항목을 정의한다.

## 원천 산출물

- `docs/spec/spec-fixed.md`
- `docs/architecture/interview-20260710/interview-log.md`

## MVP 인프라 전제

- 단일 백엔드 인스턴스와 단일 writer를 사용한다.
- MySQL 호환 RDB를 사용한다.
- Redis, pub/sub, 외부 메시지 브로커, 분산 타이머, 다중 인스턴스 STOMP는 제외한다.

## 클라우드와 호스팅 선택

- 클라우드 제공자는 미확정이다.
- 제공자 선택 시 컴퓨팅, managed DB, secret manager, log/metric platform, backup/PITR을 재인터뷰한다.

## 컴퓨팅과 배포 단위

- 단일 Spring Boot 인스턴스를 배포 단위로 사용한다.
- versioned executable JAR가 CI artifact다.
- OCI container image로 패키징 가능한 상태를 유지하되 Dockerfile, registry, runtime은 미확정이다.

## 네트워크, TLS, Load Balancer, CDN

- HTTPS 단일 origin을 사용한다.
- reverse proxy가 TLS를 종료하고 WebSocket upgrade를 전달한다.
- FE 정적 자산, REST, STOMP는 같은 origin으로 라우팅한다.
- CDN과 다중 load balancer는 MVP에 도입하지 않는다.

## FE/BE 배포와 라우팅

- same-site 배포와 session cookie 인증을 전제로 한다.
- REST와 STOMP의 상세 path/destination은 TRD와 FE/BE 계약에서 결정한다.

## 데이터베이스 선택과 운영

- MySQL 호환 RDB를 사용한다.
- schema는 Flyway migration으로 변경하고 production JPA는 `validate`로 제한한다.
- DB 제공자의 native backup/PITR을 종료 경기, 계정, 카드/덱, 신고, 감사, 집계 데이터 보호 수단으로 사용한다.
- RDB에는 검증·배포된 모든 카드 식별자·버전과 카드별 현재 활성 버전을 보존한다.
- 카드 version 동기화는 기존 동일 버전을 갱신하지 않고 새 버전 추가와 활성 버전 선택만 허용한다.
- 활성 버전 변경은 버전 관리되는 활성 버전 목록을 포함한 애플리케이션 배포를 통해서만 수행하며 운영 중 RDB 직접 변경을 허용하지 않는다.

## Redis/Cache/Message Broker 선택

- MVP에는 도입하지 않는다.
- 활성 경기 상태와 명령 직렬화는 단일 프로세스에서 처리한다.

## Object Storage와 정적 자산

- 사용자 이미지 업로드는 MVP 제외다.
- 카드 이미지는 현재 `docs/cards` 원본과 FE 정적 자산 경계에 있으며 object storage는 미확정이다.
- 카드 정의 JSON과 활성 버전 목록은 애플리케이션 산출물에 포함하며 외부 object storage를 요구하지 않는다.

## Secret과 환경 설정

- `local`, `test`, `prod` Spring profile을 분리한다.
- DB, SMTP, OAuth, 보안 secret은 환경 변수로 주입한다.
- CI secret은 GitHub Actions Secrets를 사용한다.
- 운영 Secret Manager는 제공자 선택 뒤 결정한다.

## Environment Strategy

- 공통 설정에는 secret을 저장하지 않는다.
- local은 `.env` 또는 IDE 환경 변수, test는 전용 test 설정, prod는 배포 환경 주입을 사용한다.

## 관측 인프라

- Actuator health/readiness/liveness와 Prometheus endpoint를 제공한다.
- endpoint는 public internet에 직접 노출하지 않는다.
- Grafana, alert routing, log aggregation 제품은 미확정이다.

## 구조화 로깅과 로그 집계

- request/game/event correlation ID를 포함한 구조화 로그를 사용한다.
- 비밀번호, token, cookie, CSRF, 이메일 원문, 채팅/게시글 원문, RNG seed는 로그·메트릭·오류 응답에 남기지 않는다.

## 메트릭, 알림, 대시보드

- 운영 메트릭은 로그인 실패, Rate Limit, STOMP 실패, 카드팩, 신고·제재, 경기 종료, 활성 경기, WebSocket 연결, 명령 실패·지연을 포함한다.
- 카드별 사용/승리와 체크메이트 기물 통계는 Prometheus label이 아닌 MySQL 집계 read model에 저장한다.
- alert 임계치와 dashboard 구현은 제공자·SLO 확정 뒤 결정한다.

## Capacity/Cost Guardrail

- 현재 트래픽 목표와 비용 상한은 미확정이다.
- CD와 클라우드 제공자 확정 전 재인터뷰에서 capacity, 비용, SLO를 결정한다.

## 백업과 복구 정책

- 종료된 영속 데이터는 provider native backup/PITR로 보호한다.
- backup 보존, RPO/RTO, restore drill은 미확정이다.
- 활성 경기는 서버 장애 시 `SERVER_ABORTED` 또는 `NO_RESULT`로 무효 처리한다.

## MVP 제외 확장 후보

- Redis session/cache, STOMP pub/sub, 다중 인스턴스, 분산 timer/lock/queue, external active-game store
- CDN, object storage, managed analytics warehouse

## 후속 스킬 연계

- 클라우드 제공자 확정 시 architecture-decision 재실행
- RPO/RTO, SLO, 비용 상한 확정 시 spec 인터뷰

## Repo 설정 반영

- 인프라 provider가 미확정이므로 Dockerfile, IaC, deploy manifest는 아직 만들지 않는다.

## 미확정 사항

- provider, compute, managed DB, registry, Secret Manager, log aggregation, Grafana, alerting

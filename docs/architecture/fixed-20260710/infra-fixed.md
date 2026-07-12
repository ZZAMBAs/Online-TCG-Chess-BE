# Infrastructure Architecture Fixed

## 확정된 결정

- MVP는 단일 백엔드 인스턴스와 단일 writer로 운영한다.
- HTTPS same-origin reverse proxy가 TLS를 종료하고 FE, REST, STOMP를 라우팅한다.
- CDN, Redis, pub/sub, queue, 분산 timer, 다중 인스턴스 STOMP는 MVP에 도입하지 않는다.
- MySQL 호환 RDB를 사용하며 종료 경기·계정·카드/덱·신고·감사·analytics 집계 데이터를 영속화한다.
- 활성 경기는 재시작 후 완전 복구하지 않고 명세의 `SERVER_ABORTED` 또는 `NO_RESULT` 처리로 종료한다.
- 실행 JAR를 기본 artifact로 사용하고 OCI container image로의 전환 가능성은 유지한다.
- `local`, `test`, `prod` profile과 환경 변수 secret 주입을 사용한다.
- Actuator health/readiness/liveness, Prometheus endpoint, 구조화 로그를 앱 레벨에서 제공한다.
- 운영 메트릭과 카드 분석 통계 저장소를 분리한다.
- DB backup/PITR은 선택된 provider의 native 기능을 사용한다.

## 문서화 가정

- reverse proxy, DB, monitoring은 선택한 provider의 사설/제한 네트워크 경계 안에 배치한다.

## 미확정 또는 상위 산출물 재검토

- cloud provider, compute, managed DB, registry, Secret Manager, Grafana/log aggregation/alerting
- RPO/RTO, backup 보존 기간, restore drill, SLO, 비용 상한, 트래픽 목표
- CD, Dockerfile, IaC, migration deployment, smoke test, rollback

## 후속 스킬 연계

- provider/CD 확정 시 `architecture-decision` 재실행
- RPO/RTO/SLO/비용/트래픽 목표 확정 시 `spec-interview`

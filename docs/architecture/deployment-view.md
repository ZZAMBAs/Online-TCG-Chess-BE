# Deployment View

## 목적

클라우드 제공자 미확정 상태에서 MVP가 요구하는 논리적 배포 topology를 보여준다.

## 전체 배포 Topology

```text
Browser
  |
HTTPS same origin
  v
Reverse Proxy / TLS termination
  |--------------------> FE static assets
  |
  | REST + WebSocket upgrade
  v
Spring Boot single instance
  |-- packaged card catalog / active-version manifest
  |
  v
MySQL compatible RDB
```

## 네트워크 경계

- reverse proxy가 외부 HTTPS와 WebSocket upgrade를 처리한다.
- Spring Boot와 MySQL은 provider 내부 또는 제한된 네트워크 경계에 둔다.
- Actuator와 Prometheus endpoint는 public internet에 직접 노출하지 않는다.

## 컴퓨팅 구성

- 단일 Spring Boot instance와 단일 writer를 사용한다.
- 실행 JAR를 기본 artifact로 사용한다.
- VM, PaaS, container runtime은 미확정이다.

## 데이터 저장소 구성

- MySQL 호환 RDB: domain data, 모든 배포 카드 버전과 활성 버전, GameEvent, GameSnapshot, audit, read model aggregate
- 애플리케이션 산출물: 검증된 카드 catalog와 활성 버전 목록
- 활성 경기: Spring Boot process memory
- Redis, queue, NoSQL, data warehouse: MVP 미도입

## 캐시와 메시징 구성

- Spring WebSocket/STOMP를 단일 인스턴스에서 처리한다.
- Redis pub/sub, distributed session, broker는 미도입이다.

## 관측 구성

- Spring Boot Actuator와 Prometheus endpoint를 앱이 제공한다.
- 구조화 로그와 분석 read model을 분리한다.
- Grafana, log aggregation, alerting은 provider 확정 후 연결한다.

## 환경별 차이

- local/test/prod profile을 사용한다.
- 각 환경의 secret은 환경 변수로 주입한다.
- provider 선택 전 deployment manifest와 runtime-specific 설정은 만들지 않는다.

# Architecture Traceability

| 결정 | 출처 산출물 | 출처 섹션 | 반영 문서 | 상태 |
| --- | --- | --- | --- | --- |
| 모듈러 모놀리스 + 헥사고날 | architecture interview | 2026-07-10 인터뷰 | `server-architecture.md` | 확정 |
| 기능 우선 8개 모듈 | PRD | 기능 PRD map | `server-architecture.md` | 확정 |
| MySQL + JPA + Flyway | build/spec/interview | JPA/MySQL 의존성, 저장 원칙 | `server-architecture.md`, `infrastructure-architecture.md` | 확정 |
| GameEvent + Snapshot + 메모리 활성 경기 | spec/interview | 경기 저장·재시작 원칙 | `server-architecture.md`, `deployment-view.md` | 확정 |
| Redis/queue 미도입 | spec/interview | MVP 단일 인스턴스 제약 | `infrastructure-architecture.md` | 확정 |
| 세션 쿠키 + Spring Security + STOMP 검증 | spec/interview | 인증·실시간 통신 | `server-architecture.md` | 확정 |
| 단일 origin reverse proxy/TLS | spec/interview | same-site 배포 | `infrastructure-architecture.md`, `deployment-view.md` | 확정 |
| GitHub Actions CI, CD 보류 | interview | CI/CD 결정 | `cicd-architecture.md` | 확정 |
| ArchUnit/Spotless Hard gate | interview | AI 하네스 결정 | `harness-guardrails.md` | 확정 |
| Conditional static analysis/test tools | interview | AI 하네스 결정 | `harness-guardrails.md` | 확정 |
| OpenAPI + STOMP schema/fixture | spec/interview | 인터페이스 안정성 | `harness-guardrails.md`, `cicd-architecture.md` | 확정 |
| Actuator/Prometheus/structured log | spec/interview | 운영·보호 장치 | `infrastructure-architecture.md` | 확정 |
| GameEvent 기반 card analytics read model | spec/interview | 주요 메트릭·저장 원칙 | `server-architecture.md`, `infrastructure-architecture.md` | 확정 |
| 클라우드 제공자와 CD | interview | 운영 미확정 | `infrastructure-architecture.md`, `cicd-architecture.md` | 재인터뷰 |
| RPO/RTO/SLO/비용/트래픽 목표 | interview | 운영 미확정 | `infrastructure-architecture.md` | spec 재검토 |

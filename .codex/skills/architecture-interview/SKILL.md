---
name: architecture-interview
description: 서버 아키텍처 스타일(layered, clean, hexagonal, DDD, modular monolith, monolith, MSA 등), 인프라 아키텍처(AWS/GCP/Azure, VM/PaaS/Kubernetes, CDN, Redis/ElastiCache, RDS/Cloud SQL, DB/NoSQL 등), CI/CD, AI 하네스 방어 장치를 한국어 인터뷰로 자세히 확정하고 승인 후 docs/architecture 문서로 생성·갱신해야 할 때 사용한다. 기존 spec/prd/trd/websocket/architecture 산출물과 현재 구현 코드를 읽고, 아키텍처 선택지를 직접 도출해 한 번에 하나씩 충분히 많은 질문과 추천안을 제시해야 할 때 사용한다.
---

# Architecture Interview

## 개요

서버 아키텍처 스타일, 인프라 아키텍처, CI/CD, AI 하네스 품질 게이트 결정을 한국어 인터뷰로 구체화하고, 승인된 결정은 `docs/architecture/` 문서로 생성하거나 갱신한다. PRD/TRD가 다룰 기능별 상세 요구사항을 다시 묻지 않고, 구현과 운영의 큰 구조를 결정한다.

## 기본 원칙

- 모든 질문과 요약은 한국어로 작성한다.
- 질문은 반드시 한 번에 하나만 한다.
- 질문은 충분하다고 판단될 때까지 최대한 많이 한다.
- 이미 확정된 결정은 다시 묻지 않는다. 다만 기존 산출물, 현재 코드, 새 답변이 충돌하면 확인 질문을 한다.
- 기존 스킬 산출물이 있으면 반드시 먼저 읽고 재사용한다.
- 현재 구현 코드와 구현된 기능 범위를 확인해 질문 범위를 확장하거나 축소한다.
- 아직 구현되지 않은 영역은 아키텍처 후보로 다루고, 이미 구현된 영역은 문서와 코드 drift를 확인한다.
- 기능 상세, API payload, DB column, 카드 효과, 화면 문구처럼 PRD/TRD에서 다룰 사항은 아키텍처 질문으로 확정하지 않는다.
- 질문 은행 파일에 의존하지 않는다. 읽은 산출물과 현재 코드에서 필요한 아키텍처 질문을 직접 생성한다.
- 요구사항 변경이 필요하면 직접 수정하지 않고 `상위 산출물 재검토 필요`로 기록한다.
- 파일 작성 전에는 반영 예정 요약을 세션에 제시하고 승인받는다.
- 개별 스킬 내부에 전체 워크플로우 순서를 강제하지 않는다.

## 먼저 확인할 자료

존재하는 파일만 읽는다.

- `docs/spec/spec-fixed.md`
- `docs/prd.md`, `docs/trd.md`, `docs/websocket-spec.md`
- `docs/features/*/prd.md`, `docs/features/*/trd.md`
- `docs/architecture/*`
- `harness-guardrails-review.tmp.md`
- `build.gradle`, `settings.gradle`, `src/main`, `src/test`
- `.github`, `Dockerfile`, `docker-compose*`, `infra`, `deploy`, `k8s` 등 CI/CD 또는 인프라 설정

## 질문 방식

각 질문은 다음 형식을 유지한다.

```markdown
질문: [하나의 구체적인 아키텍처 결정 질문]

추천 답변: [현재 프로젝트 맥락에서 권장하는 선택]

추천 이유: [서버/인프라/보안/운영/하네스 관점의 근거]

영향받는 문서: [예: server-architecture.md, cicd-architecture.md]

상위 산출물 재검토 필요: [없음 또는 spec/prd/trd/websocket 중 필요한 항목과 이유]
```

사용자가 "추천대로", "계속", "알아서"처럼 위임하면 추천 답변을 채택하고 다음 질문으로 넘어간다.

## 질문 생성 범위

자료를 읽은 뒤 다음 범위에서 필요한 질문을 직접 생성한다. 각 질문은 선택지를 2-4개로 좁히고, 현재 프로젝트 기준 추천안을 함께 제시한다.

### 서버 아키텍처

- 전체 구조 선택: monolith, layered monolith, clean architecture, hexagonal architecture, DDD tactical patterns, modular monolith, MSA 중 무엇을 채택할지 묻는다.
- 모듈 경계: 기능별 패키지, 계층별 패키지, bounded context, module API 공개 범위를 묻는다.
- 의존성 방향: domain/application/adapter/infrastructure 간 허용 의존성과 금지 의존을 묻는다.
- 트랜잭션 책임 위치: controller/handler, application service, domain service, repository 중 어느 계층이 트랜잭션 정책을 소유할지 묻는다.
- 어댑터 구조: REST, WebSocket/STOMP, persistence, external API adapter를 서버 프로젝트 구조에서 어디에 둘지 묻는다.
- 데이터 저장 아키텍처: RDB 중심, event log, snapshot, cache, read model, NoSQL 중 어떤 저장소 역할 구분을 둘지 묻는다.
- 확장 방식: 단일 인스턴스 유지, modular monolith 확장, Redis 기반 분산화, MSA 전환 조건을 묻는다.

### 인프라 아키텍처

- 클라우드/호스팅 선택: AWS, GCP, Azure, 온프레미스, PaaS, 단일 VM 중 어떤 방향인지 묻는다.
- 컴퓨팅 선택: EC2/Compute Engine/VM, container service, Kubernetes, PaaS 중 무엇을 쓸지 묻는다.
- 네트워크와 edge: reverse proxy, load balancer, CDN, TLS termination, same-site FE/BE 배포 방식을 묻는다.
- 데이터베이스 선택: MySQL/PostgreSQL, RDS/Cloud SQL/Azure Database, 자체 운영 DB, NoSQL 필요 여부를 묻는다.
- 캐시와 메시징: Redis/ElastiCache/Memorystore, pub/sub, queue 도입 여부와 MVP 제외 여부를 묻는다.
- 정적 자산과 파일: CDN, object storage, 이미지 업로드가 필요할 때의 확장 방향을 묻는다.
- secret과 설정: cloud secret manager, 환경 변수, CI secret, local dev secret 방식을 묻는다.
- 관측과 운영: Prometheus/Grafana, cloud monitoring, log aggregation, alert, backup, disaster recovery 범위를 묻는다.

### CI/CD와 AI 하네스

- branch protection, required checks, 배포 승인, rollback 기준을 묻는다.
- 서버 아키텍처를 정적 분석으로 강제할 도구와 범위를 묻는다.
- FE가 있거나 생길 예정이면 FE typecheck/lint/e2e/contract drift gate를 묻는다.

## PRD/TRD로 넘길 항목

다음은 아키텍처 인터뷰에서 확정하지 말고 상위 또는 feature 문서 재검토 대상으로 표시한다.

- 사용자 기능 포함/제외 범위
- 상세 API endpoint, payload, 필드명
- DB 테이블/컬럼의 상세 schema
- 카드 효과, 체스 규칙, MMR 공식 등 도메인 정책값
- 화면 문구, UI layout, 세부 UX
- 오류 코드의 개별 명칭과 상세 메시지
- feature별 테스트 케이스의 구체 입력값

## AI 하네스 질문 필수 조건

서버 아키텍처를 논의할 때는 다음 도구 또는 동등한 대안을 적용할지 반드시 질문한다.

- ArchUnit
- Spotless
- PMD
- SpotBugs 또는 FindSecBugs
- JaCoCo coverage verification
- Gradle dependency locking 및 verification
- Testcontainers
- Spring Security Test
- FE가 있으면 TypeScript strict, type-aware ESLint, dependency-cruiser, Vitest, Playwright

각 도구는 `Hard gate`, `Conditional gate`, `Advisory` 중 하나로 분류하고, CI에서 실패시킬 수 있는지 확인한다.

## 생성 또는 갱신할 문서

승인된 결정은 다음 구조로 문서화한다. 상세 섹션은 `references/document-templates.md`를 읽고 따른다.

```text
docs/architecture/
  server-architecture.md
  infrastructure-architecture.md
  cicd-architecture.md
  deployment-view.md
  harness-guardrails.md
  architecture-decisions.md
  architecture-traceability.md
  architecture-review-ledger.md
```

## 문서 작성 규칙

- 확정된 결정과 문서화 가정을 구분한다.
- 원천 문서에 없는 값을 임의 확정하지 않는다.
- 확정되지 않은 항목은 `미확정` 또는 `아키텍처 후보`로 표시한다.
- 기존 아키텍처 문서가 있으면 먼저 읽고 갱신한다.
- 문서와 구현이 충돌하면 drift로 기록한다.
- Redis, CDN, object storage, Kubernetes, managed DB 등 인프라 구성 요소는 확정되지 않았다면 MVP 아키텍처처럼 쓰지 않는다.
- CI에서 실패시킬 수 있는 하드 게이트와 보조 도구를 구분한다.

## 문서 반영 전 요약

충분한 답변이 모이면 파일을 쓰기 전에 다음을 세션에서 요약하고 명확한 승인을 받는다.

- 확정된 서버 아키텍처 결정
- 확정된 인프라/CI/CD 결정
- 확정된 AI 하네스/정적 분석 결정
- 미확정 사항
- 상위 산출물 재검토 필요 항목
- 생성 또는 갱신할 아키텍처 문서

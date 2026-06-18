# Architecture Document Templates

이 문서는 `architecture-interview`가 승인된 아키텍처 결정을 문서화할 때 사용하는 템플릿이다.

## server-architecture.md

```markdown
# Server Architecture

## 목적
## 원천 산출물
## 현재 구현 기준
## 서버 아키텍처 스타일
## 프로젝트 디렉터리 구조
## 패키지와 모듈 경계
## 레이어와 의존성 방향
## 어댑터 배치 구조
## 빌드 모듈 구성
## 보안 경계의 코드 배치
## 정적 분석과 강제 규칙
## 테스트와 품질 게이트
## 미확정 사항
```

## infrastructure-architecture.md

```markdown
# Infrastructure Architecture

## 목적
## 원천 산출물
## MVP 인프라 전제
## 클라우드와 호스팅 선택
## 컴퓨팅과 배포 단위
## 네트워크, TLS, Load Balancer, CDN
## FE/BE 배포와 라우팅
## 데이터베이스 선택과 운영
## Redis/Cache/Message Broker 선택
## Object Storage와 정적 자산
## Secret과 환경 설정
## 관측 인프라
## 백업과 복구 정책
## MVP 제외 확장 후보
## 미확정 사항
```

## cicd-architecture.md

```markdown
# CI/CD Architecture

## 목적
## 원천 산출물
## 브랜치와 머지 정책
## Required Checks
## Backend CI
## Frontend CI
## 보안과 공급망 검사
## Migration 검증과 배포 순서
## Artifact와 버전
## Rollback 정책
## Secret 처리
## 미확정 사항
```

## deployment-view.md

```markdown
# Deployment View

## 목적
## 전체 배포 Topology
## 네트워크 경계
## 컴퓨팅 구성
## 데이터 저장소 구성
## 캐시와 메시징 구성
## 관측 구성
## 환경별 차이
```

## harness-guardrails.md

```markdown
# Harness Guardrails

## 목적
## Hard Gate
## Conditional Gate
## Advisory 도구
## Backend 강제 규칙
## Frontend 강제 규칙
## CI Required Check
## 도입 전 PoC 항목
## 미확정 사항
```

## architecture-decisions.md

```markdown
# Architecture Decisions

## ADR-lite 형식

### ADR-{번호}. {결정 제목}

- 상태:
- 배경:
- 선택지:
- 결정:
- 포기한 대안:
- 영향:
- 재검토 조건:
```

## architecture-traceability.md

```markdown
# Architecture Traceability

| 결정 | 출처 산출물 | 출처 섹션 | 반영 문서 | 상태 |
| --- | --- | --- | --- | --- |
```

## architecture-review-ledger.md

`architecture-review`의 `references/review-ledger-schema.md` 형식을 따른다.


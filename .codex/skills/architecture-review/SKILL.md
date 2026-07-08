---
name: architecture-review
description: 서버 프로젝트 구조와 인프라스트럭처 아키텍처 문서 및 repo 설정을 한국어로 검토하고 승인 후 보완해야 할 때 사용한다. 기존 architecture-review-ledger와 현재 산출물·구현 코드 fingerprint를 비교해 변경 없는 영역은 생략하고, 서버 구조 스타일, 모듈/패키지 경계, 클라우드/컴퓨팅/네트워크/DB/캐시/CDN/CI-CD/AI 하네스 중 조금이라도 바뀐 영역은 재검토해야 할 때 사용한다.
---

# Architecture Review

## 개요

서버 프로젝트 구조와 인프라스트럭처 아키텍처 산출물을 변경 영향 기반으로 검토하고, 승인된 보완 사항은 아키텍처 문서에 반영한다. 매번 전체를 재검토하지 않고, 이전 리뷰 이후 바뀐 영역만 깊게 본다.

## 기본 원칙

- 모든 검토와 요약은 한국어로 작성한다.
- 기존 `docs/architecture/architecture-review-ledger.md`가 있으면 먼저 읽는다.
- 리뷰 단위는 문서 전체가 아니라 아키텍처 영역이다.
- 변경 없는 영역은 생략할 수 있다.
- 관련 요구사항, PRD/TRD, 인터페이스 계약, 아키텍처 결정, 구현 코드, 의존성, CI/CD, 인프라 설정 중 하나라도 바뀌면 생략하지 않는다.
- 생략한 영역도 생략 사유와 재검토 조건을 남긴다.
- 파일 작성 전에는 반영 예정 요약을 세션에 제시하고 승인받는다.
- 승인된 리뷰 결과가 문서와 repo 설정의 drift를 함께 고쳐야 하는 경우, 승인 범위 안에서 관련 repo 설정과 검증 파일도 직접 반영한다.
- 개별 스킬 내부에 전체 워크플로우 순서를 강제하지 않는다.
- ADR 작성, issue 분리, 심층 보안 리뷰, 운영 runbook 작성은 직접 수행하지 않고 후속 스킬 연계 항목으로 표시한다.

## 먼저 확인할 자료

존재하는 파일만 읽는다.

- `docs/spec/spec-fixed.md`
- `docs/prd.md`, `docs/trd.md`, `docs/websocket-spec.md`
- `docs/features/*/prd.md`, `docs/features/*/trd.md`
- `docs/architecture/*`
- `build.gradle`, `settings.gradle`, `src/main`, `src/test`
- `.github`, `Dockerfile`, `docker-compose*`, `infra`, `deploy`, `k8s`

## Fingerprint

필요하면 `scripts/architecture_fingerprint.py`를 사용해 관련 파일과 디렉터리의 fingerprint를 계산한다.

```powershell
python .codex\skills\architecture-review\scripts\architecture_fingerprint.py docs\spec\spec-fixed.md build.gradle src\main
```

이 스크립트는 읽기 전용이어야 하며 repo 파일을 수정하지 않는다.

## 리뷰 영역

다음 영역별로 검토한다.

- 서버 아키텍처 스타일
- 프로젝트 디렉터리와 패키지 구조
- 모듈 경계와 의존성 방향
- 어댑터 배치 구조
- 클라우드/호스팅 선택
- 컴퓨팅과 배포 단위
- 네트워크, TLS, CDN
- DB, 캐시, 메시징, 파일 저장소
- 보안 경계와 secret 관리
- 운영 관측 인프라
- CI/CD
- AI 하네스와 정적 분석
- environment strategy
- release gates
- operational readiness gates
- observability gates
- quality gates
- 확장 전략과 전환 조건

## 생략 가능 조건

다음이 모두 참이면 해당 영역은 생략할 수 있다.

- 관련 원천 문서가 변하지 않았다.
- 관련 PRD/TRD 또는 인터페이스 계약이 변하지 않았다.
- 관련 아키텍처 결정이 변하지 않았다.
- 관련 구현 코드가 변하지 않았다.
- 관련 의존성, CI/CD, 인프라 설정이 변하지 않았다.
- 이전 결정과 현재 문서가 충돌하지 않는다.

## 생략 금지 조건

다음 중 하나라도 참이면 재검토한다.

- 요구사항이 바뀌었다.
- 구현 코드가 문서와 다르다.
- 프로젝트 구조, 모듈 경계, 의존성 방향이 바뀌었다.
- 클라우드 제공자, 컴퓨팅 방식, DB/캐시/CDN/메시징 선택이 바뀌었다.
- 배포, 장애/복구, 백업 정책이 바뀌었다.
- environment strategy, release gate, operational readiness gate, observability gate, quality gate가 바뀌었다.
- 보안 정책, secret 처리, actuator 접근, CI required check가 바뀌었다.
- 의존성 또는 배포 방식이 바뀌었다.
- 이전에 `미확정`이던 항목이 확정되었다.

## Redis 등 기존 결정 재검토 규칙

Redis, ElastiCache, Memorystore, queue, pub/sub, RDS, Cloud SQL, Kubernetes처럼 비용이 큰 인프라 결정을 이미 검토했다면, 관련 입력이 완전히 같을 때는 상세 리뷰를 생략한다. 서비스 역할, managed/self-hosted 여부, 네트워크 배치, 운영 정책, 장애 정책, 요구사항 중 하나라도 바뀌면 서버 구조/인프라/SRE/보안/하네스 관점으로 다시 검토한다.

## 종합 응답 형식

```markdown
검토 범위:
- [검토한 영역]
- [생략한 영역과 사유]

핵심 이슈:
- [문제 또는 충돌]

추천 확정안:
- [반영할 정책 또는 문장]

재검토 필요:
- [상위 산출물 또는 아키텍처 영역]

Ledger 반영 후보:
- [area, fingerprint, skip_conditions, re_review_triggers 요약]
```

`references/review-ledger-schema.md`를 읽고 ledger 필드를 맞춘다.

## 문서 보완 규칙

- 사용자 승인 전에는 파일을 수정하지 않는다.
- 승인된 리뷰 결과만 `docs/architecture/*`에 반영한다.
- 승인된 리뷰 결과가 하네스/CI/정적 분석/인프라 설정 drift를 지적하면 `build.gradle`, `settings.gradle`, `.github/workflows/*`, 정적 분석/하네스 설정 파일, `src/test`의 아키텍처/하네스 검증 테스트, `Dockerfile`, `docker-compose*`, `infra`, `deploy`, `k8s`, `src/main/resources`의 아키텍처성 설정에 직접 반영할 수 있다.
- 기존 문서를 덮어쓰기보다 검토 결과에 맞춰 갱신한다.
- 원천 문서에 없는 값을 임의 확정하지 않는다.
- 기능 구현, 도메인 정책 구현, controller/service/repository production 기능 코드는 작성하지 않는다.
- 요구사항, PRD/TRD, 인터페이스 계약 변경이 필요하면 직접 수정하지 않고 재검토 필요 항목으로 남긴다.
- ADR 작성, 심층 보안 리뷰, 운영 runbook 작성이 필요하면 후속 스킬 연계 항목으로 남긴다.
- `architecture-review-ledger.md`에는 검토한 영역, 생략한 영역, 생략 사유, fingerprint, 재검토 조건을 남긴다.

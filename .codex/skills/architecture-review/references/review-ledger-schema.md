# Architecture Review Ledger Schema

`architecture-review-ledger.md`는 변경 없는 영역을 안전하게 생략하기 위한 기록이다.

## 권장 섹션

```markdown
# Architecture Review Ledger

## 목적

## 리뷰 영역 요약

| area | last_reviewed_at | decision_summary | skipped_this_run | skip_reason |
| --- | --- | --- | --- | --- |

## 영역별 상세

### {area}

- last_reviewed_at:
- source_documents:
- source_fingerprint:
- implementation_paths:
- implementation_fingerprint:
- decision_summary:
- skip_conditions:
- re_review_triggers:
- latest_result:
```

## area 후보

- server-architecture-style
- project-package-structure
- module-boundaries
- adapter-placement
- cloud-hosting
- compute-deployment-unit
- network-tls-cdn
- data-cache-messaging-storage
- security-secret-boundary
- operations-observability-infra
- cicd
- harness-guardrails
- environment-strategy
- release-gates
- operational-readiness-gates
- observability-gates
- quality-gates
- scalability-transition

## 생략 조건 작성 기준

생략 조건은 구체적인 path와 결정 요약을 포함한다. "변경 없음"처럼 막연하게 쓰지 않는다.

## 재검토 조건 작성 기준

다음 변화는 반드시 재검토 조건에 포함한다.

- 관련 요구사항 변경
- 관련 PRD/TRD 또는 인터페이스 계약 변경
- 관련 코드 또는 의존성 변경
- CI/CD 또는 인프라 설정 변경
- 보안 정책 또는 secret 처리 변경
- 클라우드 제공자, 컴퓨팅 방식, 네트워크, DB, 캐시, CDN, 메시징 선택 변경
- environment strategy, release gate, operational readiness gate, observability gate, quality gate 변경
- 미확정 항목 확정

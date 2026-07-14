---
id: "ARCH-ADR-001"
status: "accepted"
decision_scope: "infrastructure"
fixed_reference: "docs/architecture/fixed-20260710/infra-fixed.md"
supersedes: []
source_documents:
  - "docs/spec/spec-fixed.md"
  - "docs/architecture/interview-20260710/interview-log.md"
  - "docs/architecture/interview-20260710/final-summary.md"
  - "docs/architecture/fixed-20260710/impl-fixed.md"
  - "docs/architecture/fixed-20260710/infra-fixed.md"
---

# ARCH-ADR-001. MVP 활성 경기를 단일 인스턴스 메모리에 유지

## Context

2026-07-10 아키텍처 인터뷰와 확정본은 MVP를 단일 백엔드 인스턴스·단일 writer로 운영하고, 활성 경기는 단일 프로세스 메모리에 둔다고 결정했다. 제품 요구사항도 서버 재시작 또는 crash로 활성 경기가 유실될 때 `SERVER_ABORTED` 또는 `NO_RESULT`로 무효 처리하고 전적과 MMR에 반영하지 않도록 명시한다.

같은 원천은 수평 확장, Redis/pub-sub 기반 상태 공유, 다중 인스턴스 STOMP, 분산 타이머, 외부 활성 경기 저장소와 복구를 MVP 이후 확장으로 둔다. 이러한 확장은 이벤트 순서, 중복 처리, 단일 writer 보장, 장애 복구, STOMP 세션 라우팅 정책을 별도로 정의해야 한다.

## Decision

MVP에서는 활성 경기 상태를 단일 백엔드 인스턴스의 프로세스 메모리에 두고, Redis/pub-sub·외부 메시지 브로커·분산 타이머·다중 인스턴스 STOMP·활성 경기 외부 저장소 복구를 도입하지 않는다.

이 결정은 MVP가 1:1 PvP 완성에 집중하고 단일 인스턴스·단일 writer를 전제하며, 재시작 후 활성 경기 완전 복구를 요구하지 않는 현재 요구사항과 일치한다. 종료된 경기의 결과와 기보는 계속 영속화하되, 활성 경기 유실은 명세의 무효 처리 규칙으로 다룬다.

## Alternatives

| 대안 | 장점 | 단점/위험 | 현재 상황에서의 적합성 | 선택 또는 제외 이유 |
| --- | --- | --- | --- | --- |
| 단일 인스턴스 프로세스 메모리 활성 경기 상태 | 단일 writer 전제와 일치하며, MVP의 서버 권위 경기 흐름을 추가 분산 조정 없이 운영할 수 있다. | 재시작·crash 뒤 활성 경기의 완전 복구를 제공하지 못한다. | MVP는 단일 인스턴스를 전제하고 완전 복구를 필수 요구사항으로 두지 않는다. | 선택. 유실 시 `SERVER_ABORTED` 또는 `NO_RESULT` 무효 처리라는 제품 규칙이 이미 확정되어 있다. |
| Redis/pub-sub, 다중 인스턴스 STOMP, 분산 타이머를 통한 수평 확장 | 다중 인스턴스와 상태 공유를 위한 기반을 제공할 수 있다. | 이벤트 순서, 중복 처리, 단일 writer 보장, STOMP 세션 라우팅을 별도로 정의해야 한다. | 현재 MVP 범위에서 제외되어 있으며, 트래픽·SLO·다중 인스턴스 요구가 아직 확정되지 않았다. | 제외. 해당 요구가 생기면 별도 아키텍처 결정으로 재검토한다. |
| 활성 경기 상태 외부 저장소와 복구 고도화 | 재시작 또는 장애 뒤 활성 경기 복구를 목표로 할 수 있다. | 복구 정책과 장애 처리 기준을 별도로 정의해야 하며, 현재 무효 처리 규칙을 바꾼다. | MVP는 활성 경기 완전 복구를 요구하지 않고 무효 처리 규칙을 이미 가진다. | 제외. 무중단 배포 또는 활성 경기 복구가 제품 요구사항이 될 때 재검토한다. |

## Consequences

- 활성 경기 상태는 서버 재시작 또는 crash에서 보존되지 않는다.
- 유실된 활성 경기는 `SERVER_ABORTED` 또는 `NO_RESULT`로 처리하고 전적과 MMR에 반영하지 않는다.
- 종료된 경기 결과와 기보는 DB에 보존하며, 활성 경기 상태와 구분한다.
- 단일 인스턴스의 CPU·메모리·WebSocket 연결·명령 지연이 운영 목표를 충족하지 못하거나, 다중 인스턴스·Redis session·STOMP pub/sub·분산 lock/queue가 필요해지면 `$architecture-decision`을 다시 수행한다.

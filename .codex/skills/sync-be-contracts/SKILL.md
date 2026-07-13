---
name: sync-be-contracts
description: Online-TCG-Chess-BE에서 FE/BE 전체 계약 협상이 completed로 끝난 뒤 fixed negotiation summary를 BE 구현 계약으로 동기화해야 할 때 사용한다. REST API, STOMP/WebSocket, 인증/CSRF/cookie, 오류 포맷, 상태 동기화, projection, contract test, fixture 등 모든 확정 topic의 BE 규약을 docs/contracts/{topic}.md로 투영하며, 부분 협상 상태에서는 동기화를 차단해야 할 때 사용한다.
---

# Sync BE Contracts

## 개요

`docs/negotiation/session.md`가 전체 계약 협상 완료를 뜻하는 `completed`일 때만, topic별 `summarize.md`에서 BE 구현에 필요한 규약을 `docs/contracts/{topic}.md`에 저장한다. 협상 절차, 과정 기록, 승인 이력, 원본 추적은 `$negotiate-fe-be-contract`와 `docs/negotiation`이 담당하므로 이 스킬은 전체 협상 완료 뒤 BE 구현자가 꺼내 볼 결정된 계약 정보만 남긴다.

## 기본 원칙

- 모든 질문, 분석, 기록은 한국어로 작성한다.
- 새 계약을 만들거나 협상하지 않는다.
- `docs/negotiation/session.md`의 `status: completed`를 전체 동기화의 선행 hard gate로 사용한다.
- 하나의 topic이 `fixed`여도 session이 `completed`가 아니면 부분 sync하지 않는다.
- topic은 계약 분류명이 아니라 FE/BE 협의 주제명이다.
- `docs/contracts/{topic}.md`에는 그 topic에서 BE가 알아야 할 결정 사항만 저장한다.
- 원본 경로, source_artifacts, supersedes, 협상 과정, 사용자 결정 이력은 복사하지 않는다.
- `summarize.md`가 `fixed`가 아니면 구현 가능한 계약처럼 정리하지 않는다.
- production code, test code, PRD/TRD, architecture, `docs/negotiation` 원문은 수정하지 않는다.
- 계약 동기화가 끝나면 `docs/negotiation/*/summarize.md`와 `docs/contracts/*.md`의 fingerprint를 기록한다.

## 입력 범위

먼저 `docs/negotiation/session.md`를 읽는다. 파일이 없거나 `status: completed`가 아니면 어떤 `docs/contracts/*.md`도 생성·갱신하지 않고 `$negotiate-fe-be-contract`를 계속해야 한다고 보고한다.

session이 `completed`이면 모든 `docs/negotiation/*/summarize.md`를 스캔한다. 하나라도 없거나 형식을 해석할 수 없거나 `fixed`가 아니면 전체 sync를 차단하고 어떤 계약 파일도 수정하지 않는다.

전체 gate가 통과한 뒤 사용자가 topic을 지정하면 해당 topic만 처리할 수 있다. topic이 없으면 모든 fixed topic을 처리한다.

먼저 다음만 읽는다.

1. `docs/negotiation/session.md`
2. 모든 `docs/negotiation/*/summarize.md`의 상태
3. 대상 `docs/negotiation/{topic}/summarize.md`
4. 이미 존재하는 `docs/contracts/{topic}.md`
5. 필요할 때만 관련 `docs/spec/spec-fixed.md`, `docs/websocket-spec.md`, `docs/trd.md`, `docs/features/*/trd.md`

`session.md`가 `completed`가 아니거나 summarize 전체 집합에 문제가 있으면 문서를 만들지 말고 차단 사유를 보고한다. 부분 협상 상태를 `docs/contracts/{topic}.md`의 blocked 문서로 투영하지 않는다.

## 출력 구조

topic마다 하나의 Markdown 파일만 사용한다.

```text
docs/contracts/
  {topic}.md
```

모든 topic에 API, 보안, 검증 같은 고정 분류 파일을 만들지 않는다. topic 파일 안에서 필요한 섹션만 사용하고, 내용이 없는 섹션은 생략한다.

## 문서 형식

`docs/contracts/{topic}.md`는 다음 구조를 기본으로 한다.

```markdown
# {Topic} BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

## REST 계약

## STOMP/WebSocket 계약

## 인증/보안/노출 제한

## 상태 동기화와 서버 권위

## 오류 포맷과 사용자 표시 영향

## 테스트/fixture/드리프트 검증

## 구현 메모

```

섹션 의미는 다음과 같다.

- `BE가 지켜야 할 결정`: topic의 핵심 합의를 BE 구현 관점으로 요약한다.
- `REST 계약`: endpoint, method, request/response, status, error envelope, pagination, 검색, 정렬, 날짜/시간 표현을 적는다.
- `STOMP/WebSocket 계약`: destination, command/event, payload, subscription, ack, error event, reconnect/disconnect 동작을 적는다.
- `인증/보안/노출 제한`: cookie, CSRF, Origin/CORS, 권한/소유권, rate limit, masking, 공개/비공개 projection을 적는다.
- `상태 동기화와 서버 권위`: `stateVersion`, `actionId`, `commandId`, pending, rollback, resync, idempotency, concurrency를 적는다.
- `오류 포맷과 사용자 표시 영향`: FE가 분기하거나 표시할 오류 코드, 메시지 노출 범위, empty/loading/blocked 상태 영향을 적는다.
- `테스트/fixture/드리프트 검증`: contract test, OpenAPI, JSON Schema, fixture, MSW/mock sync, drift guard 기준을 적는다.
- `구현 메모`: controller, STOMP handler, service, transaction, persistence, audit/security log, 구현 순서, TDD issue 연결 후보를 적는다.

## 추출 기준

`negotiate-fe-be-contract`의 `summarize.md` 구조를 기준으로 추출한다.

- 전체 gate 통과 뒤 대상 `상태.status`가 `fixed`이면 `implementation_status: ready`로 기록한다.
- `결정`은 BE가 지켜야 할 결정과 필요한 계약 섹션으로 재배치한다.
- `FE 구현 영향`은 BE가 맞춰야 하는 API 소비 방식, 화면 상태, mock/fixture 요구만 반영한다.
- `BE 구현 영향`은 구현 메모와 관련 계약 섹션에 반영한다.
- `계약 테스트/검증`은 테스트/fixture/드리프트 검증에 반영한다.
- `미결정 또는 사용자 결정 이력`은 이력으로 옮기지 말고, 현재 구현을 막는 항목만 구현 차단 사항에 반영한다.
- `참조 메모 반영 대상`은 BE 구현 계약 자체가 아니면 생략한다.

## 갱신 규칙

- 기존 `docs/contracts/{topic}.md`는 현재 `summarize.md` 기준으로 덮어쓴다.
- 원본 보존이나 변경 이력 보존을 위해 오래된 내용을 남기지 않는다.
- 이전 파일에 있었지만 현재 fixed 요약에서 사라진 계약은 제거한다.
- 확정 요약에도 BE 구현에 필요한 핵심값이 없으면 계약 파일을 갱신하지 말고 전체 협상 커버리지 누락으로 보고해 `$negotiate-fe-be-contract`에서 보완한다.
- 같은 내용을 여러 섹션에 장황하게 중복하지 않는다.

## 출처 상태 기록

계약 파일을 하나 이상 생성하거나 갱신한 뒤 아래 명령을 실행한다.

```bash
python3 .codex/scripts/artifact-state.py record contracts \
  --input-glob 'docs/negotiation/*/summarize.md' \
  --output-glob 'docs/contracts/*.md'
```

이 기록은 협상 원문을 계약 문서에 복사하지 않으며, 이후 TRD와 이슈 생성 단계에서 stale 계약을 자동 차단하는 용도로만 사용한다.

## 금지 사항

- `summarize.md`에 없는 endpoint, destination, field, error code를 새로 확정하지 않는다.
- topic을 API/보안/검증 같은 고정 분류로 재해석하지 않는다.
- topic별 디렉터리나 고정 분류 파일 세트를 만들지 않는다.
- 협상 로그, 원본 경로, source_artifacts, 승인 이력을 `docs/contracts`에 누적하지 않는다.
- FE repo에 BE 계약 전문을 복사하지 않는다.
- negotiation session이 `completed`가 아닌 상태에서 fixed topic만 골라 부분 sync하지 않는다.

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 처리한 topic
- 확인한 negotiation session 완료 상태
- 생성 또는 갱신한 `docs/contracts/{topic}.md`
- BE 구현에 바로 사용할 수 있는 계약 범위
- 미확정 또는 구현 차단 항목
- 수정하지 않은 코드와 협상 원문 범위

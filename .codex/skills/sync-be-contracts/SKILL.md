---
name: sync-be-contracts
description: Online-TCG-Chess-BE에서 FE/BE 협의가 끝난 docs/negotiation/{topic}/summarize.md를 BE 구현자가 바로 참조할 계약 문서로 정리해야 할 때 사용한다. 협의 topic별로 결정된 REST API, STOMP/WebSocket, 인증/CSRF/cookie, 오류 포맷, 상태 동기화, projection, contract test, fixture 등 BE가 알아야 할 규약만 docs/contracts/{topic}.md로 생성·갱신하고, TDD나 구현 전에 FE와 확정된 규약을 확인해야 할 때 사용한다.
---

# Sync BE Contracts

## 개요

`docs/negotiation/{topic}/summarize.md`에 정리된 FE/BE 협의 결과 중 BE 구현에 필요한 규약만 `docs/contracts/{topic}.md`에 저장한다. 협상 절차, 과정 기록, 승인 이력, 원본 추적은 `$negotiate-fe-be-contract`와 `docs/negotiation`이 담당하므로 이 스킬은 BE 구현자가 꺼내 볼 결정된 계약 정보만 남긴다.

## 기본 원칙

- 모든 질문, 분석, 기록은 한국어로 작성한다.
- 새 계약을 만들거나 협상하지 않는다.
- topic은 계약 분류명이 아니라 FE/BE 협의 주제명이다.
- `docs/contracts/{topic}.md`에는 그 topic에서 BE가 알아야 할 결정 사항만 저장한다.
- 원본 경로, source_artifacts, supersedes, 협상 과정, 사용자 결정 이력은 복사하지 않는다.
- `summarize.md`가 `fixed`가 아니면 구현 가능한 계약처럼 정리하지 않는다.
- production code, test code, PRD/TRD, architecture, `docs/negotiation` 원문은 수정하지 않는다.
- 계약 동기화가 끝나면 `docs/negotiation/*/summarize.md`와 `docs/contracts/*.md`의 fingerprint를 기록한다.

## 입력 범위

사용자가 topic을 지정하면 해당 topic만 처리한다. topic이 없으면 `docs/negotiation/*/summarize.md`를 스캔해 `fixed` 상태인 topic을 처리한다.

먼저 다음만 읽는다.

1. 대상 `docs/negotiation/{topic}/summarize.md`
2. 이미 존재하는 `docs/contracts/{topic}.md`
3. 필요할 때만 관련 `docs/spec/spec-fixed.md`, `docs/websocket-spec.md`, `docs/trd.md`, `docs/features/*/trd.md`

`summarize.md`가 없거나 형식을 해석할 수 없으면 문서를 만들지 말고 차단 사유를 보고한다. `summarize.md` 상태가 `fixed`가 아니면 `docs/contracts/{topic}.md`에 구현 차단 상태와 BE가 기다려야 할 결정만 짧게 기록한다.

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

- implementation_status: ready | blocked

## BE가 지켜야 할 결정

## REST 계약

## STOMP/WebSocket 계약

## 인증/보안/노출 제한

## 상태 동기화와 서버 권위

## 오류 포맷과 사용자 표시 영향

## 테스트/fixture/드리프트 검증

## 구현 메모

## 구현 차단 사항
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
- `구현 차단 사항`: `fixed`가 아니거나 fixed 요약만으로 BE 구현을 확정할 수 없는 질문을 적는다.

## 추출 기준

`negotiate-fe-be-contract`의 `summarize.md` 구조를 기준으로 추출한다.

- `상태.status`가 `fixed`이면 `implementation_status: ready`로 기록한다.
- `상태.status`가 `fixed`가 아니면 `implementation_status: blocked`로 기록하고 구현 차단 사항만 남긴다.
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
- 확정 요약에도 BE 구현에 필요한 핵심값이 없으면 추측하지 말고 `구현 차단 사항`에 질문으로 남긴다.
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

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 처리한 topic
- 생성 또는 갱신한 `docs/contracts/{topic}.md`
- BE 구현에 바로 사용할 수 있는 계약 범위
- 미확정 또는 구현 차단 항목
- 수정하지 않은 코드와 협상 원문 범위

---
name: create-trd
description: 존재하는 docs/prd.md와 docs/features/{feature}/prd.md, docs/spec/spec-fixed.md, docs/architecture/*, 현재 구현·빌드 설정을 기준으로 전체 허브 TRD docs/trd.md, 전반적인 기술 문서 docs/websocket-spec.md와 docs/milestones.md 등 필요한 공통 기술 산출물, 기능별 TRD docs/features/{feature}/trd.md를 한국어로 생성·갱신해야 할 때 사용한다. 인자 없이 호출하면 전체 feature TRD 세트를 다루고, {feature} 인자가 있으면 해당 기능 TRD만 다룬다. 기술 스택이나 아키텍처를 새로 선택하지 않고, PRD 생성, 요구사항 인터뷰, 스펙 리뷰, issue, ADR 작성은 하지 않는다.
---

# Create TRD

## 개요

존재하는 PRD와 아키텍처 결정을 기준으로 허브 TRD, 공통 기술 문서, 기능별 TRD를 생성하거나 갱신한다. 제품 요구사항, 기술 스택, 서버/인프라 아키텍처를 새로 확정하지 않고, 구현자가 테스트와 설계를 바로 도출할 수 있는 기술 요구사항으로 변환한다.

## 기본 원칙

- 모든 질문, 분석, 문서 초안은 한국어로 작성한다.
- 먼저 `docs/spec/spec-fixed.md`, `docs/prd.md`, 대상 기능의 `docs/features/{feature}/prd.md`를 읽는다.
- 존재하는 `docs/architecture/*`, `build.gradle`, `settings.gradle`, `src/main`, `src/test`, `.github`, `Dockerfile`, `docker-compose*`, `infra`, `deploy`, `k8s`를 읽고 현재 기술 기준을 확인한다.
- 필요한 PRD 파일이 없으면 진행하지 않고 먼저 PRD 생성을 요청한다. 별도 승인 메타데이터는 요구하지 않고 파일 존재를 기본 게이트로 본다.
- 아키텍처 결정이 필요한데 문서가 없거나 미확정이면 임의 확정하지 않고 `architecture-interview` 또는 `architecture-review` 필요 항목으로 남긴다.
- `docs/spec/spec-fixed.md`, `docs/prd.md`, 기능별 PRD는 입력 문서로 취급하고 수정하지 않는다.
- 요구사항 인터뷰, 스펙 리뷰, PRD 생성, issue 생성, ADR 작성은 하지 않는다.
- `docs/trd.md`는 긴 상세 문서가 아니라 허브/요약/링크 문서로 작성한다.
- 상세 기술 요구사항은 `docs/features/{feature}/trd.md`에 작성한다.
- 여러 기능이 공유하는 기술 약속은 공통 기술 문서에 작성하고, 기능별 TRD에서는 링크와 기능별 영향만 적는다.
- 사용자가 명시적으로 일괄 진행을 요청하지 않는 한, 허브 TRD, 공통 기술 문서, 기능별 TRD는 문서별 사용자 승인 게이트를 통과한 뒤 다음 문서로 진행한다.

## 대상 범위

사용자가 `{feature}` 인자를 주면 해당 feature만 처리한다. 예를 들어 `$create-trd matchmaking`처럼 요청하면 `docs/features/matchmaking/prd.md`와 관련 공통 기술 문서를 기준으로 `docs/features/matchmaking/trd.md`만 생성하거나 갱신한다.

인자가 없으면 `docs/features/*/prd.md`를 기준으로 전체 feature 후보를 탐색하고 허브 TRD, 필요한 공통 기술 문서, 기능별 TRD 세트를 순서대로 생성하거나 갱신한다.

지정된 `{feature}`에 PRD가 없으면 유사한 feature 폴더를 추측해 진행하지 말고, 누락된 경로를 보고하고 중단한다.

## 입력 확인

우선 존재하는 문서와 설정만 읽는다.

- 원천 명세: `docs/spec/spec-fixed.md`
- PRD 산출물: `docs/prd.md`, `docs/features/{feature}/prd.md`
- 기존 TRD 산출물: `docs/trd.md`, `docs/features/{feature}/trd.md`
- 공통 기술 문서: `docs/websocket-spec.md`, `docs/milestones.md`, `docs/traceability.md`
- 아키텍처 산출물: `docs/architecture/*`
- 구현/빌드 기준: `build.gradle`, `settings.gradle`, `src/main`, `src/test`
- CI/CD 또는 인프라 설정: `.github`, `Dockerfile`, `docker-compose*`, `infra`, `deploy`, `k8s`

## 진행 절차

1. `{feature}` 인자가 있는지 확인하고 처리 범위를 확정한다.
2. 입력 문서와 현재 구현/설정 파일을 읽는다.
3. 필요한 PRD 파일 존재와 아키텍처 결정 상태를 확인한다.
4. 파일 작성 전에 처리 범위, 생성/갱신 대상 문서, 공통 기술 문서 필요 여부, 미확정 또는 재검토 필요 항목을 세션에서 제시하고 사용자 승인을 받는다.
5. 인자가 없으면 `docs/trd.md`를 생성하거나 갱신하고 확정받은 뒤 공통 기술 문서와 기능별 TRD로 진행한다.
6. 필요한 공통 기술 문서를 생성하거나 갱신한다.
7. 기능별 `docs/features/{feature}/trd.md`를 하나씩 생성하거나 갱신한다. 각 문서 초안 작성 후 확정 여부를 묻고, 확정 전에는 후속 문서의 기준으로 삼지 않는다.
8. 필요하면 `docs/traceability.md`에 PRD, TRD, 아키텍처, 공통 기술 문서의 연결을 보강한다.
9. 작성 후에는 생성/수정한 파일, 처리한 feature 목록, 남은 모호함, 재검토 필요 항목, 승인 완료된 문서 목록을 간단히 보고한다.

## 공통 기술 문서 기준

공통 기술 문서는 여러 기능에서 반복될 기술 약속을 한곳에 모으기 위해 작성한다. 원천 명세, 확정된 PRD, 아키텍처 문서에 근거가 없는 값은 임의 확정하지 않고 "계약 후보" 또는 "미확정 사항"으로 표시한다.

필요할 때 생성하거나 갱신하는 대표 문서는 다음과 같다.

- `docs/websocket-spec.md`: STOMP/WebSocket destination, 메시지 envelope, 서버 이벤트, 클라이언트 명령, 재접속, 순서, 재동기화, 실시간 오류 응답, 계약 검증 기준
- `docs/milestones.md`: 구현 순서, 기술 의존 관계, 선행 하네스 또는 공통 인프라 작업, 기능별 진행 순서
- `docs/traceability.md`: 원천 명세, PRD, TRD, 아키텍처, 공통 기술 문서 간 추적

공통 기술 문서가 필요하지 않은 기능 단위 요청에서는 기존 문서를 읽고 관련 링크만 유지한다.

## 문서 작성 규칙

- 확정된 요구사항, 아키텍처 결정, 문서화 가정, 계약 후보, 미확정 사항을 구분한다.
- 기능별 TRD는 해당 기능 PRD의 시나리오와 수용 기준을 기술 구현·테스트 관점으로 변환한다.
- Java/Spring 버전, DB, 캐시, 메시징, 배포 단위, 하네스/정적 분석 도구 같은 기술 스택 선택은 아키텍처 산출물의 결정을 따른다. 필요한 결정이 없으면 TRD에서 새로 선택하지 않고 재검토 필요 항목으로 남긴다.
- 서버 책임, 도메인 상태와 불변식, 데이터 저장, 명령/데이터 흐름, REST/STOMP 영향, 권한/검증, 동시성/멱등성, 오류 코드와 상태 불변성, 운영/관측 영향, 테스트 시나리오를 작성한다.
- 실패 흐름에는 사용자에게 보이는 결과, 변경되면 안 되는 도메인 상태, 실패해도 저장될 수 있는 보안 로그/감사 로그/Rate Limit 카운터를 구분한다.
- 원천 명세나 PRD에 없는 endpoint, payload, DB schema, 정책값은 임의 확정하지 않고 "계약 후보" 또는 "미확정 사항"으로 표시한다.
- 공통 실시간 계약은 기능별 TRD에 중복해 길게 쓰지 않고 `docs/websocket-spec.md`를 기준 문서로 둔다.
- 기능별 TRD에는 관련 실시간 계약이 있으면 `docs/websocket-spec.md` 링크와 이벤트 이름 또는 계약 후보 수준만 적는다.
- 아키텍처 문서와 현재 코드가 충돌하면 구현 방향을 확정하지 말고 drift와 재검토 필요 항목으로 기록한다.
- 확정된 문서의 결정사항은 후속 문서에서 기준으로 사용할 수 있다.
- 미확정 문서의 내용은 후속 문서에 단정적으로 반영하지 않는다.
- 문서별 승인 요청은 초안 요약, 생성/수정 파일, 확정 여부 질문, 수정 요청 가능성을 짧게 포함한다.

## 문서 구조

다음 구조만 생성하거나 갱신한다.

```text
docs/
  trd.md
  traceability.md
  milestones.md
  websocket-spec.md
  features/
    {feature}/
      trd.md
```

다음 구조는 생성하지 않는다.

```text
docs/prd.md
docs/features/{feature}/prd.md
docs/features/{feature}/issues/
docs/features/{feature}/adr/
```

## Hub TRD 필수 섹션

`docs/trd.md`는 다음 섹션을 포함한다.

- `# TRD`
- `## 목적`
- `## 입력 문서`
- `## 전체 기술 원칙`
- `## 공통 기술 문서`
- `## Feature TRD 목록`
- `## 아키텍처 결정 참조`
- `## 미확정 및 재검토 필요`

## Feature TRD 필수 섹션

기능별 `trd.md`는 다음 섹션을 포함한다.

- `# {Feature Name} TRD`
- `## 목적`
- `## 입력 문서`
- `## 서버 책임`
- `## 데이터와 상태`
- `## 도메인 상태와 불변식`
- `## 명령/데이터 흐름`
- `## 인터페이스 영향`
- `## 권한과 검증`
- `## 예외 처리`
- `## 동시성 및 멱등성`
- `## 오류 코드와 상태 불변성`
- `## 운영 및 관측 영향`
- `## 테스트 시나리오`
- `## 미확정 사항`
- `## 관련 문서`

`오류 코드와 상태 불변성`에는 관련 공통 오류 코드, 실패 시 변경되면 안 되는 도메인 상태, 실패해도 저장될 수 있는 보안 로그/감사 로그/Rate Limit 카운터를 구분해 작성한다.

## WebSocket Spec 작성 기준

`docs/websocket-spec.md`는 기능별 TRD에 중복하지 않을 STOMP/WebSocket 공통 계약 기준 문서다. 필수 섹션은 다음을 포함한다.

- `# WebSocket Spec`
- `## 목적`
- `## 입력 문서`
- `## 적용 범위`
- `## 연결 및 인증 원칙`
- `## STOMP destination`
- `## 공통 이벤트 envelope`
- `## 클라이언트 명령 메시지 원칙`
- `## 서버 이벤트 메시지 원칙`
- `## 주요 이벤트 목록`
- `## 상태 버전, 순서, 재동기화`
- `## 재접속 및 연결 끊김 처리`
- `## 실시간 오류 응답`
- `## 권한, 제재, 계정 상태 검증`
- `## Rate Limit 및 메시지 제한`
- `## 테스트 및 계약 검증`
- `## 미확정 사항`
- `## 관련 문서`

destination, payload, 이벤트 필드는 원천 명세와 확정 문서에 없으면 임의 확정하지 않고 "계약 후보" 또는 "미확정 사항"으로 표시한다.

## 검증

문서 생성 후 다음을 확인한다.

- `docs/spec/spec-fixed.md`, `docs/prd.md`, 기능별 PRD가 수정되지 않았다.
- PRD, issue, ADR이 생성되지 않았다.
- 허브 TRD, 공통 기술 문서, 기능별 TRD가 문서별 사용자 승인 게이트를 통과한 뒤 다음 문서로 진행되었다.
- 인자 없는 호출은 전체 feature 범위를 처리하고, `{feature}` 인자 호출은 해당 기능만 처리한다.
- `docs/trd.md`는 허브 문서이고, 상세 기술 요구사항은 기능별 TRD와 공통 기술 문서에 위치한다.
- `docs/websocket-spec.md`가 필요한 경우 필수 섹션을 포함하고, 원천 명세와 확정 문서에 없는 실시간 계약을 확정값처럼 쓰지 않는다.
- 각 기능별 TRD에 실패 시 상태 불변성, 동시성/멱등성, 오류 코드, 테스트 시나리오가 있다.
- 아키텍처 결정이 필요한 미확정 사항은 임의 확정하지 않고 재검토 필요 항목으로 남겼다.

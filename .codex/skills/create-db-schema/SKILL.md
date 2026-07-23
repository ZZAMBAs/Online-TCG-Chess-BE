---
name: create-db-schema
description: create-trd 완료 후 create-issues-adr 전에 확정된 요구사항, PRD, TRD, 아키텍처와 FE/BE 계약을 바탕으로 MySQL Flyway DB 스키마 또는 아키텍처에 확정된 NoSQL 스키마 정의를 생성·갱신하고, 저장소 선택 변경이 필요하면 architecture-decision으로 차단·연계해야 할 때 사용한다.
---

# Create DB Schema

## 개요

`$create-trd`가 만든 최신 기술 설계를 실행 가능한 DB 스키마 자원으로 바꾼다. 현재 확정 아키텍처의 MySQL/JPA/Flyway를 우선 따르며, 이 스킬은 DB에 연결하거나 DDL/DML을 실행하지 않는다.

## 기본 원칙

- 모든 질문, 분석, 승인 요청, SQL 주석은 한국어로 작성한다.
- 전체 feature와 공유 저장 경계를 한 번에 처리한다. feature 인자를 받아 부분 스키마를 추측하지 않는다.
- `docs/spec/spec-fixed.md`, `docs/prd.md`, `docs/trd.md`, `docs/features/*/prd.md`, `docs/features/*/trd.md`는 입력 문서로만 취급하고 수정하지 않는다.
- 작업 전 `python3 .codex/scripts/artifact-state.py verify prd`, `verify architecture`, `verify trd`를 실행한다. 하나라도 실패하면 해당 산출물을 갱신할 때까지 중단한다.
- `docs/contracts/*.md`가 있으면 `verify contracts`도 통과해야 한다. `docs/negotiation/session.md`와 `docs/negotiation/*/summarize.md`는 계약 해석 보조 입력으로만 사용하며 새 계약을 만들지 않는다.
- 기존 `db-schema` 상태가 stale이면 현재 입력을 기준으로 변경 계획을 다시 만들되, 기존 version-controlled Flyway migration은 수정하거나 삭제하지 않는다.
- 스키마 초안, 테이블·컬럼·키·제약·인덱스, migration 순서, 영향받는 자원과 아키텍처 재결정 필요 여부를 먼저 제시하고 사용자의 명시적 승인을 받은 뒤에만 파일을 작성한다.
- JPA 엔티티, repository, service, production 기능 코드, DB 접속 설정, 테스트 구현은 수정하지 않는다. schema resource와 이를 찾는 최소 resource 설정만 수정할 수 있다.
- DB 클라이언트, JDBC, Flyway CLI 등으로 실제 DB에 연결하거나 DDL/DML을 실행하지 않는다.

## 입력 범위

다음 순서로 필요한 파일만 읽는다.

1. `docs/spec/spec-fixed.md`, `docs/prd.md`, `docs/trd.md`, `docs/traceability.md`, `docs/milestones.md`, `docs/websocket-spec.md`
2. `docs/features/*/prd.md`, `docs/features/*/trd.md`
3. `docs/architecture/current-fixed.md`가 가리키는 `infra-fixed.md`, `impl-fixed.md`, `harness-fixed.md`와 관련 `docs/architecture/*.md`
4. `docs/contracts/*.md`, `docs/negotiation/session.md`, `docs/negotiation/*/summarize.md`
5. `build.gradle`, `settings.gradle`, `src/main/resources`, 기존 `src/main/resources/db/migration/*.sql`, 기존 `src/main/resources/nosql/*/*`

원천 문서 사이에 저장 모델, 보존 기간, 공개 범위, 동시성 또는 데이터 소유권 충돌이 있으면 SQL로 임의 해결하지 말고 충돌을 보고한다.

## 저장소 선택 게이트

- 현재 fixed 아키텍처에 MySQL/JPA/Flyway가 확정되어 있으면 RDB schema를 MySQL Flyway migration으로 작성한다.
- NoSQL vendor와 인프라가 현재 fixed 아키텍처에 확정되어 있으면 그 vendor의 native schema validation, collection/index 정의를 작성할 수 있다.
- RDB와 NoSQL 전환, 새 NoSQL vendor, queue/cache를 영속 저장소로 사용하는 결정, 또는 필요한 DB 인프라가 fixed에 없으면 파일을 만들거나 바꾸지 않는다. 저장소 후보와 필요한 인프라를 정리해 `$architecture-decision`으로 넘기고, 사용자의 답변과 fixed 결과 뒤에 다시 실행한다.
- 저장소 전환이 확정되어도 이미 version-controlled된 Flyway migration을 삭제하지 않는다. 신규 NoSQL 정의와 별도 이전·운영 계획은 후속 아키텍처/이슈 산출물에서 다룬다.

## RDB 산출물 규칙

```text
src/main/resources/db/migration/
  V...__create_{table}.sql
  V...__alter_{table}_{purpose}.sql
```

- 초기 생성은 테이블 하나당 하나의 `CREATE TABLE` Flyway migration으로 작성한다. 외래 키 의존 대상, join table, index와 제약을 적용 가능한 순서로 둔다.
- 기존 version-controlled migration은 적용됐을 가능성이 있으므로 불변이다. 변경은 항상 더 높은 Flyway version의 새 migration으로 작성한다.
- 같은 실행에서 새로 만든 미커밋 초안만 수정할 수 있다. 이미 저장소에 존재한 migration을 초안으로 취급하려면 사용자의 명시가 필요하다.
- 테이블·컬럼·자료형·nullability·PK/FK·unique/check 제약·index·낙관적 revision·감사 시각은 상위 입력에 근거할 때만 만든다. 근거 없는 정책값, enum 값, retention, partition, trigger, procedure는 추가하지 않는다.
- `DROP`, 파괴적 type 축소, 데이터 backfill이 필요한 변경은 실행하지 않으며 영향과 별도 이전 필요성을 승인 초안에 표시한다. 이 스킬은 migration 파일도 사용자 승인 뒤에만 작성한다.

## NoSQL 산출물 규칙

```text
src/main/resources/nosql/{vendor}/
```

- vendor가 fixed 문서에 명시된 경우에만 vendor-native 형식으로 collection, document validation, key/index/TTL 정의를 작성한다.
- document 구조, partition/shard key, consistency, TTL, secondary index는 PRD/TRD/아키텍처에서 근거가 있을 때만 확정한다.
- vendor가 정해지지 않았거나 해당 인프라가 없으면 범용 JSON, MongoDB 문법 또는 임의 vendor 파일을 만들어 두지 않는다.

## 진행 절차

1. 입력 산출물과 최신성 게이트를 확인하고 기존 schema resource와 `db-schema` 상태를 읽는다.
2. feature별 데이터 소유권, 영속 상태, 관계, 조회 패턴, 동시성·멱등성, 감사·보안 보존 요구를 추출한다.
3. 현재 fixed 저장소와 비교해 RDB/NoSQL 변경 필요 여부를 판단한다. 아키텍처 게이트 대상이면 차단 사유와 `$architecture-decision` 입력을 보고하고 멈춘다.
4. 저장소 선택이 fixed면 생성·변경·유지할 schema 파일, migration 순서, 기존 파일 불변성, 데이터 이전 위험을 사용자에게 제시하고 승인받는다.
5. 승인 범위 안에서 schema resource와 필요한 최소 resource 설정만 생성·갱신한다.
6. SQL syntax, migration version 중복, 파일명 규칙, 외래 키 참조 순서와 `git diff --check`를 확인한다. NoSQL은 해당 vendor 형식과 파일 경로를 확인한다.
7. 생성 또는 갱신한 schema 종류에 맞는 명령으로 출처 상태를 기록한다.

RDB가 있으면 다음을 사용한다.

```bash
python3 .codex/scripts/artifact-state.py record db-schema \
  --input docs/spec/spec-fixed.md \
  --input docs/prd.md \
  --input docs/trd.md \
  --input docs/traceability.md \
  --input-glob 'docs/features/*/prd.md' \
  --input-glob 'docs/features/*/trd.md' \
  --input-glob 'docs/architecture/*.md' \
  --input-glob 'docs/architecture/fixed-*/*.md' \
  --optional-input-glob 'docs/contracts/*.md' \
  --optional-input-glob 'docs/negotiation/*/summarize.md' \
  --optional-input-glob 'docs/negotiation/session.md' \
  --output-glob 'src/main/resources/db/migration/*.sql' \
  --optional-output-glob 'src/main/resources/nosql/*/*'
```

NoSQL만 있으면 `--output-glob 'src/main/resources/nosql/*/*'`를 필수 output으로 바꾸고 RDB glob은 optional output으로 사용한다.

## 금지 사항

- DB 연결, DDL/DML 실행, 데이터 조회·수정, Flyway migrate 실행
- 상위 문서에 없는 테이블·필드·정책값·NoSQL vendor를 확정하는 행위
- applied 가능성이 있는 Flyway migration 수정·삭제
- JPA entity/repository/service/controller, 기능 테스트, PRD/TRD/계약 원문 수정
- 인프라 부재를 SQL 또는 placeholder NoSQL 파일로 우회하는 행위

## 완료 보고

작업을 마치면 다음만 간결히 보고한다.

- 확인한 최신성 게이트와 저장소 선택
- 생성·갱신한 RDB/NoSQL schema 파일
- 기존 migration 불변성 및 새 migration 여부
- `db-schema` fingerprint 기록 결과
- `$architecture-decision` 또는 사용자 승인이 필요한 차단 항목

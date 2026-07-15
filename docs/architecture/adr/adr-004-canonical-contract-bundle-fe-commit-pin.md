---
id: "ARCH-ADR-004"
status: "accepted"
decision_scope: "harness"
fixed_reference: "docs/architecture/fixed-20260714/harness-fixed.md"
supersedes: []
source_documents:
  - "docs/negotiation/contract-fixture/summarize.md"
  - "docs/architecture/interview-20260714/interview-log.md"
---

# ARCH-ADR-004. BE canonical 계약 번들을 FE가 BE commit으로 고정해 동기화

## Context

FE와 BE는 동일한 REST OpenAPI, STOMP JSON Schema, fixture와 fingerprint를 사용해야 한다. 계약 협상은 동일 bundle과 source BE commit pin을 요구하지만 기존 harness 문서는 FE 공유 방식을 미확정으로 남겨 두었다. MVP는 package registry나 runtime 계약 조회 인프라를 아직 선택하지 않았으며, 양쪽 저장소가 계약을 독립 작성하면 의미가 같은지 수동으로 확인해야 하고 drift를 기계적으로 차단하기 어렵다.

## Decision

BE 저장소의 version-controlled OpenAPI 3.1·STOMP JSON Schema와 authored positive/negative/privacy fixture 원본만 사람이 수정하는 단일 작성 정본으로 둔다. manifest, fingerprint와 언어별 생성 산출물은 이 정본에서 결정적으로 파생하며 직접 수정하거나 별도 의미 원천으로 사용하지 않는다. authored fixture와 generated fixture의 구분은 후속 schema closure·TRD에서 manifest 항목별로 닫는다.

FE 저장소는 적용할 BE git commit을 명시적으로 pin하고 해당 commit의 canonical bundle을 checked-in copy로 동기화한다. FE는 같은 계약을 독립적으로 다시 작성하지 않는다.

FE의 계약 채택 metadata는 allowlist로 고정한 canonical repository identity, full 40-character BE commit, canonical bundle root와 expected bundle root fingerprint를 함께 고정한다. manifest 내부에 자기 source commit을 넣는 self-reference는 사용하지 않는다.

BE CI는 canonical source를 빈 임시 디렉터리에 재생성해 manifest file closure, per-file hash와 root fingerprint를 계산하고 checked-in bundle과 byte-for-byte 비교한다. manifest 미참조·누락·stale file과 직접 수정한 파생 산출물은 실패한다.

FE sync는 fetched BE script를 실행하지 않고 manifest가 허용한 data file closure만 빈 staging directory로 복사한다. FE CI는 repo lockfile로 고정한 generator를 clean temporary directory에서 실행해 TypeScript discriminated union·validator·fixture 파생물을 checked-in output과 byte-for-byte 비교한다. pin, copy와 expected root fingerprint는 함께 변경되어야 하며 pin-only·copy-only·fingerprint-only 변경은 실패한다.

계약 변경은 먼저 BE canonical bundle commit으로 확정하고, FE가 그 commit으로 pin을 갱신하는 별도 리뷰 가능한 변경으로 채택한다. FE pin이 갱신되기 전에는 기존 pin의 계약을 계속 사용한다. FE의 일반 build와 테스트는 checked-in copy만 사용한다. 별도 contract-drift CI job은 최신 branch나 HEAD를 조회하지 않고 canonical repository의 정확한 pin commit만 read-only checkout한다. 해당 commit이 protected default branch에서 승인되었는지 확인하고 manifest graph와 checked-in copy를 byte-for-byte 비교하며 checkout을 할 수 없으면 실패한다. 이 checkout은 CI 검증 시점의 개발 의존성이며 runtime, application build artifact와 제품 동작은 원격 호출이나 외부 artifact registry에 의존하지 않는다.

bundle의 상세 디렉터리, manifest JSON Schema, 생성 명령과 CI job 이름은 후속 계약 schema closure·TRD·issue가 정한다.

BE commit pin은 build provenance이며 runtime protocol negotiation이 아니다. production 최초 배포 이후 기존 pin의 closed validator를 실패시키는 field 추가·삭제·의미 변경은 incompatible contract다. incompatible contract는 old endpoint·destination·schema를 유지하는 parallel version 또는 old/new를 함께 수용하는 expand-contract 단계 없이 활성화하지 않는다. FE·BE release artifact에는 adopted bundle root fingerprint를 기록하고 CD 확정 뒤 release pair compatibility를 deploy gate로 검사한다. provider/CD 전에는 이 gate가 미구현이므로 post-launch breaking contract activation을 허용하지 않는다.

전체 REST endpoint, STOMP destination, 오류와 fixture가 manifest root closure에 포함되는 `contract-schema-closure`가 fixed된 뒤 bundle gate를 활성화한다.

## Alternatives

| 대안 | 장점 | 단점/위험 | 현재 상황에서의 적합성 | 선택 또는 제외 이유 |
| --- | --- | --- | --- | --- |
| BE canonical bundle + FE BE-commit pin/checked-in copy | 소유권과 채택 버전이 명확하고 offline build와 commit 단위 검토가 가능하다. | FE pin 갱신과 copy 동기화 절차가 필요하다. | 별도 배포 인프라가 없는 MVP에서 Git과 CI를 재사용할 수 있다. | 선택. 새 인프라 없이 양쪽 drift를 기계적으로 차단한다. |
| package/artifact registry 게시 | semver dependency와 중앙 배포가 가능하다. | registry, publish 권한, 보존·가용성, credential과 release 운영이 추가된다. | provider/CD와 artifact 배포가 미확정인 MVP에는 과도하다. | 제외. 필요 시 후속 확장으로 재검토한다. |
| FE/BE 독립 계약 파일 + 수동 비교 | 각 저장소가 자율적으로 수정하기 쉽다. | 정본이 둘이고 drift·누락·생성 차이를 review에 의존한다. | fixed 계약과 자동 drift gate 요구에 맞지 않는다. | 제외. 동일 bundle 보장을 약화한다. |

## Consequences

- BE 계약 변경은 canonical bundle과 manifest/fingerprint를 함께 갱신해야 한다.
- FE 계약 채택은 pin된 BE commit과 checked-in bundle·생성 결과를 원자적으로 갱신해야 한다.
- BE와 FE의 채택 시점이 다를 수 있으므로 compatible expand-contract 또는 parallel version과 배포 순서를 계약 변경 이슈에서 명시해야 한다.
- checked-in copy를 사용하는 일반 로컬 build와 테스트는 network 없이 재현할 수 있다. cross-repository provenance 검증 job은 정확히 pin된 BE commit checkout이 필요하지만 최신 계약 탐색, runtime 호출 또는 artifact registry에는 의존하지 않는다.
- 저장소 크기와 동기화 비용이 커지거나 여러 소비자·독립 release가 필요해지면 artifact registry 전환을 `$architecture-decision`으로 재검토한다.

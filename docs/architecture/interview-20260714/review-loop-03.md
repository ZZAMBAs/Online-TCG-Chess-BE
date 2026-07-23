# Architecture Review Loop 03

## 리뷰 입력

- 기준 인터뷰: `interview-20260714/interview-log.md` 질문 5
- 기준 계약: `docs/negotiation/contract-fixture/summarize.md`
- 기준 문서: ARCH-ADR-004, `fixed-20260714/harness-fixed.md`, CI/CD·harness·traceability 문서
- 기준 repo 설정: `build.gradle`, `.github/workflows/backend-ci.yml`, 현재 계약 bundle 미구현 상태

## 리뷰 초점

- canonical 계약 번들의 단일 소유권
- FE가 사용하는 정확한 bundle version의 고정과 동기화
- BE·FE CI drift gate와 offline/runtime 경계
- MVP에 새 registry·credential·release infrastructure를 추가하지 않는지

## 초안 결과

- 기존 fixed 문서의 동일 BE commit pin 요구와 FE 공유 방식 미확정 문구 사이의 충돌을 제거했다.
- BE canonical source와 FE checked-in copy를 구분하고 FE pin 갱신 전 기존 계약을 계속 사용하는 채택 경계를 명시했다.
- BE source/manifest/generated output과 FE pin/bundle/generated output을 각각 CI에서 재계산하도록 책임을 분리했다.
- payload 상세, 디렉터리·명령·job 이름은 계약 schema closure와 후속 TRD/TDD로 남겨 아키텍처가 구현 세부를 선점하지 않는다.

## 독립 리뷰 결과

- BE/CI 리뷰: 선택 방향은 타당하나 일반 offline build와 exact pin provenance checkout의 경계, 작성 정본과 파생물의 우선순위, 계약 요약의 양쪽 repo pin 표현, ADR `decision_scope`를 차단 사항으로 지적했다.
- FE 소비자 리뷰: local self-consistency만으로 pin 출처를 증명하지 못하는 문제, stale/unmanifested/generated drift 완전성, pin과 runtime 호환성의 혼동을 차단 사항으로 지적했다.
- 사용자 재결정 필요성: 없음. 두 리뷰 모두 승인된 1번 대안을 실행 가능하게 명확히 하는 보완으로 판정했다.

## 보완 반영

- 사람이 수정하는 단일 작성 정본을 BE의 version-controlled OpenAPI·STOMP schema와 authored fixture 원본으로 한정하고 manifest, fingerprint와 언어별 output을 결정적 파생물로 명시했다.
- FE 채택 metadata에 allowlist canonical repository identity, full 40-character BE commit, bundle root와 expected root fingerprint를 함께 고정했다.
- 일반 FE build/test는 checked-in copy로 offline 수행하고, 별도 provenance job만 정확한 pin commit을 read-only checkout해 protected default branch 승인과 byte 일치를 검증하도록 분리했다.
- BE·FE 모두 clean temporary directory, manifest closure와 byte-for-byte diff를 사용하며 stale/unmanifested/missing file, pin-only/copy-only/fingerprint-only 변경, fetched BE script 실행을 차단했다.
- commit pin은 build provenance일 뿐 runtime negotiation이 아님을 명시하고, post-launch incompatible contract는 parallel version 또는 expand-contract 없이 활성화하지 않도록 release guardrail을 추가했다.
- 전체 REST/STOMP/오류/fixture root closure는 후속 `contract-schema-closure` fixed를 gate 활성화 선행 조건으로 두었다.
- ARCH-ADR-004의 `decision_scope`를 허용값 `harness`로 정정하고 `contract-fixture`의 self-pin 해석을 제거했다.

## 재리뷰와 승인

- BE/CI 독립 재리뷰: 차단 없음. single source, exact pin provenance, FE sync 공급망 경계, runtime 비의존과 후속 TRD 경계를 승인했다.
- FE 소비자 독립 재리뷰: 차단 없음. full commit·root fingerprint 결합, clean closure/byte diff, breaking contract release guardrail과 schema closure 선행 조건을 승인했다.
- 남은 이슈: manifest 상세 schema, 동기화 명령, generator와 compatibility job은 후속 `contract-schema-closure`·TRD·issue 소유이며 현재 architecture 차단 사항이 아니다.
- 상태: 통과, 차단 없음
- 사용자 결정: 추천안 확정

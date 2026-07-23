# Architecture Decision Final Summary - 2026-07-14

## 결과

- status: fixed
- interview: `interview-log.md`
- review_loops: 3
- fixed: `../fixed-20260714/`
- architecture_adr: `../adr/adr-002-versioned-card-catalog-rdb-sync.md`, `../adr/adr-003-versioned-card-pack-catalog-rdb-sync.md`, `../adr/adr-004-canonical-contract-bundle-fe-commit-pin.md`

## 최종 확정

- `docs/cards`와 활성 버전 목록은 카드 작성·배포 원천이다.
- RDB는 검증·배포된 모든 불변 카드 버전과 현재 활성 버전의 실행·조회 원천이다.
- 활성 버전은 새 배포에서만 전환하고 신규 경기가 이를 고정한다.
- 기존 경기와 과거 기보는 이후 활성 버전 변경으로 달라지지 않는다.
- 활성화·롤백 가능한 버전은 효과 처리·계약·fixture를 함께 유지한다.
- JSON만 변경해 새로운 효과가 자동 구현된 것으로 취급하지 않는다.
- `docs/card-packs`와 별도 활성 manifest는 카드팩 작성·배포 원천이고, RDB는 모든 불변 팩 버전과 현재 활성 팩 버전의 실행·조회 원천이다.
- 팩 활성 버전도 RDB 직접 수정이 아니라 검증된 새 배포에서만 전환한다.
- 카드팩 지급·감사·게임 카드 버전 적용 같은 제품 동작은 PRD·계약이 소유하고 architecture는 이를 반복 정의하지 않는다.
- BE 저장소가 canonical OpenAPI 3.1·STOMP JSON Schema·fixture·manifest/fingerprint 번들을 소유한다.
- FE는 적용할 BE git commit을 pin하고 해당 bundle을 checked-in copy로 동기화하며, 양쪽 CI가 fingerprint와 생성 결과의 drift를 실패시킨다.
- 계약 번들 전달은 runtime 원격 호출이나 MVP artifact registry에 의존하지 않는다.

## 리뷰

- 작성 원천과 실행 원천의 역할 충돌을 해소했다.
- RDB 직접 활성화 우회를 금지했다.
- 롤백 대상 버전의 실행 가능성을 효과 처리·계약 보존으로 보완했다.
- 제품 정책과 팩 master 저장·동기화 architecture의 소유권을 분리했다.
- 기존 카드 catalog의 불변 동기화·배포 활성화·검증 경계를 팩 catalog에 재사용했다.
- fixed 계약의 동일 bundle 요구와 기존 FE 공유 방식 미확정 문구의 충돌을 해소했다.
- BE 원천과 FE 채택 시점을 별도 commit으로 추적하면서 수동 이중 작성 없이 CI drift를 차단한다.
- 차단 이슈는 남지 않았다.

## 변경하지 않은 결정

- 서버 스타일, 클라우드·컴퓨팅·네트워크, Redis/메시징, 인증·secret, 관측, CD와 분산 전환 조건은 `fixed-20260710` 결정을 유지한다.

## 남은 미확정

- 상세 resource, persistence schema, 동기화 use case, effect registry와 contract fixture 구현
- provider/CD 기반 실제 배포·rollback 자동화

## 후속 연계

- 현재 협상 topic의 fresh FE/BE 검토
- 전체 계약 fixed 후 `sync-be-contracts`
- 이후 `create-trd`와 `create-issues-adr`, `tdd-workflow`

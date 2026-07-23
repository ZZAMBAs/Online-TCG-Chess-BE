# Final Coverage Review BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

- 전체 fixed 요구사항, PRD, 양쪽 fixed architecture와 모든 negotiation summary를 fresh FE/BE 검토자가 독립 대조했다.
- canonical contract surface는 63개 REST operation, STOMP CONNECT/SUBSCRIBE/SEND/server channel, auth/cookie/CSRF, 공통 오류, matchmaking, game state·command·private recovery, chat, replay, community, identity와 trust/admin을 모두 포함한다.
- exact component, discriminator, required/null/forbidden, operation security/error/header, public/private projection, live/replay union과 manifest/provenance/fixture coverage에 누락이 없다.
- fresh FE 최종 결과: blocking finding 없음.
- fresh BE 최종 결과: blocking finding 없음.

## 해소된 이전 차단

- post lifetime report 정책은 fixed spec 기준으로 유지했다.
- 관리자 공지 producer와 eligible population은 사용자 승인과 fixed PRD/contract에 반영했다.
- canonical bundle 공유 방식은 ARCH-ADR-004와 fixed architecture로 확정했다.
- auth/error/matchmaking/game/replay/community/trust exact schema는 `contract-schema-closure` 네 registry로 닫았다.
- trust-safety PRD의 차단 상대 문구 오기는 상위 spec에 맞게 정정했다.

## 오류 포맷과 사용자 표시 영향

- generated OpenAPI/TypeScript/Ajv, MSW, fake STOMP와 Playwright는 canonical manifest와 fixture만 사용한다.
- contract drift, private tail loss, unknown definition과 privacy leakage는 cache/reducer 진입 전 또는 snapshot sync로 차단한다.

## 구현 메모

- named DTO/schema와 operation/channel registry를 canonical bundle로 투영하며 임의 Map, 미등록 status/code/header를 추가하지 않는다.
- 전체 session completed 뒤 `$sync-be-contracts`로 BE 구현 계약을 생성한다.

## 테스트/fixture/드리프트 검증

- 모든 operation/message/union variant positive와 structural/domain/privacy/sequence/provenance negative coverage
- FE exact commit pin, checked-in copy, per-file/root fingerprint와 generated output drift
- live/replay definition, private sequence tail recovery와 chat viewer/sender restriction matrix

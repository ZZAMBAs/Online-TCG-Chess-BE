# Match History Replay Rest BE Contract

## 상태

- implementation_status: ready

## BE가 지켜야 할 결정

- summary, 최대 10개 recent match page, opponent/result/end reason과 sealed replay의 terminal/initialState/steps/stateAfter/visibleCardDefinitions는 `docs/negotiation/contract-schema-closure/summarize.md`의 닫힌 DTO를 사용한다.
- replay의 `initialState`와 `stateAfter`는 동일 viewer-redacted state schema를 사용하고 live-only action capability, receipt/error/connection metadata를 포함하지 않는다.
- 전적 요약, 최근 경기 목록과 참가자 전용 sealed replay의 FE/BE 기술 계약은 합의되었다.
- replay step은 committed transition 단위이고 완전한 viewer `stateAfter`가 최종 권위다. current gameplay/card handler를 재실행하지 않는다.
- historical card definition은 viewer에게 실제 보이는 ref만 제공하며 비공개 정보는 제외한다.
- unknown game과 nonparticipant는 동일한 `404 RESOURCE_NOT_FOUND`를 사용한다.
- replay는 `viewerColor-bottom`으로 고정하며 BE canonical FEN·좌표는 유지하고 FE가 rendering 경계에서만 회전한다. MVP 방향 전환 toggle은 제외한다.
- `GET /api/v1/me/match-history/summary`는 `countedMatches`, 승·무·패와 소수점 첫째 자리 HALF_UP 승률 문자열을 반환한다. 0전은 `"0.0"`이다.
- `GET /api/v1/me/match-history/matches?cursor=...`는 `(endedAt DESC, gameId DESC)` 기준 사용자 결합 opaque keyset cursor와 고정 최대 10개를 사용한다.
- `GET /api/v1/me/match-history/matches/{gameId}/replay`는 봉인된 종료·무효 경기의 일관된 전체 응답을 참가자에게만 제공한다.
- replay step은 committed transition 단위이고 `stepIndex`는 `0..n-1`, `stateVersion`은 저장 version, inner event는 저장 ordinal 순이다.
- event와 `stateAfter`가 겹치면 `stateAfter`가 권위이며 카드 적용 step의 FEN은 저장 outcome `resultingFen`과 같아야 한다.
- 무효 종료는 `GAME_ENDED`와 `reasonCode: SERVER_ABORTED`, `terminalOutcome: INVALID`로 나타내며 winner를 두지 않는다.

## 오류 포맷과 사용자 표시 영향

- replay board는 server `stateAfter`를 원자 교체하고 current handler를 실행하지 않는다.
- board rotation은 `viewerColor-bottom` 원칙에 따라 canonical FEN/좌표를 바꾸지 않고 FE rendering 경계에서 수행한다.

## 구현 메모

- sealed historical viewer projection과 participant authorization을 제공해야 한다.
- projection은 transition별 불변 after-state 저장 또는 versioned replay projector용 after-value 저장 중 하나로 구현하되 current handler 재실행을 금지한다.
- 저장 세부 방식은 현재 확정 아키텍처 변경 없이 후속 TRD에서 구체화할 수 있다.

## 테스트/fixture/드리프트 검증

- summary 계산, 최대 10개 keyset cursor, transition ordering, event/stateAfter FEN 일치, sealed consistency와 최대 크기를 검증한다.
- historical definition allowlist와 상대 미사용 레전드·후보·내부 ID·raw selection·상세 실패·RNG/MMR/접속·차단 정보 부재를 privacy-negative fixture로 검증한다.
- unknown/nonparticipant의 status/code/body shape가 동일한지 검증한다.

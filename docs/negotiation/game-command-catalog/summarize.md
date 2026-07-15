# Game Command Catalog Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/game-command-catalog/20260713-162513.md`, `docs/negotiation/game-command-catalog/20260713-162711.md`, `docs/negotiation/game-command-catalog/20260713-164349.md`, `docs/negotiation/game-command-catalog/20260713-165037.md`, `docs/negotiation/game-command-catalog/20260713-165315.md`, `docs/negotiation/game-command-catalog/20260713-165532.md`, `docs/negotiation/game-command-catalog/20260714-144352.md`, `docs/negotiation/game-command-catalog/20260714-144649.md`, `docs/negotiation/game-command-catalog/20260714-144831.md`
- supersedes: 2026-07-13의 `USE_PRE_MOVE_CARD`, `USE_POST_MOVE_CARD`, `{cardInstanceId,selection}`, `CARD_USED`와 카드 pending 없는 phase 조항

## 결정

### command catalog

- 경기 command는 fixed game-state-sync의 `actionId`, `gameId`, `intent`, `baseStateVersion`, `payload` envelope를 유지하고 wrapper와 intent별 payload를 `additionalProperties: false`로 닫는다.
- intent는 `SKIP_PRE_MOVE`, `CARD_ACTIVATE`, `CARD_RESOLVE`, `MOVE_PIECE`, `CHOOSE_PROMOTION`, `DRAW_CARD`, `PASS_POST_MOVE`, `RESIGN`만 허용한다. 구형 카드 intent는 alias 없이 schema-invalid다.
- `SKIP_PRE_MOVE`, `DRAW_CARD`, `PASS_POST_MOVE`, `RESIGN` payload는 정확히 `{}`다.
- `MOVE_PIECE`는 `{from,to}`이며 square는 소문자 `[a-h][1-8]`다. `CHOOSE_PROMOTION`은 `{pieceType}`이고 값은 `QUEEN|ROOK|BISHOP|KNIGHT`다.
- `CARD_ACTIVATE`는 정확히 `{cardInstanceId}`, `CARD_RESOLVE`는 `{activationId,selection}`이고 selection은 fixed `contract-fixture`의 6종 공용체를 참조한다. 자유형 object, card ID/version, effect와 client 후보 계산 결과를 받지 않는다.
- phase별 허용 관계는 `PRE_MOVE: SKIP_PRE_MOVE|CARD_ACTIVATE`, `PIECE_MOVE: MOVE_PIECE`, `PROMOTION: CHOOSE_PROMOTION`, `POST_MOVE: CARD_ACTIVATE|DRAW_CARD|PASS_POST_MOVE`, `EFFECT_PENDING: CARD_RESOLVE`, 활성 경기 전체: `RESIGN`이다.

### transition과 event catalog

- 19개 event의 payload, public/private scope, required/null/forbidden 조건과 종료 reason/outcome mapping은 `docs/negotiation/contract-schema-closure/summarize.md`의 GameEvent registry로 고정한다.
- 카드 보드 변경은 outcome `resultingFen`, 표준 이동은 `PIECE_MOVED.resultingFen`, promotion 완료는 `PROMOTION_COMPLETED.resultingFen`이 해당 transition의 보드 권위다.

- 확정 공개·개인 delta는 outer `messageType: GAME_TRANSITION` variant로 전달한다. outer 필드는 `schemaVersion,eventId,messageType,gameId,stateVersion,transitionId,serverTime,payload`다. public payload는 `{projectionScope:"PUBLIC",events,privateSequencesAfter}`, viewer-private는 `{projectionScope:"VIEWER_PRIVATE",viewerPrivateSequence,events}`다. `eventType`은 inner `events[]` discriminator에만 사용한다.
- public과 private envelope는 같은 `(gameId,stateVersion,transitionId)`를 공유하고 서로 다른 `eventId`를 가진다. `privateSequencesAfter`는 WHITE/BLACK viewer별 commit 뒤 private cursor를 제공하고 실제 개인 변화가 있는 viewer cursor만 1 증가한다.
- `events[]` 원소는 0-based 연속 `ordinal`과 닫힌 `eventType/payload`를 가진다. 사유는 해당 payload variant 안에서만 허용하며 outer/inner 공통 optional `reasonCode`는 두지 않는다. 배열 순서가 서버가 확정한 인과 순서이며 FE가 eventType으로 재정렬하지 않는다.
- 구조 event는 `TURN_STARTED`, `PHASE_CHANGED`, `PRE_MOVE_SKIPPED`, `PIECE_MOVED`, `PROMOTION_REQUIRED`, `PROMOTION_COMPLETED`, `CARD_ACTIVATED`, `EFFECT_PENDING`, `CARD_EFFECT_APPLIED`, `CARD_EFFECT_FAILED`, `CARD_DRAWN`, `POST_MOVE_PASSED`, `MANA_CHANGED`, `CHECK_DECLARED`, `TURN_ENDED`, `TIMER_UPDATED`, `GAME_ENDED`, 개인 `PRIVATE_HAND_UPDATED`, `PRIVATE_LEGEND_UPDATED`의 19개다.
- phase는 `TURN_START|PRE_MOVE|PIECE_MOVE|PROMOTION|POST_MOVE|EFFECT_PENDING|TURN_END|GAME_ENDED`, color는 `WHITE|BLACK`이다.
- `PIECE_MOVED`는 표준 말 이동 전용이다. 카드 보드 변화는 `CARD_EFFECT_APPLIED`의 outcome과 `resultingFen`으로 정확히 한 번 적용하고 별도 이동 event를 중복 발행하지 않는다.
- 선택형 activation public 순서는 `CARD_ACTIVATED → MANA_CHANGED(변화 시) → EFFECT_PENDING → PHASE_CHANGED`, 무대상 activation은 activation·mana 뒤 applied/failed와 결과·다음 단계 event, resolve는 applied/failed 뒤 결과·다음 단계 event다. server가 원래 PRE/POST phase를 activation에 보존하고 다음 단계를 결정한다.
- 한 도메인 transition은 inner event 수와 무관하게 `stateVersion`을 한 번만 증가시킨다. domain 변경, stateVersion, transitionId, ordered GameEvent와 멱등 결과는 같은 명령 확정 경계에서 원자 보존하고 commit 뒤 projection을 발행한다.
- timer, disconnect, 항복, 사용자 command와 경기 종료는 같은 경기 lock/queue에서 경쟁한다. 자동 transition은 `actionId` 없이 생성할 수 있다.

### public/private merge와 pending

- public transition만 FE version cursor를 전진시킨다. private augmentation은 public commit의 선행 조건이 아니며 private 유실 때문에 public 적용을 대기하지 않는다.
- 현재 public cursor가 `v`일 때 `v+1` private tuple만 보류한다. 더 큰 version은 gap으로 보고 resync한다. 대응 public commit 직후 보류 private를 idempotent 보강하고, 현재 public tuple과 같은 private는 즉시 보강한다.
- viewer-private sequence도 snapshot의 `lastViewerPrivateSequence`를 기준으로 duplicate/stale/+1/gap을 판정한다. public after cursor가 +1인데 대응 private가 유실되거나 2 이상 gap이면 부분 손패를 추정하지 않고 sync한다.
- public 수신 시 기대 +1 private가 buffer에 없으면 2,000ms 단회 grace를 시작하고, 만료·reconnect·새 public cursor 중 하나가 먼저 발생하면 sync한다.
- `stateVersion < currentPublicCursor`이거나 권위 snapshot version 이하 private는 stale로 폐기한다. 같은 tuple의 같은 payload는 duplicate이며, 같은 tuple의 다른 payload 또는 같은 game/version의 다른 transitionId는 부분 merge하지 않고 resync한다.
- actor 성공 result와 application error는 `GAME_TRANSITION` 밖의 개인 receipt다. success receipt는 commit 뒤에만 보내며 `actionId,stateVersion,transitionId`로 pending을 연결할 뿐 cursor나 권위 state를 바꾸지 않는다.
- success receipt가 public보다 먼저 오면 pending은 `confirmed-awaiting-transition`이다. 대응 public transition을 commit하거나 receipt version 이상인 viewer snapshot을 적용하면 overlay를 idempotent 제거한다. 이미 적용한 tuple의 replay receipt는 즉시 confirmed 처리한다.
- 거부된 command는 GameEvent, stateVersion, phase, timer와 행동 슬롯을 바꾸지 않고 fixed common-error 개인 application error로 응답한다.
- 전송 command의 `pendingByActionId`와 권위 domain phase `EFFECT_PENDING`은 별개다. activation receipt가 먼저 와도 transition 또는 snapshot이 확정한 selection UI를 임의 생성·제거하지 않는다.
- malformed resolve는 command pending만 실패시키고 권위 pending을 유지한다. 구조상 유효한 kind·후보 불일치는 committed effect failure이므로 success receipt와 transition으로 권위 pending을 종료한다.

### 공개 일반 손패와 actor-private instance

- viewer snapshot의 `publicGeneralHands`는 정확히 `WHITE`, `BLACK` 순의 두 원소다. 각 원소는 `ownerColor`와 완전한 `cards[{definitionRef,count}]`를 가지며 같은 ref는 한 번, count는 양수이고 0 count는 제거한다.
- public card 목록은 `(cardId,cardVersion,definitionFingerprint,viewFingerprint)` 오름차순이다. 비어 있으면 빈 배열이며 fixed definition presentation/최초 view 규칙을 적용한다.
- public `CARD_ACTIVATED`는 `actorColor`, `usedDefinition`, 완전한 `actorPublicGeneralHandAfter`를 가진다. 레전드 발동도 변경 없는 일반 손패 after-state를 포함한다.
- public `CARD_DRAWN`은 `actorColor`, `drawnDefinition`, 완전한 `actorPublicGeneralHandAfter`, 0 이상 `remainingGeneralDeckCountAfter`를 가진다.
- actor-only `PRIVATE_HAND_UPDATED`는 완전한 `ownGeneralHandAfter[{cardInstanceId,definitionRef}]`를 제공한다. ref tuple 뒤 card instance ID ASCII 순으로 정렬하고 instance ID는 중복되지 않는다.
- actor-only `PRIVATE_LEGEND_UPDATED`는 `ownUnusedLegendAfter`를 `{cardInstanceId,definitionRef}` 또는 사용 완료를 나타내는 명시적 `null`로 제공한다.
- public 손패 count와 actor-private instance 수량이 ref별로 다르면 public state를 rollback하지 않고 재동기화하며 반복되는 canonical mismatch는 fatal contract drift다.

### board, move와 time 정상형

- 일반 snapshot의 `fen`은 서버가 생성한 정확한 6-field 권위 문자열이며 FE는 opaque value로 취급하고 자체 canonicalization하지 않는다.
- phase가 `PROMOTION`일 때 `fen`은 최종 합법 수의 canonical FEN이 아니라 문법적으로 유효한 6-field 서버 권위 intermediate board projection이다. 이때 닫힌 `pendingPromotion: {from,to,color,choices}`가 필수이며 terminal-rank pawn을 최종-position legality로 거부하지 않는다.
- 완료된 move의 UCI는 promotion suffix를 포함한 서버 파생값이고 SAN은 서버 생성 표시값이다. FE는 둘을 상태 식별이나 재계산에 쓰지 않는다. `PROMOTION_REQUIRED`에는 완료된 UCI/SAN을 넣지 않고 `PROMOTION_COMPLETED`에만 제공한다.
- timestamp는 UTC `YYYY-MM-DDTHH:mm:ss.SSSZ`, `remainingMillis`는 `serverTime` 시점의 0 이상 JSON safe integer다.
- `TIMER_UPDATED`는 turn/deadline/remaining-time anchor 등 서버 권위 timer 상태가 committed transition에서 변경될 때만 포함한다. 화면 countdown tick은 FE가 계산하며 GameEvent와 stateVersion을 만들지 않는다.
- 경기 시작 handoff는 fixed matchmaking-lifecycle의 개인 `GAME_CREATED`와 이어지는 subscribe/sync/initial viewer snapshot이 소유한다. 이 catalog는 별도 `GAME_STARTED` public delta를 중복 정의하지 않는다.

## FE 구현 영향

- feature store/reducer는 public transition 원자 commit, private idempotent augmentation, pending overlay와 receipt를 서로 다른 operation으로 처리한다.
- FEN은 렌더링 입력으로만 사용하고 legality 재검증이나 정상화로 계약값을 바꾸지 않는다.
- UI countdown은 serverTime/deadline anchor로 보간하며 tick을 server state로 취급하지 않는다.
- 카드 schema/generated union은 fixed `contract-fixture`를 사용하고 자유형 mock을 허용하지 않는다.
- 공개 손패는 public transition만으로 갱신하고 private event는 자기 card instance 선택 정보만 보강한다.

## BE 구현 영향

- inbound adapter는 최신 8개 intent와 닫힌 payload를 검증하고 client 계산 결과나 자유형 카드 입력을 받지 않는다.
- gameplay application은 후보 상태 검증, 원자 commit, 안정적인 inner ordinal과 public/private projection을 생성한다.
- public/private serializer와 actor receipt serializer를 분리하고 commit 실패 시 state나 success receipt를 노출하지 않는다.
- public activation/draw serializer는 일반 손패 완전 after-state를, actor-private serializer는 instance 완전 after-state를 생성하고 ref별 count 정합을 검증한다.
- timer·disconnect·종료와 command를 경기별로 직렬화하며 UI tick 목적의 event를 저장하지 않는다.

## 계약 테스트/검증

- JSON Schema: 최신 8개 command, 8개 phase, 19개 inner event, `GAME_TRANSITION`, public/private projection, actor receipt, promotion intermediate snapshot과 `additionalProperties: false`
- command: 일반 move, capture/mana, skip/pass/draw/resign, phase 오류, stale version, 같은 actionId replay와 conflict
- transition: ordered inner events, 한 version 증가, duplicate, public/private 순서 역전, future private gap, tuple 충돌, snapshot 이하 stale private와 scope privacy
- pending: receipt-before-public, public-before-receipt, replay receipt, snapshot을 통한 pending 해소와 optimistic overlay 무중복
- promotion: terminal-rank pawn과 pendingPromotion 동시 존재, 완료 전 UCI/SAN 부재, 완료 뒤 promotion suffix UCI와 SAN
- timer/concurrency: UI tick 무event, committed deadline 변경, timer-command-disconnect-resign-end 경쟁과 단일 종료
- handoff: `GAME_CREATED → subscribe/sync → initial snapshot`
- privacy-negative: 상대 레전드, 덱 구성·순서, RNG, MMR, 개인 오류와 private selection이 public projection에 포함되면 실패
- drift gate: 해석 가능한 fixed schema와 positive/negative fixture fingerprint를 양쪽 CI에서 비교한다.
- card regression: old intent/`CARD_USED` 거부, `resultingFen` 단일 board 적용, 전송/domain pending 분리, public hand-after와 private instance count 정합, nullable legend와 deterministic ordering

## 미결정 또는 사용자 결정 이력

- 구조 catalog는 요구사항과 양쪽 fixed architecture를 구체화한 사용자 판단 불필요 기술 계약으로 FE/BE 2차 검토에서 이견 없이 확정했다.
- 2026-07-14 fixed `game-card-action-selection`과 `contract-fixture` 이후 fresh FE/BE 검토로 카드 intent/event/phase를 교체했다. 공개 일반 손패의 완전 after-state와 actor-private instance 보강도 이견 없이 확정해 catalog를 fixed로 복구했다.
- 이는 이미 확정된 lifecycle·공개 범위의 기술 투영이므로 새 사용자 결정은 없었다.

## 참조 메모 반영 대상

- BE: 전체 협상 session이 `completed`가 된 뒤 `$sync-be-contracts`가 `docs/contracts/game-command-catalog.md`에 구현 참조 계약을 투영한다.
- FE: 전체 협상 session이 `completed`가 된 뒤 FE 계약 동기화가 canonical BE repo의 fixed 요약을 구현 참조 문서로 투영한다.
- 현재는 양쪽 repo에 별도 참조 메모를 만들지 않는다.

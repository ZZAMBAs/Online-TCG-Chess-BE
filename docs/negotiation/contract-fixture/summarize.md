# Contract Fixture Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/contract-fixture/20260714-143759.md`, `docs/negotiation/contract-fixture/20260714-144010.md`
- supersedes: 자유형 카드 selection/candidate/outcome, `CARD_USED` 기반 fixture와 active definition으로 pinned/historical definition을 치환하는 방식

## 결정

### 공통 wire와 command

- JSON Schema dialect는 draft 2020-12다. 모든 최종 object variant는 `additionalProperties: false`로 닫고 `schemaVersion`은 문자열 literal `"1"`을 사용한다.
- square는 소문자 `^[a-h][1-8]$`, version과 stateVersion은 0 이상 JSON safe integer, ID는 비어 있지 않은 opaque string이다.
- `CARD_ACTIVATE` payload는 정확히 `{cardInstanceId}`이고 `CARD_RESOLVE` payload는 정확히 `{activationId,selection}`이다. client는 card ID/version/fingerprint, actor color, 비용, 효과와 후보 계산 결과를 제출하지 않는다.
- selection은 다음 6종 닫힌 공용체다.
  - `PAWN_AND_DIRECTION {selectionKind,pawnSquare,direction}`: `CARD_001`, direction은 `LEFT|RIGHT`
  - `PAWN {selectionKind,pawnSquare}`: `CARD_002~003`
  - `ROOK {selectionKind,rookSquare}`: `CARD_005`
  - `UNORDERED_PIECE_PAIR {selectionKind,pieceSquares}`: `CARD_006`, 정확히 서로 다른 두 square
  - `FROM_TO {selectionKind,from,to}`: `CARD_007~011`
  - `TARGET_PIECE {selectionKind,targetSquare}`: `CARD_012`
- `CARD_004`는 resolve selection이 없다. unordered pair는 각 pair 내부를 ASCII square 오름차순으로 정규화한 뒤 후보 membership과 command 멱등 canonical value를 비교한다.

### pending 후보와 실패 경계

- actor-private pending candidate는 `{selectionKind,options}`다. `options`는 `minItems: 1`이고 해당 kind의 완전한 submit-ready selection object만 중복 없이 포함한다. FE는 option 하나를 변형 없이 제출한다.
- deterministic option 순서는 `PAWN_AND_DIRECTION: (pawnSquare, LEFT 후 RIGHT)`, 단일 square kind: square, unordered pair: 내부 정렬 후 `(first,second)`, `FROM_TO: (from,to)`다.
- JSON parse 실패, 6종 union 구조 위반, 누락·추가 field, type·square·enum 위반과 unknown kind는 malformed application error이며 pending과 stateVersion을 유지한다.
- 구조상 유효하지만 현재 activation의 expected kind와 다르거나 canonical option 목록 밖인 선택, 또는 적용 시 최종 불변식을 만족하지 못하는 선택은 새 `CARD_EFFECT_FAILED` transition으로 끝나며 이미 확정된 소비와 공개를 유지한다.

### transition, outcome과 snapshot

- public card inner event는 `CARD_ACTIVATED`, `EFFECT_PENDING`, `CARD_EFFECT_APPLIED`, `CARD_EFFECT_FAILED`다. actor-private augmentation만 activation ID, card instance, 후보, canonical selection과 상세 failure code를 포함한다.
- applied outcome은 다음 5종 닫힌 공용체이며 모두 효과 적용 뒤 서버 권위 6-field `resultingFen`을 포함한다.
  - `PIECE_RELOCATED {from,to,resultingFen}`: `CARD_001~003`, `CARD_007~011`
  - `PAWNS_RELOCATED {moves[{from,to}],resultingFen}`: `CARD_004`
  - `CASTLING_RELOCATED {king{from,to},rook{from,to},resultingFen}`: `CARD_005`
  - `PIECES_SWAPPED {squares[2],resultingFen}`: `CARD_006`
  - `PIECE_CONVERTED {square,pieceType,fromColor,toColor,resultingFen}`: `CARD_012`
- FE live reducer와 replay는 `resultingFen`으로 board를 정확히 한 번 교체한다. outcome 좌표는 animation·설명·감사 표시용이며 보드를 재계산하지 않는다. 같은 카드 보드 변경을 별도 `PIECE_MOVED`로 중복 발행하지 않는다.
- public pending에는 definition ref와 actor color만 둔다. actor snapshot만 activation ID, card instance, activation base version/phase와 candidates를 가진 `ownPendingCardEffect`를 포함한다. opponent에는 이 field가 `null`이다.
- `phase == EFFECT_PENDING`이면 public `pendingCardEffect`가 필수이고 다른 phase에서는 `null`이다. 종료 snapshot에서는 두 pending field가 모두 `null`이다.
- viewer snapshot은 `ownColor`를 포함하며 actor reconnect는 동일 activation, pinned definition과 후보를 복원한다.

### pinned definition view와 privacy

- `CardDefinitionRef`는 닫힌 `{cardId,cardVersion,definitionFingerprint,viewFingerprint}`다.
- `definitionFingerprint`는 full immutable server definition의 RFC 8785 canonical JSON bytes, `viewFingerprint`는 `viewFingerprint` field 자체를 제외한 closed `CardDefinitionView` canonical JSON bytes에 각각 SHA-256을 적용한 `sha256:<lowercase hex>`다.
- `CardDefinitionView`는 ref field와 `name,type,packId,image,timing,manaCost,summary,useGuide,selectionKind`만 포함한다. activation condition, effect detail, handler와 내부 실패 규칙은 포함하지 않는다.
- viewer registry에 ref가 처음 나타나는 snapshot 또는 viewer-private transition에는 view를 함께 보낸다. shared live public transition의 card occurrence는 두 참가자의 선행 registry 차이와 무관하게 항상 view를 함께 보내며 같은 canonical bytes/fingerprint의 반복은 idempotent하게 허용한다. ref-only는 해당 viewer 또는 replay top-level registry가 exact view를 먼저 등록한 뒤에만 허용한다. unknown ref without view, 같은 ref의 다른 fingerprint 또는 다른 canonical view bytes는 fatal contract drift다.
- snapshot은 그 viewer projection이 실제 참조하는 pinned definition view만 `(cardId,cardVersion)`별 한 번 포함한다. 상대의 미사용 레전드와 숨은 deck definition을 선공개하지 않는다.

### manifest, fingerprint와 fixture bundle

- canonical manifest root closure는 모든 fixed REST operation, STOMP destination/message/error와 positive/structural-negative/domain-negative/privacy-negative/sequence/provenance fixture를 포함한다.
- manifest 밖 file, unresolved/external ref, fixture 없는 union variant와 schema 없는 operation/destination은 bundle 생성 실패다. 상세 root/file/operation/channel/fixture registry는 `docs/negotiation/contract-schema-closure/summarize.md`를 따른다.
- canonical BE contract bundle의 manifest는 `schemaVersion`, JSON Schema dialect, hash algorithm, schema path/fingerprint, card/version별 definition/view fingerprint·selection kind·candidate/outcome schema ref·stable handler contract·fixture ID, fixture path/fingerprint와 bundle fingerprint를 가진다.
- 개별 JSON은 RFC 8785 canonical JSON bytes와 SHA-256을 사용한다. 의미 없는 manifest 목록은 path 또는 `(cardId,cardVersion)`로 정렬하며 bundle fingerprint는 자기 field를 제외한 manifest canonical value를 hash한다.
- 활성화 또는 rollback 가능한 모든 card version은 definition, handler contract, activation schema, 필요한 resolve/candidate schema, public/private outcome과 positive/negative/privacy fixture에 연결된다. `CARD_004`만 resolve selection이 없다.
- BE 저장소는 canonical bundle을 Git commit으로 버전 관리한다. FE 저장소는 채택할 BE commit을 명시적으로 pin하고 그 commit의 bundle을 checked-in copy로 동기화한다. 양쪽 CI는 각 책임 범위의 fingerprint와 generated output을 재계산한다. runtime 원격 의존은 두지 않는다.

## FE 구현 영향

- schema에서 TypeScript discriminated union과 Ajv validator를 결정적으로 생성하고 직접 수정하지 않는다.
- outbound option과 inbound transition/snapshot을 Ajv로 검증한 뒤 reducer에 전달한다. definition registry와 viewer-private sequence 규칙은 stateful registry adapter와 fixture로 추가 검증한다.
- board authority는 `resultingFen`이며 outcome 좌표를 다시 적용하지 않는다. own-color perspective는 canonical square store 밖의 rendering/input 경계에서 적용한다.
- source fingerprint 확인, 임시 재생성 diff, typecheck, fixture Ajv, fake STOMP reducer와 privacy-negative를 CI hard gate로 둔다.

## BE 구현 영향

- inbound adapter는 공통 6종 structural union까지만 검증하고 activation binding과 candidate membership는 직렬화된 domain command에서 판정한다.
- event store는 pinned card ref, ordered outcome 좌표, `resultingFen`, actor-private canonical selection과 failure detail을 보존하고 projection에서 viewer별로 redact한다.
- replay는 최신 handler를 재실행하지 않고 저장된 ordered outcome과 immutable historical definition view를 projection한다.
- 같은 action ID의 reversed unordered pair는 최초 결과 replay이며 canonical selection이 달라지면 `COMMAND_CONFLICT`다. success receipt는 outcome commit 뒤에만 발행한다.

## 계약 테스트/검증

- schema: 6종 selection/candidate, 5종 outcome, event/snapshot oneOf, 누락·추가 field, 좌표·enum·타입
- lifecycle: activation 성공·비소모 거부, pending reconnect, resolve 성공, malformed pending 유지, kind·후보 밖 소비 유지 실패, 최종 불변식 rollback
- idempotency: unordered pair 반전, duplicate action, canonical command conflict, receipt/transition 역순
- reducer/replay: `resultingFen` 단일 적용, outcome 표시, 과거 version 유지, unknown definition ref와 fingerprint drift fatal
- privacy-negative: public/opponent에 activation ID, card instance, 후보, raw selection, 상세 실패, 상대 미사용 레전드/ref/view가 포함되면 실패
- catalog completeness: 모든 deployable `(cardId,version)`의 handler/schema/outcome/fixture 연결과 manifest·generated bundle fingerprint drift

## 미결정 또는 사용자 결정 이력

- 사용자 판단 사항은 없다. FE/BE 2차 상호 검토에서 fixed 카드 제품 규칙, 공개 범위, version pinning과 replay 정책을 구현 가능한 wire로 투영하는 데 이견이 없어 기술 계약으로 확정했다.

## 참조 메모 반영 대상

- 전체 negotiation session이 `completed`가 된 뒤에만 BE `$sync-be-contracts`와 FE 계약 동기화가 이 fixed 요약과 canonical bundle을 반영한다.
- 현재는 topic별 부분 동기화나 repo별 독립 계약 복사를 하지 않는다.

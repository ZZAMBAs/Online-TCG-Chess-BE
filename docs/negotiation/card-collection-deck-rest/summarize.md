# Card Collection Deck REST Contract Summary

## 상태

- status: fixed
- source_artifacts: `docs/negotiation/card-collection-deck-rest/20260714-145800.md`, `docs/negotiation/card-collection-deck-rest/20260714-150211.md`, `docs/negotiation/card-collection-deck-rest/20260714-150950.md`, `docs/negotiation/card-collection-deck-rest/20260714-153229.md`, `docs/negotiation/card-collection-deck-rest/20260714-153507.md`, `docs/negotiation/card-collection-deck-rest/20260714-153742.md`, `docs/negotiation/card-collection-deck-rest/20260714-153842.md`
- supersedes: pack inventory/`packInstanceId`, opening의 historical card version/view 고정, 여러 saved deck, quick matchmaking의 `{deckId}` 단독 request

## 결정

### 공통과 active card catalog

- REST object는 `schemaVersion: "1"`, 닫힌 schema와 fixed auth·CSRF·공통 오류 계약을 사용한다. ID는 nonempty opaque string, revision은 0 이상 JSON safe integer, 시각은 UTC millisecond `Z`다.
- `GET /api/v1/cards/catalog`는 현재 active card별 fixed `CardDefinitionView`와 `catalogViewFingerprint`를 반환한다. 내부 activation condition, effect detail, handler와 실패 규칙은 금지한다.
- catalog는 `(cardId,cardVersion)`으로 결정적 정렬한다. ETag를 지원하면 catalog view fingerprint와 같고 `If-None-Match` 일치 시 `304`를 허용한다.
- collection, opening reward와 deck은 view/version/fingerprint를 중복 포함하지 않고 stable `cardId`로 active catalog와 join한다.

### collection과 starter 초기화

- `GET /api/v1/me/card-collection`은 `{revision,entries[{cardId,quantity}]}` 완전 resource를 반환한다. card ID별 한 항목, 양수 quantity, card ID 순이다.
- 주요 기능 사용 자격이 확정될 때 starter collection과 stable single deck을 사용자당 한 번, 한 transaction으로 생성한다. 동시 bootstrap·재시도에도 중복 지급하거나 deck ID를 바꾸지 않는다.
- 정상 eligible 사용자에게 collection/deck 부분 초기화, deck 404, revision 0 empty invalid starter를 성공으로 노출하지 않는다.

### BASIC pack 상태와 opening

- pack inventory와 pack instance는 없다. 인증 사용자는 `GET /api/v1/card-packs/basic`으로 `packId: BASIC`, `priceGold: 0`, `cardsPerOpening: 3`, slot별 legend probability 100 basis points, active immutable `probabilityVersion`과 current `quota`를 조회한다.
- closed quota는 `{kstDate,successfulOpenings,dailyLimit,remainingOpenings,resetsAt}`이며 daily limit은 10, reset은 다음 KST 자정의 UTC 시각이다.
- `POST /api/v1/card-packs/basic/openings`은 CSRF와 `Idempotency-Key`, 정확히 빈 `{}` body를 사용한다. 최초 성공과 동일 key replay는 최초 terminal `201`과 body를 반환한다.
- success body는 `openingId`, `packId`, `probabilityVersion`, `openedAt`, `rewards`, `collectionRevision`, 최초 commit의 `quota` snapshot이다.
- rewards는 slot 1·2·3의 정확히 세 항목이며 각각 `{slot,cardId,quantity}`다. quantity는 현재 보유량이 아닌 해당 slot 지급량 literal `1`이고 같은 card ID가 여러 slot에 나와도 aggregate하지 않는다.
- opening response에는 card version, definition ref/view, fingerprint, rarity 판정 내부값, quantity-before/after를 포함하지 않는다. FE는 current catalog와 join하고 success/replay 뒤 collection과 BASIC 상태를 GET한다.
- 동일 key replay는 active card/pack version, 날짜와 현재 collection이 바뀌어도 최초 opening ID, rewards, probability version, collection revision과 quota snapshot을 그대로 반환한다. replay snapshot으로 current cache를 역행시키지 않는다.

### opening transaction, idempotency와 오류

- 사용자+KST 날짜 quota 확인·증가, 세 slot RNG, stable card ID 지급, collection revision 증가와 opening 감사는 한 transaction에서 확정한다.
- 9회 상태의 동시 요청 중 하나만 10번째 성공이며 실패·rollback은 지급, collection revision, 성공 횟수와 성공 감사를 바꾸지 않는다.
- idempotency key는 인증 사용자와 BASIC opening operation에 결합한다. 같은 canonical request는 최초 결과를 재생하고 다른 의미 재사용은 `409 COMMAND_CONFLICT`다.
- idempotency binding은 opening 감사와 같은 수명으로 영속하며 restart·재배포·active version 전환 뒤에도 재지급하지 않는다. raw key는 log/trace/response에 남기지 않고 server-side digest로 비교한다.
- 일일 제한 초과는 `429 RATE_LIMITED`이며 `Retry-After`와 `retryAfterSeconds`는 다음 KST 자정까지 같은 양의 delta-second다. RNG/pool/collection 내부 정보는 오류에 노출하지 않는다.

### 사용자당 단일 saved deck

- MVP는 사용자당 하나의 stable deck resource만 제공한다. 여러 deck의 이름·목록·생성·삭제·기본 선택은 추후 확장이다.
- `GET /api/v1/me/deck`은 `{deckId,revision,entries,valid,invalidReasonCodes}`를 반환한다. entries는 `{cardId,quantity}` 전체 목록이고 version/view를 포함하지 않는다.
- server에는 완전하고 저장 당시 유효한 deck만 저장한다. 불완전 편집은 FE local draft다.
- current `valid`는 조회 시점의 collection·active catalog 기준 파생값이며 revision 증가 없이 달라질 수 있다. closed invalid reason은 `CARD_NOT_ACTIVE|OWNED_QUANTITY_EXCEEDED|DECK_COMPOSITION_INVALID`다.
- `PUT /api/v1/me/deck`은 `{expectedRevision,entries}` 전체 교체다. exactly legend 1, normal 5, 동일 normal 최대 2, 보유 수량 이하와 active card를 검증하고 성공 시 revision을 1 증가시킨 전체 resource를 반환한다.
- 구조·규칙 위반은 fixed `VALIDATION_FAILED`와 RFC 6901 entry pointer, stale revision은 `409 DECK_REVISION_MISMATCH {currentRevision,resyncRequired:true}`다. FE는 GET 후 local draft를 자동 덮어쓰거나 expected revision을 바꿔 자동 재저장하지 않는다.

### matchmaking handoff와 version pinning

- fixed `POST /api/v1/matchmaking/quick` body는 `{deckId,deckRevision}`이다. client는 entries, card version과 fingerprint를 보내지 않는다.
- queue 진입에서 single deck ID/revision과 current validity를 검사하고, game 생성 직전에 같은 revision과 validity를 다시 검사한다.
- 대기 중 deck 변경은 terminal failure `DECK_CHANGED`, current invalid는 `DECK_INVALID`다. 상대 deck과 catalog 내부 정보는 노출하지 않는다.
- game 생성 transaction에서만 stable card ID를 그 시점 current active card ID/version/fingerprint로 resolve해 deck snapshot에 pin한다. deck 저장과 queue 진입은 card version을 pin하지 않는다.

## FE 구현 영향

- catalog, collection, pack와 deck은 독립 loading/error state를 가지며 loading을 empty로 처리하지 않는다.
- collection/deck/reward를 card ID로 current catalog에 join한다. catalog가 없으면 placeholder와 재시도를 제공하고 active catalog에 ID가 끝내 없으면 contract/catalog integrity 오류로 처리한다.
- opening 중 중복 입력을 막고 결과가 불명확하면 같은 key로 재시도한다. success/replay 후 collection과 pack을 재조회한다.
- deck revision conflict는 server latest와 local draft를 사용자에게 구분하고 current `valid`로 빠른 매치 가능 여부를 판단한다.

## BE 구현 영향

- `cardcollection`이 ARCH-ADR-002·003의 active card/pack catalog, starter, collection, opening, single deck transaction과 persistent idempotency를 소유한다.
- public REST serializer는 current catalog 외 resource에 card version/view/fingerprint를 넣지 않는다.
- matchmaking은 deck ID/revision만 받아 재검증하고 gameplay game creation port가 current active card version을 pin한다.

## 계약 테스트/검증

- catalog: active current view only, ETag/fingerprint, internal field privacy-negative
- starter/collection: concurrent once-only initialization, partial rollback, duplicate quantity와 revision ordering
- pack: BASIC 0 gold, closed quota 0·9·10회, ordered 3 slots, legend 0~3, same card duplicate
- opening: same-key byte-equivalent replay, key conflict, restart/deploy/active version change replay, transaction rollback, 9→10 concurrency, stale snapshot 뒤 GET recovery
- privacy: collection/opening/deck에 version/ref/view/fingerprint와 다른 사용자 데이터가 들어가면 실패, raw idempotency key와 RNG secret 비노출
- deck: valid PUT, invalid 비저장, stale revision, multi-tab conflict, current validity change without revision
- matchmaking: `{deckId,deckRevision}`, `DECK_CHANGED`, `DECK_INVALID`, game creation current version pin과 기존 game 불변

## 미결정 또는 사용자 결정 이력

- 2026-07-14 사용자는 MVP에서 사용자당 하나의 편집 가능한 deck을 확정하고 여러 saved deck 관리를 추후 확장으로 두었다.
- 카드팩 감사·개봉 결과는 지급 card ID·slot·probability version이 중요하며 당시 effect version/view는 opening contract로 고정하지 않도록 확정했다.
- ARCH-ADR-003으로 pack master 작성·RDB 동기화·배포 활성화 architecture를 확정했다.
- FE/BE 3라운드 검토에서 field와 lifecycle 이견이 모두 해소돼 추가 사용자 결정 없이 fixed했다.

## 참조 메모 반영 대상

- 전체 negotiation session이 completed된 뒤에만 BE `$sync-be-contracts`와 FE 계약 동기화가 이 fixed 요약을 반영한다.


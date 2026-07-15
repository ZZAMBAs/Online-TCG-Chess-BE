# Canonical STOMP Schema Registry

## 공통

- server-to-client normal/error body의 outer discriminator는 `messageType`이다. inbound game command는 `intent`, sync와 chat send는 wire discriminator가 없다. `eventType`은 `GAME_TRANSITION.payload.events[]`에서만 사용한다.
- 정상 literal: `MATCHMAKING_STATE_CHANGED | GAME_VIEWER_SNAPSHOT | GAME_COMMAND_ACCEPTED | GAME_TRANSITION | CHAT_SEND_ACCEPTED | CHAT_MESSAGE_RECEIVED`.
- 오류 literal: `STOMP_FATAL_ERROR | GAME_COMMAND_REJECTED | GAME_COMMAND_MALFORMED | CHAT_COMMAND_REJECTED | CHAT_COMMAND_MALFORMED`.
- 모든 final object는 `additionalProperties:false`이고 optional condition field를 한 객체에 모으지 않고 code별 final `oneOf`로 전개한다.

## 오류 union

| variant | final fields | code/condition |
| --- | --- | --- |
| `StompFatalError` | `schemaVersion,messageType,errorCode,message,traceId` | `UNAUTHENTICATED | CSRF_INVALID | FORBIDDEN | ORIGIN_REJECTED | DESTINATION_NOT_ALLOWED | PROTOCOL_ERROR`; correlation/condition field 금지, `ERROR` frame 후 close |
| `GameParsedError` | base + `actionId,gameId,stateVersion,transitionId` | `NOT_GAME_PARTICIPANT | GAME_NOT_ACTIVE | NOT_YOUR_TURN | INVALID_GAME_PHASE | COMMAND_CONFLICT | CARD_CONDITION_NOT_MET | INSUFFICIENT_MANA | CARD_NOT_AVAILABLE | ILLEGAL_CHESS_MOVE | INVALID_PROMOTION_SELECTION | ACCOUNT_SUSPENDED`; 추가 condition 없음 |
| `GameStateMismatchError` | GameParsedError fields + `resyncRequired:true` | `STATE_VERSION_MISMATCH` |
| `GameValidationError` | GameParsedError fields + `fieldErrors` | `VALIDATION_FAILED` |
| `GameRateLimitError` | GameParsedError fields + `retryAfterSeconds` | `RATE_LIMITED` |
| `GameMalformedError` | base only | `messageType:GAME_COMMAND_MALFORMED`, `MALFORMED_REQUEST`; client ID 반사 금지 |
| `ChatParsedError` | base + `actionId,gameId` | `RESOURCE_NOT_FOUND | GAME_NOT_ACTIVE | CHAT_CLOSED | COMMAND_CONFLICT | COMMUNICATION_SUSPENDED | ACCOUNT_SUSPENDED`; gameplay version field 금지 |
| `ChatValidationError` | ChatParsedError fields + `fieldErrors` | `VALIDATION_FAILED` |
| `ChatRateLimitError` | ChatParsedError fields + `retryAfterSeconds` | `RATE_LIMITED` |
| `ChatMalformedError` | base only | `messageType:CHAT_COMMAND_MALFORMED`, `MALFORMED_REQUEST`; client ID 반사 금지 |

- game error는 `/user/queue/games/{gameId}`, chat error는 `/user/queue/games/{gameId}/chat`, fatal은 STOMP `ERROR`에만 허용한다.
- 공개 topic의 error, chat error의 stateVersion/transitionId, malformed error의 client correlation field는 privacy/structural negative다.

## 재사용 component

- `Color = WHITE | BLACK`
- `PieceType = KING | QUEEN | ROOK | BISHOP | KNIGHT | PAWN`
- `Phase = TURN_START | PRE_MOVE | PIECE_MOVE | PROMOTION | POST_MOVE | EFFECT_PENDING | TURN_END | GAME_ENDED`
- `CardInstanceRef = {cardInstanceId,definitionRef}`
- `PublicHand = {ownerColor,cards:[{definitionRef,count}]}`; count는 1 이상이다.
- `DefinitionOccurrence = {definitionRef} | {definitionRef,definitionView:CardDefinitionView}`. 해당 viewer registry 최초 출현은 view variant가 필수고, 이미 exact view를 등록한 뒤에는 ref-only 또는 동일 canonical view 반복을 허용한다.
- shared live public topic의 card occurrence는 항상 `PublicDefinitionOccurrence = {definitionRef,definitionView}`를 사용한다. ref-only 최적화는 viewer-private/snapshot 또는 replay top-level registry가 exact view를 먼저 보장한 뒤에만 허용한다. 다른 bytes/fingerprint는 fatal drift다.
- `players`와 `publicGeneralHands`는 `minItems=maxItems=2`, WHITE 후 BLACK이다.

## ViewerGameState

required: `ownColor,fen,turnNumber,turnColor,phase,players,publicGeneralHands,ownGeneralHand,ownUnusedLegend,visibleCardDefinitions,pendingCardEffect,ownPendingCardEffect,pendingPromotion,timer,terminalOutcome,opponentActions,lastViewerPrivateSequence`.

- players item: `{color,mana,checkReceivedCount,remainingGeneralDeckCount}`.
- own hand: `CardInstanceRef[]`; own legend: `null | CardInstanceRef`.
- public pending: `null | {actorColor,definitionRef,originPhase:PRE_MOVE|POST_MOVE}`.
- own pending: `null | {activationId,cardInstanceId,definitionRef,activationBaseStateVersion,originPhase,candidates}`. candidates는 canonical 6종 CandidateSet `$ref`다.
- promotion: `null | {from,to,color,choices:[QUEEN,ROOK,BISHOP,KNIGHT]}`.
- timer: `{timerState:"RUNNING",activeColor,whiteRemainingMillis,blackRemainingMillis,zeroAt,graceEndsAt}` 또는 `{timerState:"STOPPED",whiteRemainingMillis,blackRemainingMillis}`.
- terminal: `null | {outcomeType:"DECISIVE",winnerColor,loserColor} | {outcomeType:"DRAW"} | {outcomeType:"INVALID"}`.
- opponentActions: `{subjectRef,canBlock,canReportProfile}`.
- PROMOTION에서만 promotion non-null, EFFECT_PENDING에서만 public pending non-null이며 actor viewer만 own pending non-null, GAME_ENDED는 pending/promotion null·timer STOPPED·terminal non-null이다.

## ReplayGameState

- live state를 참조해 field를 금지하지 않고 별도 final object를 사용한다.
- required는 ViewerGameState에서 `ownPendingCardEffect,opponentActions,lastViewerPrivateSequence`를 제거한 나머지다.
- EFFECT_PENDING에서도 public pending만 허용한다. activation/card instance/candidate/selection/private failure는 state와 replay event 모두 금지한다.
- replay `initialState`와 모든 `stateAfter`는 이 component를 직접 `$ref`한다.

## Game inbound command와 sync

- game command final envelope는 `{schemaVersion:"1",actionId,gameId,intent,baseStateVersion,payload}`이며 intent와 payload를 다음 oneOf로 함께 닫는다.
  - `SKIP_PRE_MOVE | DRAW_CARD | PASS_POST_MOVE | RESIGN`: payload는 정확히 `{}`.
  - `MOVE_PIECE`: payload `{from,to}`.
  - `CHOOSE_PROMOTION`: payload `{pieceType}`이며 `QUEEN | ROOK | BISHOP | KNIGHT`만 허용한다.
  - `CARD_ACTIVATE`: payload `{cardInstanceId}`.
  - `CARD_RESOLVE`: payload `{activationId,selection}`이며 selection은 canonical 6종 Selection `$ref`다.
- sync request는 `{schemaVersion:"1",requestId,gameId}`이고 destination path의 `gameId`와 body가 같아야 한다.
- viewer snapshot은 `{schemaVersion:"1",messageType:"GAME_VIEWER_SNAPSHOT",requestId,gameId,stateVersion,projectionScope:"VIEWER_PRIVATE",serverTime,payload:ViewerGameState}`다.
- command accepted는 `{schemaVersion:"1",messageType:"GAME_COMMAND_ACCEPTED",actionId,gameId,stateVersion,transitionId}`다.

## GAME_TRANSITION

`{schemaVersion,messageType:"GAME_TRANSITION",eventId,gameId,stateVersion,transitionId,serverTime,payload}`이며 payload는 다음 final oneOf다.

- public: `{projectionScope:"PUBLIC",events,privateSequencesAfter:[{color,lastViewerPrivateSequence}]}`. 배열은 WHITE 후 BLACK 정확히 2개다.
- viewer-private: `{projectionScope:"VIEWER_PRIVATE",viewerPrivateSequence,events}`.
- viewer-private sequence는 viewer별 0 시작 단조 cursor이고 private envelope가 존재할 때 정확히 1 증가한다. public after cursor가 현재보다 같으면 private 없음, 1 크면 동일 tuple private를 기대하며, 2 이상 크면 즉시 sync한다. private가 public보다 먼저 오면 tuple/sequence로 보류한다.
- public 수신 시 after cursor가 +1인데 대응 private가 buffer에 없으면 FE는 2,000ms 단회 grace timer를 시작하고 그동안 신규 game command와 후속 delta 적용을 보류한다. 그 안에 exact private가 오면 적용하고 timer를 취소한 뒤 보류를 순서대로 처리하며, 만료·reconnect·새 public cursor 도착 중 하나가 먼저 발생하면 보류를 폐기하고 sync한다. late private는 snapshot cursor 기준 stale/duplicate 규칙으로 처리한다.

- event final shape는 `{ordinal,eventType,payload}`이며 ordinal은 0부터 연속이다.
- PUBLIC payload는 아래 17종, VIEWER_PRIVATE payload는 아래 6종만 허용한다.

### LivePublicGameEvent payload

| eventType | exact payload |
| --- | --- |
| `TURN_STARTED` | `{turnNumber,turnColor}` |
| `PHASE_CHANGED` | `{fromPhase,toPhase}`; 동일 값 금지 |
| `PRE_MOVE_SKIPPED` | `{actorColor}` |
| `PIECE_MOVED` | `PieceMovedPayload` oneOf |
| `PROMOTION_REQUIRED` | `{actorColor,from,to,choices:[QUEEN,ROOK,BISHOP,KNIGHT]}` |
| `PROMOTION_COMPLETED` | `{actorColor,from,to,pieceType,uci,san,resultingFen}` |
| `CARD_ACTIVATED` | `{actorColor,usedDefinition:PublicDefinitionOccurrence,actorPublicGeneralHandAfter:PublicHand}` |
| `EFFECT_PENDING` | `{actorColor,definitionRef,originPhase}` |
| `CARD_EFFECT_APPLIED` | `{actorColor,usedDefinition:PublicDefinitionOccurrence,outcome:CardAppliedOutcome}` |
| `CARD_EFFECT_FAILED` | `{actorColor,usedDefinition:PublicDefinitionOccurrence}` |
| `CARD_DRAWN` | `{actorColor,drawnDefinition:PublicDefinitionOccurrence,actorPublicGeneralHandAfter,remainingGeneralDeckCountAfter}` |
| `POST_MOVE_PASSED` | `{actorColor}` |
| `MANA_CHANGED` | `{color,before,after,delta,reasonCode}` |
| `CHECK_DECLARED` | `{checkingColor,checkedColor,checkReceivedCountAfter,doubleCheck}` |
| `TURN_ENDED` | `{turnNumber,turnColor}` |
| `TIMER_UPDATED` | `{timer}` |
| `GAME_ENDED` | `{reasonCode,terminalOutcome,endedAt}` |

`PieceMovedPayload` final oneOf:

- `QUIET`: common + `moveKind:"QUIET",capture:null,secondaryMove:null,notation:{status:"COMPLETED",uci,san}`.
- `CAPTURE`: common + `moveKind:"CAPTURE",capture:{square,pieceType,color},secondaryMove:null,notation:{status:"COMPLETED",uci,san}`.
- `EN_PASSANT`: common pawn move + `moveKind:"EN_PASSANT",capture:{square,pieceType:"PAWN",color},secondaryMove:null,notation:{status:"COMPLETED",uci,san}`.
- `CASTLING`: common king move + `moveKind:"CASTLING",capture:null,secondaryMove:{pieceType:"ROOK",from,to},notation:{status:"COMPLETED",uci,san}`.
- `PROMOTION_PENDING`: common pawn move + `moveKind:"PROMOTION_PENDING",capture:null|{square,pieceType,color},secondaryMove:null,notation:{status:"PENDING_PROMOTION"}`. 완료 UCI/SAN은 금지한다.
- common은 `actorColor,from,to,movedPieceType,resultingFen`이다.

`CardAppliedOutcome`은 다음 canonical `outcomeType` oneOf다.

- `{outcomeType:"PIECE_RELOCATED",from,to,resultingFen}`.
- `{outcomeType:"PAWNS_RELOCATED",moves:[{from,to}],resultingFen}`. `moves`는 1개 이상이며 이동 전 `from` square 순으로 결정적 정렬한다.
- `{outcomeType:"CASTLING_RELOCATED",king:{from,to},rook:{from,to},resultingFen}`.
- `{outcomeType:"PIECES_SWAPPED",squares:[square,square],resultingFen}`. 서로 다른 두 square를 오름차순 정렬한다.
- `{outcomeType:"PIECE_CONVERTED",square,pieceType,fromColor,toColor,resultingFen}`. `fromColor`와 `toColor`는 서로 다르다.

### viewer-private event payload

| eventType | exact payload |
| --- | --- |
| `CARD_ACTIVATED` | `{activationId,cardInstanceId,definitionRef}` |
| `EFFECT_PENDING` | `{ownPendingCardEffect}`; non-null full actor pending |
| `CARD_EFFECT_APPLIED` | `{activationId,selection}`; selection형만 |
| `CARD_EFFECT_FAILED` | `{activationId,selection,failureCode}` 선택형 variant 또는 `{failureCode}` 무대상 variant |
| `PRIVATE_HAND_UPDATED` | `{ownGeneralHandAfter:CardInstanceRef[]}` |
| `PRIVATE_LEGEND_UPDATED` | `{ownUnusedLegendAfter:null|CardInstanceRef}` |

- private failure code: `SELECTION_NOT_CANDIDATE | EFFECT_NOT_APPLICABLE | KING_SAFETY_VIOLATION | GAME_INVARIANT_VIOLATION`.
- public event에 action/card instance/activation/candidate/selection/failureCode/subjectRef가 있으면 privacy-negative다.
- `LivePublicGameEvent`는 위 표의 final union이며 card occurrence에 `PublicDefinitionOccurrence`만 허용한다.
- `ReplayGameEvent`는 같은 eventType/payload 의미를 가진 별도 final union이지만 card occurrence는 top-level `visibleCardDefinitions`로 먼저 등록된 `{definitionRef}`만 허용한다. live public union을 `$ref`하지 않고 private event와 sequence field도 포함하지 않는다.
- live ref-only occurrence, replay unknown ref와 replay event의 view-bearing occurrence를 structural/stateful negative fixture로 거부한다.

## Chat normal messages

- send command: `{schemaVersion,actionId,gameId,text}`.
- accepted: `{schemaVersion,messageType:"CHAT_SEND_ACCEPTED",actionId,gameId,message:ChatMessageView}`.
- received: `{schemaVersion,messageType:"CHAT_MESSAGE_RECEIVED",gameId,message:ChatMessageView}`.
- history와 live의 `ChatMessageView`는 동일 canonical `$ref`를 사용한다.

## Channel registry

- `CONNECT` frame은 handshake session cookie와 exact Origin을 사용하고 native headers `{accept-version:"1.2",host,heart-beat,X-CSRF-TOKEN}`를 요구한다. Authorization/session/token query parameter와 body를 금지한다.
- `SUBSCRIBE` frame은 `{id,destination,ack:"auto"}` header와 빈 body만 허용하며 아래 server destination 중 현재 principal이 승인된 것만 허용한다. 임의 다른 game/user destination은 `DESTINATION_NOT_ALLOWED` fatal error다.

Authorization scope literal은 다음으로 닫는다.

- `SESSION_CONNECT`: valid session, exact Origin, CSRF와 허용 account state.
- `GAME_PARTICIPANT`: authenticated current game participant; account suspension 거부.
- `VIEWER_GAME_PARTICIPANT`: `GAME_PARTICIPANT`이며 user destination principal과 일치.
- `ACTIVE_MATCHMAKING_USER`: ACTIVE account의 본인 matchmaking user destination.
- `CURRENT_GAME_CHAT_VIEWER`: current game participant이며 account suspension 없음. communication suspension은 과거/current chat 구독·수신을 막지 않는다.
- `CURRENT_GAME_CHAT_SENDER`: `CURRENT_GAME_CHAT_VIEWER`이며 communication suspension도 없음.
- `SERVER_FATAL_CONTEXT`: CONNECT 또는 이미 결합된 session에 대한 fatal delivery context.

| direction | destination | authorization scope | allowed schema |
| --- | --- | --- | --- |
| CLIENT_CONNECT | STOMP `CONNECT` | `SESSION_CONNECT` | ConnectFrame |
| CLIENT_SUBSCRIBE | `/topic/games/{gameId}` | `GAME_PARTICIPANT` | SubscribeFrame |
| CLIENT_SUBSCRIBE | `/user/queue/games/{gameId}` | `VIEWER_GAME_PARTICIPANT` | SubscribeFrame |
| CLIENT_SUBSCRIBE | `/user/queue/matchmaking` | `ACTIVE_MATCHMAKING_USER` | SubscribeFrame |
| CLIENT_SUBSCRIBE | `/user/queue/games/{gameId}/chat` | `CURRENT_GAME_CHAT_VIEWER` | SubscribeFrame |
| CLIENT_TO_SERVER | `/app/games/{gameId}/commands` | `GAME_PARTICIPANT` | 8 command oneOf |
| CLIENT_TO_SERVER | `/app/games/{gameId}/sync` | `GAME_PARTICIPANT` | GameSyncRequest |
| SERVER_TO_CLIENT | `/topic/games/{gameId}` | `GAME_PARTICIPANT` | public GameTransition only |
| SERVER_TO_CLIENT | `/user/queue/games/{gameId}` | `VIEWER_GAME_PARTICIPANT` | snapshot, receipt, game error, private transition |
| SERVER_TO_CLIENT | `/user/queue/matchmaking` | `ACTIVE_MATCHMAKING_USER` | MatchmakingStateChanged |
| CLIENT_TO_SERVER | `/app/games/{gameId}/chat/messages` | `CURRENT_GAME_CHAT_SENDER` | ChatSendCommand |
| SERVER_TO_CLIENT | `/user/queue/games/{gameId}/chat` | `CURRENT_GAME_CHAT_VIEWER` | accepted, received, chat error |
| SERVER_ERROR | STOMP `ERROR` | `SERVER_FATAL_CONTEXT` | StompFatalError |

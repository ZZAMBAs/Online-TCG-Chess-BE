# Canonical REST Component Registry

## 공통 wrapper

- `Page<T> = {schemaVersion:"1",items:T[],nextCursor:string|null}`.
- 모든 response nullable property는 required다.
- 모든 request optional property는 생략만 허용하고 null을 금지한다.
- ID/ref는 비어 있지 않은 opaque string, revision/version/count는 0 이상 JSON-safe integer, timestamp는 UTC millisecond `Z`다.
- email은 trim된 표준 email 형식, nickname은 fixed spec의 2~20 Unicode code point, password/newPassword는 fixed auth password 정책을 적용한다.

## Auth components

- `CsrfTokenResponse = {schemaVersion:"1",token}`.
- `AuthSession = {schemaVersion:"1",authenticated:false} | {schemaVersion:"1",authenticated:true,accountStatus,roles,activeRestrictions}`.
- `CurrentConsentsResponse = {schemaVersion:"1",termsVersion,privacyPolicyVersion}`.
- `LocalRegistrationRequest = {email,password,nickname,termsVersion,privacyPolicyVersion,termsAgreed:true,privacyPolicyAgreed:true}`.
- `LocalLoginRequest = {email,password}`.
- `EmailVerificationConfirmRequest = {token}`.
- `PasswordResetRequest = {email}`; `PasswordResetConfirmRequest = {token,newPassword}`.
- `OAuthOnboardingRequest = {nickname,termsVersion,privacyPolicyVersion,termsAgreed:true,privacyPolicyAgreed:true}`.
- `OAuthResult = {schemaVersion:"1",purpose:"LOGIN",outcome:AUTHENTICATED|ONBOARDING_REQUIRED|LOCAL_EMAIL_COLLISION|CANCELLED|FAILED} | {schemaVersion:"1",purpose:"WITHDRAWAL",outcome:WITHDRAWAL_REAUTHENTICATED|CANCELLED|FAILED} | {schemaVersion:"1",purpose:"REACTIVATION",outcome:REACTIVATED|CANCELLED|FAILED} | {schemaVersion:"1",purpose:null,outcome:"FAILED"|"NO_PENDING_OAUTH_RESULT"}`. purpose-null FAILED는 state를 신뢰할 수 없어 purpose를 권위적으로 결정할 수 없는 callback 실패다.
- `WithdrawalRequest = {method:"LOCAL",currentPassword} | {method:"OAUTH"}`.
- `LocalReactivationStartRequest = {email,password}`; `LocalReactivationConfirmRequest = {token}`.

## Identity components

- `MyProfileResponse = {schemaVersion:"1",nickname,signInMethod:{type:"LOCAL"}} | {schemaVersion:"1",nickname,signInMethod:{type:"OAUTH",provider:"GOOGLE"|"KAKAO"}}`.
- `AccessStatusResponse = {schemaVersion,accountStatus,requiredActions,activeRestrictions}`.
- restriction item은 `{type,startsAt,endsAt,reason}`, endsAt required nullable다.
- `SettingsView = {schemaVersion,revision,matchChatVisible,optionalInAppNotificationsEnabled,serviceEmailNotificationsEnabled}`.
- `ReplaceSettingsRequest = {revision,matchChatVisible,optionalInAppNotificationsEnabled,serviceEmailNotificationsEnabled}`.
- `NotificationPage = Page<NotificationView>`.
- `NotificationView`는 공통 `notificationId,createdAt`에 다음 oneOf를 결합한다: `{notificationType:"REPORT_RESOLVED",content:{reportId,result}} | {notificationType:"ADMIN_ANNOUNCEMENT",content:{announcementId,importance,title,body}} | {notificationType:"ACCOUNT_RESTRICTION",content:{restrictionType,startsAt,endsAt,reason}}`.

## Card, pack and deck components

- `CardDefinitionRef = {cardId,cardVersion,definitionFingerprint,viewFingerprint}`. 두 fingerprint는 `sha256:` 뒤 lowercase hex 64자다.
- `CardDefinitionView = {cardId,cardVersion,definitionFingerprint,viewFingerprint,name,type,packId,image,timing,manaCost,summary,useGuide,selectionKind}`.
- `type = NORMAL | LEGEND`, `packId = BASIC`, `image = string|null`, `timing`은 `PRE_MOVE|POST_MOVE`의 1~2개 중복 없는 PRE_MOVE 우선 배열, `manaCost`는 0 이상 safe integer다.
- `selectionKind = NONE | PAWN_AND_DIRECTION | PAWN | ROOK | UNORDERED_PIECE_PAIR | FROM_TO | TARGET_PIECE`다. name/summary/useGuide는 비어 있지 않은 plain text이고 HTML로 해석하지 않는다.
- `CardCatalogResponse = {schemaVersion,catalogViewFingerprint,cards:CardDefinitionView[]}`.
- `CardCollectionView = {schemaVersion,revision,entries:[{cardId,quantity}]}`.
- `BasicPackView = {schemaVersion,packId:"BASIC",priceGold:0,cardsPerOpening:3,legendProbabilityBasisPoints:100,probabilityVersion,quota}`.
- `QuotaView = {kstDate,successfulOpenings,dailyLimit:10,remainingOpenings,resetsAt}`.
- `BasicPackOpeningResult = {schemaVersion,openingId,packId:"BASIC",probabilityVersion,openedAt,rewards,collectionRevision,quota}`; rewards는 slot 1/2/3 정확히 세 `{slot,cardId,quantity:1}`다.
- `DeckView = {schemaVersion,deckId,revision,entries,valid,invalidReasonCodes}`; entries는 `{cardId,quantity}`, reason은 `CARD_NOT_ACTIVE | OWNED_QUANTITY_EXCEEDED | DECK_COMPOSITION_INVALID`다.
- `ReplaceDeckRequest = {expectedRevision,entries}`.
- `EmptyJsonObject = {}`.

## Matchmaking and match history components

- `CreateQuickMatchAttemptRequest = {deckId,deckRevision}`.
- `QuickMatchStateView` 공통은 `{schemaVersion:"1",queueEntryId,stateVersion,serverTime}`이고 다음 state oneOf다: `{state:"WAITING"}|{state:"CANCELED"}|{state:"MATCH_CONFIRMED"}|{state:"GAME_CREATED",gameId,ownColor}|{state:"FAILED",failureCode}`. ownColor은 `WHITE|BLACK`, failureCode는 `DECK_CHANGED|DECK_INVALID|ACCOUNT_NOT_ELIGIBLE|MATCH_CREATION_FAILED`다.
- `MatchHistorySummary = {schemaVersion,countedMatches,wins,losses,draws,winRate}`.
- `MatchHistoryPage = Page<MatchHistoryItem>` 최대 10개.
- `PublicAccountLabel = {labelType:"ACTIVE",nickname} | {labelType:"WITHDRAWN"}`.
- `MatchHistoryItem = {gameId,opponent:PublicAccountLabel,color,startedAt,endedAt,reasonCode,result}`; result `WIN|LOSS|DRAW`, reason에 `SERVER_ABORTED` 금지.
- `MatchReplay = {schemaVersion,gameId,viewerColor,startedAt,endedAt,terminalOutcome,initialState,steps,visibleCardDefinitions}`.
- `ReplayStep = {stepIndex,stateVersion,transitionId,serverTime,events:ReplayGameEvent[],stateAfter}`; event와 state는 `stomp-registry.md`의 별도 replay final union/component를 직접 참조한다.

## Chat and community components

- `ChatMessageView = {chatMessageId,sequence,senderColor,maskedText,sentAt}`.
- `ChatMessagePage = Page<ChatMessageView>` 최대 50개.
- `CommunityPostView = {postId,revision,title,body,author,capabilities,authorActions,createdAt,contentUpdatedAt}`.
- author는 `PublicAccountLabel`; capabilities는 `{canEdit,canDelete,canReportPost}`; authorActions는 required `null|{subjectRef,canBlock,canReportProfile}`.
- `CommunityPostPage = Page<CommunityPostView>` 최대 20개.
- `CreateCommunityPostRequest = {title,body}`.
- `UpdateCommunityPostRequest = {expectedRevision,title?,body?}`이며 title/body 중 최소 하나다.
- `DeleteCommunityPostRequest = {expectedRevision}`.
- community title은 trim 1~100 Unicode code point, body는 1~1,000 code point이고 둘 다 plain text다. update의 present field에도 같은 제약을 적용한다.

## Block and report components

- `CreateBlockRequest = {subjectRef}`; `DeleteBlockRequest = {expectedRevision}`.
- `BlockView = {blockId,revision,blockedUser:PublicAccountLabel,blockedAt}`.
- `BlockResponse = {schemaVersion,block:BlockView}`.
- `CreateReportRequest = {target,reasonCode,detail?}`. target은 `{targetType:"CHAT_MESSAGE",chatMessageId}|{targetType:"COMMUNITY_POST",postId}|{targetType:"USER_PROFILE",subjectRef}`.
- reason은 `HARASSMENT | HATE_SPEECH | SEXUAL_CONTENT | SPAM | INAPPROPRIATE_NAME | OTHER`.
- detail은 생략 가능하고 present 시 trim 1~500 Unicode code point plain text다.
- `OwnReportView` 공통 `{reportId,targetType,reasonCode,submittedAt,status,resolvedAt,result}`; OPEN은 마지막 두 field null, RESOLVED는 non-null `ACTION_TAKEN|NO_ACTION`이다.
- `OwnReportResponse = {schemaVersion,report:OwnReportView}`.

## Admin case and evidence components

- `ReportCaseListItem = {caseId,revision,targetType,status,createdAt,latestReportedAt,memberReportCount,resolvedAt,result}`; OPEN/RESOLVED nullability는 report와 같다.
- `AdminCaseTarget = {targetType:"CHAT_MESSAGE",chatMessageId} | {targetType:"COMMUNITY_POST",postId} | {targetType:"USER_PROFILE",subjectRef,nickname}`.
- `AdminMemberReport = {reportId,reporter:{subjectRef,nickname},reasonCode,submittedAt,evidenceAvailability}`.
- `QualifyingAction = {actionRef,actionType,actedAt}`; type `AUTO_HIDE | ADMIN_HIDE | SANCTION_CREATE | SANCTION_EXTEND`.
- `ReportCaseDetail = {caseId,revision,target,status,createdAt,latestReportedAt,resolvedAt,result,reports,qualifyingActions}`.
- `ReportCaseResponse = {schemaVersion,case:ReportCaseDetail}`.
- `RawEvidenceResponse = {schemaVersion,evidence}`이며 evidence는 다음 oneOf다.
  - chat `{evidenceType:"CHAT_MESSAGE",chatMessageId,gameId,sender,reporter,rawText,maskedText,sentAt,detail}`
  - post `{evidenceType:"COMMUNITY_POST",postId,postRevision,author,reporter,rawTitle,maskedTitle,rawBody,maskedBody,detail}`
  - profile `{evidenceType:"USER_PROFILE",target,reporter,detail}`
- 모든 detail은 required nullable이고 party ref는 `{subjectRef,nickname}`다.
- `ResolveReportCaseRequest` oneOf:
  - `{expectedRevision,result:"NO_ACTION"}`
  - `{expectedRevision,result:"ACTION_TAKEN",actionSource:{type:"EXISTING_ACTION",actionRef}}`
  - `{expectedRevision,result:"ACTION_TAKEN",actionSource:{type:"CREATE_SANCTION",sanctionType,duration,reason}}`
  - `{expectedRevision,result:"ACTION_TAKEN",actionSource:{type:"HIDE_POST",expectedPostRevision,reason}}`

## Moderation and sanction components

- `ModerateCommunityPostRequest = {expectedRevision,action:"HIDE"|"RESTORE",reason,sourceCaseId?}`.
- `ModerationActionResponse = {schemaVersion,moderationAction:{actionRef,postId,postRevision,action,resultingState,actedAt}}`; HIDE→MANUAL_HIDDEN, RESTORE→ACTIVE.
- `AdminUserSearchItem = {subjectRef,nickname,accountStatus,sanctionSetRevision,activeSanctionTypes}`.
- `Duration = {type:"PRESET_DAYS",days:1|3|7|30} | {type:"CUSTOM_ENDS_AT",endsAt}`.
- `SanctionView = {sanctionId,revision,sanctionType,startsAt,endsAt,reason,status,revokedAt,revokeReason,sourceCaseId}`.
- ACTIVE/EXPIRED는 revokedAt/revokeReason null, REVOKED는 non-null; sourceCaseId는 required nullable.
- `CreateSanctionRequest = {expectedSanctionSetRevision,sanctionType,duration,reason,sourceCaseId?}`.
- `CreateSanctionResponse = {schemaVersion,sanction,sanctionSetRevision,actionRef}`.
- `SanctionActionResponse = {schemaVersion,sanction,actionRef}`.
- `ExtendSanctionRequest = {expectedRevision,endsAt}`; `RevokeSanctionRequest = {expectedRevision,reason}`.

## Dictionary, card admin and announcement components

- `ForbiddenWordView = {forbiddenWordId,revision,value,createdAt,updatedAt}`.
- `ForbiddenWordResponse = {schemaVersion,forbiddenWord:ForbiddenWordView}`.
- `CreateForbiddenWordRequest = {value,changeReason}`; `UpdateForbiddenWordRequest = {expectedRevision,value,changeReason}`; `DeleteForbiddenWordRequest = {expectedRevision,changeReason}`.
- admin cards는 `Page<CardDefinitionView>`를 직접 사용하고 별도 item component를 만들지 않는다.
- `AnnouncementCreateResult = {schemaVersion,announcementId,importance,createdAt,eligibleCount,deliveredCount,skippedCount}`; eligible = delivered + skipped.
- `CreateAnnouncementRequest = {title,body,importance}`.
- announcement request title은 trim 1~100 Unicode code point이며 line break를 금지하고, body는 1~1,000 code point이며 line break를 허용한다. importance는 `NORMAL|IMPORTANT`다.

## Schema-level constraints

- 각 object의 field는 위 목록이 전체 required/allowed set이다. oneOf variant에서 열거하지 않은 field는 금지한다.
- 문자열 길이, cursor 결합, 배열 정렬·unique·최대 page size와 revision 규칙은 해당 fixed topic summary를 schema constraint와 stateful fixture로 함께 검증한다.

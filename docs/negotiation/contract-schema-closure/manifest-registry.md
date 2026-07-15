# Canonical Contract Manifest Registry

## Manifest schema

```text
Manifest {
  schemaVersion:"1",
  bundleFormatVersion:"1",
  jsonSchemaDialect:"https://json-schema.org/draft/2020-12/schema",
  hashAlgorithm:"SHA-256-RFC8785",
  files: FileEntry[1..],
  openapi:{operations:OpenApiOperation[1..]},
  stomp:{channels:StompChannel[1..]},
  fixtures:FixtureEntry[1..],
  cardContracts:CardContractEntry[1..],
  rootFingerprint:Sha256
}
```

- manifest 자체는 `files[]`와 per-file hash에서 제외한다.
- root fingerprint는 자기 `rootFingerprint` property만 제외한 manifest canonical value를 hash한다.
- 모든 path/ref는 bundle-root 상대 경로이며 absolute, `..`, external URI와 unresolved ref를 금지한다.

## child schema

```text
FileEntry {
  path,
  mediaType,
  role: OPENAPI|JSON_SCHEMA|FIXTURE|GENERATED_METADATA,
  sha256
}

OpenApiOperation {
  operationId,
  method: GET|POST|PUT|PATCH|DELETE,
  path,
  security:{profile,csrfRequired,idempotencyKeyRequired,auditedRead},
  parameters: [{location:PATH|QUERY|HEADER,name,required,schemaRef}],
  request: {kind:"NO_BODY"}|{kind:"JSON_BODY",schemaRef},
  successes: SuccessVariant[1..],
  errors: ErrorVariant[]
}

SuccessVariant {
  status,
  body:{kind:"NO_BODY"}|{kind:"JSON_BODY",schemaRef},
  requiredHeaders:[string],
  fixtureIds:[string][1..]
}

ErrorVariant {
  status,
  errorCode,
  schemaRef,
  requiredHeaders:[string],
  fixtureIds:[string][1..]
}

StompChannel {
  channelId,
  direction:CLIENT_CONNECT|CLIENT_SUBSCRIBE|CLIENT_TO_SERVER|SERVER_TO_CLIENT|SERVER_ERROR,
  destinationPattern,
  wireDiscriminator:
    {kind:"MESSAGE_TYPE",value}|
    {kind:"INTENT",value}|
    {kind:"NONE"},
  schemaRef,
  authorizationScope:SESSION_CONNECT|GAME_PARTICIPANT|VIEWER_GAME_PARTICIPANT|ACTIVE_MATCHMAKING_USER|CURRENT_GAME_CHAT_VIEWER|CURRENT_GAME_CHAT_SENDER|SERVER_FATAL_CONTEXT,
  fixtureIds:[string][1..]
}

FixtureEntry {
  fixtureId,
  class:POSITIVE|STRUCTURAL_NEGATIVE|DOMAIN_NEGATIVE|PRIVACY_NEGATIVE|SEQUENCE|PROVENANCE_DRIFT,
  transport:REST|STOMP|CONTRACT_BUNDLE,
  targetRef,
  path,
  sha256,
  covers:CoverageKey[1..]
}

CoverageKey {
  targetKind:OPERATION|CHANNEL|SCHEMA_VARIANT|BUNDLE_ROOT|FILE|FE_ADOPTION_PIN|CHECKED_IN_COPY,
  targetId,
  variant,
  status?,
  errorCode?,
  assertion
}

CardContractEntry {
  cardId,
  cardVersion,
  definitionFingerprint,
  viewFingerprint,
  selectionKind,
  activationSchemaRef,
  resolveSchemaRef:null|SchemaRef,
  candidateSchemaRef:null|SchemaRef,
  selectionSchemaRef:null|SchemaRef,
  publicOutcomeSchemaRef,
  privateOutcomeSchemaRef,
  handlerContract,
  fixtureIds:[string][1..]
}
```

- file path, operationId, `(method,path)`, channelId, fixtureId와 CoverageKey는 unique하고 결정적 정렬한다.
- success/error는 status별 별도 항목이다. 200/201, 202/204, 302/303, 304를 합치지 않는다. no-body는 명시적 `NO_BODY`다.
- STOMP command channel은 `INTENT`, normal/error outbound는 `MESSAGE_TYPE`, sync와 CONNECT처럼 body discriminator가 없는 channel은 `NONE`을 사용한다. discriminator와 schema variant의 literal은 정확히 일치해야 한다.
- `CARD_004`만 resolve/candidate/selection schema ref가 null이고 그 외 deployable card version은 세 ref가 non-null이다. handlerContract는 실행 코드 이름이 아니라 version별 안정 계약 ID다.
- manifest 밖 file, stale/missing/unmanifested file, 중복 target과 존재하지 않는 ref는 생성 실패다.

## coverage completeness

| 대상 | required fixture coverage |
| --- | --- |
| REST operation × success status | positive 1개 이상, body/no-body/required header 검증 |
| REST operation × error status × code | domain-negative 1개 이상, status/code/condition/header 검증 |
| request/response final object | required 누락, additional field, type/null 위반 structural-negative |
| discriminator variant | positive 1개와 unknown/wrong discriminator negative |
| conditional error | required condition 누락, forbidden condition 추가와 wrong header negative |
| STOMP channel × wire schema variant | `MESSAGE_TYPE`, `INTENT`, `NONE` 각각 positive 1개 이상, direction/destination/auth scope 검증 |
| game public/private | scope 교차와 private field public leakage privacy-negative |
| reducer sequence | receipt/transition 순서, private/public 순서, duplicate/stale/gap/tuple conflict/snapshot recovery |
| replay | random seek/stateAfter 원자 교체와 private field 금지 |
| definition registry | first ref without view, unknown ref, fingerprint drift |
| provenance | missing/stale/unmanifested, external ref, hash mismatch, FE pin/copy/generated mismatch |

- generator는 operation/channel/schema/card contract에서 기대 CoverageKey 집합을 계산하고 fixture covers 합집합과 정확히 일치해야 한다.
- 미커버/중복 target, fixture 없는 union variant와 schema 없는 operation/channel은 bundle 생성 실패다.
- `MESSAGE_TYPE|INTENT`는 wrong/missing discriminator, `NONE`은 임의 discriminator 추가를 structural-negative fixture로 검증한다.
- provenance fixture는 `CONTRACT_BUNDLE` transport와 `BUNDLE_ROOT | FILE | FE_ADOPTION_PIN | CHECKED_IN_COPY` target kind를 사용해 root hash, per-file hash, exact FE full commit pin과 checked-in copy를 각각 독립 검증한다.

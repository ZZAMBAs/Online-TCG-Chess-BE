# 카드 데이터 형식

이 디렉터리에는 MVP 카드의 마스터 데이터를 카드별 JSON 파일로 저장한다.
카드 JSON은 카드 조회 응답, 카드 사용 계약, 카드 공개/비공개 projection을 정의할 때 참고하는 원천 자료다.

## 파일 규칙

- 최초 버전 카드 파일명은 `{id}.json`, 후속 버전은 `{id}.v{version}.json` 형식을 사용한다. 파일명보다 JSON의 `id`와 `version` 조합이 권위 식별자다.
- `id`는 한 번 정하면 변경하지 않는다.
- 같은 `(id, version)` 정의는 배포 후 제자리 수정하거나 삭제하지 않는다.
- 비용, timing, 발동 조건, 후보 규칙, 효과, 효과 실패 시 소비, visibility 또는 projection 의미가 바뀌면 새 version을 발행한다. 아직 배포·고정되지 않은 최초 협상본의 보완은 version 1 안에서 완료할 수 있다.
- 현재 MVP 카드팩 ID는 `BASIC`이다.
- 카드 효과는 서버가 권위적으로 판정하며, JSON의 설명만으로 클라이언트가 결과를 계산하지 않는다.
- 카드별 JSON에는 사용자에게 보여줄 문구와 서버 검증에 필요한 의미 정보를 함께 기록한다.
- 현재 신규 경기에 사용할 버전은 카드 JSON의 필드가 아니라 `active-versions.json`에서 카드 식별자별로 하나씩 지정한다.
- 활성 버전 변경은 `active-versions.json` 변경, catalog 검증과 새 배포를 통해서만 수행한다.

## 공통 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string | 카드의 영구 식별자. 예: `CARD_001_PAWN_SIDE_STEP` |
| `name` | string | 사용자에게 표시할 카드명 |
| `type` | enum | 카드 종류. `NORMAL`은 일반 카드, `LEGEND`는 레전드 카드 |
| `packId` | string | 카드가 포함된 카드팩 식별자. MVP에서는 `BASIC`만 사용 |
| `image` | string 또는 null | 카드 이미지 asset 경로 또는 asset key. 이미지가 없으면 `null` |
| `timing` | enum 배열 | 카드를 사용할 수 있는 모든 턴 단계. 가능한 시기를 배열에 빠짐없이 기록 |
| `manaCost` | number | 카드 사용에 필요한 마나 |
| `target` | object | 카드가 적용될 대상과 대상 선택에 필요한 입력 |
| `activationConditions` | string 배열 | 카드를 내기 전에 충족해야 하는 최초 발동 조건. 실패하면 비소모 거부 |
| `effect` | object | 카드 효과의 사용자 설명과 구조화된 의미 정보 |
| `resolution` | object | 발동 뒤 효과 해결 명령·실패·rollback·재선택 정책 |
| `effectFailureConditions` | string 배열 | 발동은 성공했지만 효과 적용이 실패하는 대표 조건. 비용은 유지 |
| `uiText` | object | FE가 표시할 설명과 사용 안내 문구 |
| `visibility` | object | 카드가 상대에게 공개되는 시점 |
| `version` | number | 카드 정의 버전. 규칙 또는 FE/BE 계약 의미가 변경되면 단조 증가 |

## 활성 버전 목록

`active-versions.json`은 신규 경기와 현재 상품 노출에 사용할 카드 버전을 지정한다.

- `schemaVersion`: 활성 목록 형식 버전
- `cards`: `{id, version}` 항목의 배열
- 같은 카드 식별자는 정확히 한 번만 나타나야 한다.
- 항목은 반드시 같은 디렉터리에 존재하는 카드 정의의 `id`와 `version`을 가리켜야 한다.
- 카드 정의 파일에 활성 여부를 중복 기록하지 않는다.

## 허용 enum

### `type`

- `NORMAL`: 일반 카드. 경기 중 손패가 상대에게 공개된다.
- `LEGEND`: 레전드 카드. 사용 전까지 상대에게 공개되지 않는다.

### `timing`

- `PRE_MOVE`: 기물 이동 전 카드 행동
- `POST_MOVE`: 기물 이동 후 카드 행동

향후 새로운 사용 시기가 추가되면 기존 값을 재해석하지 않고 새 enum 값을 추가한다.
카드가 여러 시기에 사용 가능하면 `timing` 배열에 가능한 값을 모두 기록한다.

### `visibility`

- `PUBLIC`: 상대에게 공개 가능
- `PRIVATE`: 해당 카드 소유자에게만 공개

## `target` 형식

`target.type`은 사용자가 지정해야 하는 대상의 의미를 나타낸다. 따라서 대상 종류를 표현하기 위해 별도의 `condition` 필드를 사용하지 않는다.
발동 전에 후보 존재 여부를 판정하는 제약은 `activationConditions`에 기록하고, 발동 뒤 선택·최종 불변식 때문에 효과가 실패하는 조건은 `effectFailureConditions`에 기록한다.

예시는 다음과 같다.

- `OWN_PAWN`: 자신의 폰
- `OWN_PIECE`: 자신의 기물
- `OWN_ROOK`: 자신의 룩
- `OPPONENT_PIECE`: 상대 기물
- `BOARD_SQUARE`: 체스판의 칸
- `NONE`: 별도 대상 선택 없음

`count`는 선택할 대상 수다.
카드 사용 시 클라이언트가 추가 입력을 제출해야 하면 `parameters`에 입력 이름, 타입, 허용값, 필수 여부를 기록한다.
기물과 도착 칸을 함께 선택하는 카드는 `parameters.destination`을 `BOARD_SQUARE` 타입으로 기록한다.
여러 대상을 선택하는 카드가 중복을 허용하지 않으면 `distinct: true`, 선택 순서에 의미가 없으면 `ordered: false`를 기록한다.

## 방향과 보드 orientation

카드 방향은 FE 화면의 회전 상태가 아니라 카드 사용자 진영 기준으로 해석한다.
서버 상태, 후보, 명령 결과와 기보의 칸 좌표는 항상 canonical `a1`~`h8`를 사용한다.
live FE는 자신의 home rank가 화면 아래쪽에 보이도록 표시하지만 presentation orientation으로 canonical 좌표를 변경하지 않는다.

허용 방향 enum과 file/rank 변화량은 다음과 같다.

| 방향 | 백 | 흑 |
| --- | --- | --- |
| `LEFT` | `(-1, 0)` | `(+1, 0)` |
| `RIGHT` | `(+1, 0)` | `(-1, 0)` |
| `FORWARD` | `(0, +1)` | `(0, -1)` |
| `FORWARD_LEFT` | `(-1, +1)` | `(+1, -1)` |
| `FORWARD_RIGHT` | `(+1, +1)` | `(-1, -1)` |

`UP_LEFT`, `UP_RIGHT`는 사용하지 않는다.
서버는 경기 상태에서 확인한 카드 사용자의 색상으로 방향을 계산하고 client가 보낸 색상이나 board perspective를 신뢰하지 않는다.

## `effect` 형식

- `summary`: 사용자와 문서에서 사용할 짧은 효과 설명
- `details`: 서버 구현과 계약 협상에서 해석할 수 있는 구조화된 효과 정보

`details`에는 가능한 경우 대상 기물, 이동 거리, 방향, 수량, 상태 변화처럼 검증에 필요한 값을 별도 필드로 기록한다.
단, 카드 JSON은 범용 효과 DSL이 아니며 MVP에서는 카드별 서버 핸들러가 최종 효과를 구현한다.

### `effect.details` 공통 필드

이동 효과에서 반복적으로 사용하는 필드는 다음과 같다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `piece` | enum | 효과를 받는 기물 종류. 예: `OWN_PAWN`, `OWN_ROOK`, `OWN_KING_AND_ROOK`, `OPPONENT_PIECE` |
| `selection` | enum | 효과 대상의 선택 방식. `SINGLE`은 1개, `MULTIPLE`은 여러 개, `ALL_ELIGIBLE`은 조건을 만족하는 전체 대상, `USER_CHOICE_AMONG_CLOSEST`는 서버가 계산한 최단거리 후보 중 사용자가 1개를 선택함을 의미 |
| `filter` | enum 배열 | `ALL_ELIGIBLE` 대상 중 실제 효과를 적용할 대상을 고르는 조건 |
| `distance` | number | 이동 칸 수. 이동 효과가 아닌 경우에는 생략 |
| `direction` | enum | 카드 사용자 진영 기준 이동 방향. 예: `LEFT`, `RIGHT`, `FORWARD_LEFT`, `FORWARD_RIGHT`, `FORWARD` |
| `promotion` | enum | 효과로 폰이 끝 행에 도달했을 때의 프로모션 처리. `DISABLED`는 프로모션을 발생시키지 않음을 의미 |
| `movement` | object | 기물의 일반적인 이동 규칙과 이동 거리, 도착 칸 제약을 함께 표현하는 이동 효과 정보 |
| `distanceMetric` | enum | 거리 계산 방식. `MANHATTAN`은 두 칸의 파일·랭크 차이 절댓값 합을 의미 |
| `conversion` | enum | 효과 대상의 소유권 변경 방식. `OPPONENT_TO_OWN`은 상대 기물을 자신의 기물로 변경하는 방식 |
| `excludePieces` | enum 배열 | 서버 후보 계산에서 제외할 기물 종류. 예: `OPPONENT_KING` |
| `ownershipAfterEffect` | enum | 소유권 변경 뒤 기물 이력과 특수 상태 처리. `PRESERVE_HISTORY_USE_NEW_OWNER_RULES`는 이력을 유지하고 이후 이동 규칙은 새 진영을 따름을 의미 |
| `halfmoveClock` | enum | 카드 효과의 50수 규칙 처리. `RESET_ON_PAWN_MOVE_OR_CAPTURE`는 폰 이동·캡처 때만 0으로 초기화하고 `PRESERVE`는 현재 값을 유지함을 의미 |
| `castlingRightsAfterEffect` | enum | 교환·전환 효과 뒤 캐슬링 권리 처리. 대상 룩의 권리를 제거하는 카드별 enum을 사용 |
| `enPassantAfterEffect` | enum | 효과 뒤 앙파상 권리 처리. `CLEAR_RELATED_DO_NOT_CREATE`는 관련 기존 권리를 제거하고 새 권리를 만들지 않음 |

`filter`의 값은 가능한 한 기존 조건을 재사용한다.
현재 정의된 값은 다음과 같다.

- `HAS_NEVER_MOVED`: 한 번도 이동하지 않은 기물
- `FORWARD_SQUARE_IS_EMPTY`: 전방 1칸이 비어 있는 기물

`selection`과 `filter`의 역할은 구분한다. `selection`은 몇 개를 대상으로 삼는지 결정하고, `filter`는 대상 후보 중 어떤 대상을 효과 적용 대상으로 인정할지 결정한다.

`direction`의 모든 값은 카드 사용자 진영 기준이다. `FORWARD`는 사용자 진영의 전진 방향이고 `LEFT`, `RIGHT`, `FORWARD_LEFT`, `FORWARD_RIGHT`는 위 방향 표를 따른다.

`promotion`은 카드 효과가 폰의 위치를 변경할 수 있고 프로모션 처리에 대한 별도 규칙이 있을 때만 기록한다.

`movement`는 다음 하위 필드를 필요할 때만 사용한다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `pattern` | enum | 이동 규칙. `STANDARD`는 해당 기물의 표준 체스 이동 규칙을 따른다. |
| `maxDistance` | number | 표준 이동이 가능한 최대 칸 수. 제한이 없으면 생략한다. |
| `destinationMustBe` | enum | 도착 칸 제약. `EMPTY`는 빈 칸으로만 이동할 수 있음을 의미한다. |
| `castlingRightsAfterMove` | enum | 킹 또는 룩 이동 효과 뒤 캐슬링 권리 처리. `REMOVE`는 해당 플레이어의 캐슬링 권리를 제거한다. |

`movement`는 이동 효과일 때만 기록한다. 폰의 고정 방향 이동처럼 이미 `direction`과 `distance`로 충분히 표현되는 효과에는 추가하지 않는다.

위 거리·변환 필드는 해당 효과에서만 사용하는 효과별 세부 필드다. 서버가 계산한 후보 중 사용자가 선택하는 효과는 activation 식별자, card ID/version과 해당 `stateVersion`에 귀속된 actor-private 후보를 제공해야 한다.

카드에 위 공통 필드가 필요하지 않으면 억지로 `null`을 넣지 말고 해당 필드를 생략한다. 새로운 필드가 꼭 필요할 때는 기존 필드와 의미가 겹치지 않는지 확인한 뒤 추가한다.

## 발동과 효과 적용

- `activationConditions`: 인증·차례·phase·카드 보유·마나·`baseStateVersion` 공통 검증 뒤 카드별로 확인하는 최초 조건과 후보 존재 조건
- `effectFailureConditions`: 발동 후 well-formed selection 또는 후보 보드에 효과를 적용할 수 없는 대표 조건

`activationConditions`를 충족하지 못하면 카드는 발동되지 않고 카드, 마나, 행동 슬롯, 손패, 공개 상태, 보드, `GameEvent`와 `stateVersion`을 변경하지 않는다.

발동이 성공하면 카드와 마나 및 해당 카드 행동 슬롯을 소비하고 카드를 패에서 제거한다. 발동한 일반·레전드 카드는 효과 성공 여부와 관계없이 공개되며 레전드는 사용 완료로 처리한다.

`effectFailureConditions`에 해당하면 비용을 환급하거나 재선택하지 않고 `CARD_EFFECT_FAILED`로 종료한다. 효과의 부분 보드·소유권·castling·en-passant·halfmove 변경은 전부 남기지 않고 발동 소비·공개·phase 진행만 유지한다.

모든 카드 사용은 서버가 공통 체스 불변식과 종료 조건을 검증한다. 규칙상 effect failure와 `GameEvent` 저장 실패·서버 예외 같은 기술 실패는 구분하며, 기술 실패로 카드 소비만 단독 확정하지 않는다.

## `resolution` 형식

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `mode` | enum | `SEPARATE_COMMAND`는 발동과 선택 해결이 별도 권위 transition, `SAME_COMMAND`는 한 명령·transition 안의 ordered 단계 |
| `malformedRequest` | enum | `KEEP_PENDING`은 schema 누락·타입 오류를 효과 시도로 인정하지 않고 pending 유지 |
| `outOfCandidateSelection` | enum | `EFFECT_FAILED`는 well-formed 후보 밖 선택을 소비 유지 효과 실패로 확정 |
| `partialEffectOnFailure` | enum | `ROLLBACK`은 실패한 효과의 부분 보드·특수 상태를 남기지 않음 |
| `costOnEffectFailure` | enum | `PRESERVE`는 카드·마나·행동 슬롯 소비와 공개를 유지 |
| `reselectionOnEffectFailure` | enum | `DISALLOWED`는 확정 효과 실패 뒤 재선택·재시도를 허용하지 않음 |

대상 선택 카드의 `mode`는 `SEPARATE_COMMAND`다. `CARD_ACTIVATE` 성공 시 `EFFECT_PENDING`과 actor-private 후보를 확정하고 `CARD_RESOLVE`가 activation 식별자와 닫힌 selection을 제출한다. pending 중 다른 카드 행동과 말 이동은 차단하고 개인 시간은 계속 흐르며 재접속 snapshot으로 복원한다.

무대상 카드의 `mode`는 `SAME_COMMAND`다. 하나의 권위 transition 안에서 `CARD_ACTIVATED` 뒤 `CARD_EFFECT_APPLIED` 또는 `CARD_EFFECT_FAILED`를 ordered event로 기록한다.

카드 효과 자체는 halfmove clock을 추가로 증가시키지 않는다.
폰 이동이나 캡처가 있으면 0으로 초기화하고, 그 외 위치 변경·교환·소유권 변경과 발동 후 효과 실패는 현재 값을 유지한다.
같은 턴의 표준 말 이동은 이후 일반 체스 규칙대로 계산한다.

## version, fixture와 기보

- 경기 생성 시 덱의 card ID/version/definition fingerprint를 고정하며 이후 active version 변경을 적용하지 않는다.
- 기보는 현재 handler로 과거 효과를 재실행하지 않고 저장된 ordered 권위 `GameEvent` outcome을 조회자별 projection으로 재생한다.
- 모든 활성 card ID/version은 handler, activation/resolve schema, public/private outcome과 positive/negative/privacy fixture에 정확히 연결한다.
- fixture는 시작 권위 상태, actor·phase·version, command, ordered event, 종료 상태, 소비·보드·특수 권리·halfmove와 actor/opponent/reconnect/record projection을 포함한다.
- catalog/schema/generator/fixture manifest fingerprint가 바뀌었는데 fixture가 갱신되지 않거나 연결 요소가 누락되면 CI를 실패시킨다.

## 작성 예시

```json
{
  "id": "CARD_001_PAWN_SIDE_STEP",
  "name": "폰 사이드스텝",
  "type": "NORMAL",
  "packId": "BASIC",
  "image": null,
  "timing": ["PRE_MOVE", "POST_MOVE"],
  "manaCost": 2,
  "target": {
    "type": "OWN_PAWN",
    "count": 1
  }
}
```

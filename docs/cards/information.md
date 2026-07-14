# 카드 데이터 형식

이 디렉터리에는 MVP 카드의 마스터 데이터를 카드별 JSON 파일로 저장한다.
카드 JSON은 카드 조회 응답, 카드 사용 계약, 카드 공개/비공개 projection을 정의할 때 참고하는 원천 자료다.

## 파일 규칙

- 카드 파일명은 `{id}.json` 형식을 사용한다.
- `id`는 한 번 정하면 변경하지 않는다.
- 현재 MVP 카드팩 ID는 `BASIC`이다.
- 카드 효과는 서버가 권위적으로 판정하며, JSON의 설명만으로 클라이언트가 결과를 계산하지 않는다.
- 카드별 JSON에는 사용자에게 보여줄 문구와 서버 검증에 필요한 의미 정보를 함께 기록한다.

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
| `additionalConditions` | string 배열 | 대상 조건 외에 충족해야 하는 추가 조건 |
| `effect` | object | 카드 효과의 사용자 설명과 구조화된 의미 정보 |
| `failureConditions` | string 배열 | 카드 사용이 실패하는 대표 조건 |
| `uiText` | object | FE가 표시할 설명과 사용 안내 문구 |
| `visibility` | object | 카드가 상대에게 공개되는 시점 |
| `active` | boolean | 현재 카드팩과 게임에서 사용 가능한 카드인지 여부 |
| `version` | number | 카드 정의 버전. 효과나 조건이 변경되면 증가 |

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
대상 자체의 추가 제약은 `additionalConditions`에 기록한다.

예시는 다음과 같다.

- `OWN_PAWN`: 자신의 폰
- `OWN_PIECE`: 자신의 기물
- `OWN_ROOK`: 자신의 룩
- `OPPONENT_PIECE`: 상대 기물
- `BOARD_SQUARE`: 체스판의 칸
- `NONE`: 별도 대상 선택 없음

`count`는 선택할 대상 수다.
카드 사용 시 클라이언트가 추가 입력을 제출해야 하면 `parameters`에 입력 이름, 타입, 허용값, 필수 여부를 기록한다.

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
| `selection` | enum | 효과 대상의 선택 방식. `SINGLE`은 1개, `MULTIPLE`은 여러 개, `ALL_ELIGIBLE`은 조건을 만족하는 전체 대상, `CLOSEST`는 거리 기준으로 가장 가까운 1개를 의미 |
| `filter` | enum 배열 | `ALL_ELIGIBLE` 대상 중 실제 효과를 적용할 대상을 고르는 조건 |
| `distance` | number | 이동 칸 수. 이동 효과가 아닌 경우에는 생략 |
| `direction` | enum | 이동 방향. 예: `LEFT`, `RIGHT`, `UP_LEFT`, `UP_RIGHT`, `FORWARD` |
| `promotion` | enum | 효과로 폰이 끝 행에 도달했을 때의 프로모션 처리. `DISABLED`는 프로모션을 발생시키지 않음을 의미 |
| `movement` | object | 기물의 일반적인 이동 규칙과 이동 거리, 도착 칸 제약을 함께 표현하는 이동 효과 정보 |
| `distanceMetric` | enum | 거리 계산 방식. `MANHATTAN`은 두 칸의 파일·랭크 차이 절댓값 합을 의미 |
| `conversion` | enum | 효과 대상의 소유권 변경 방식. `OPPONENT_TO_OWN`은 상대 기물을 자신의 기물로 변경하는 방식 |
| `kingTargetBehavior` | enum | 상대 킹이 자동 선택 대상일 때의 처리. `NO_OP_IF_NEAREST`는 효과를 적용하지 않음을 의미 |
| `tiePolicy` | enum | 동일한 최단 거리 대상이 여러 개일 때 선택 방식. `FIXED_BOARD_ORDER`는 서버가 고정한 보드 좌표 순서를 사용함을 의미 |

`filter`의 값은 가능한 한 기존 조건을 재사용한다.
현재 정의된 값은 다음과 같다.

- `HAS_NEVER_MOVED`: 한 번도 이동하지 않은 기물
- `FORWARD_SQUARE_IS_EMPTY`: 전방 1칸이 비어 있는 기물

`selection`과 `filter`의 역할은 구분한다. `selection`은 몇 개를 대상으로 삼는지 결정하고, `filter`는 대상 후보 중 어떤 대상을 효과 적용 대상으로 인정할지 결정한다.

`direction`의 `FORWARD`는 해당 기물의 진영이 정한 전진 방향을 뜻한다. `LEFT`, `RIGHT`, `UP_LEFT`, `UP_RIGHT`처럼 보드 방향을 사용하는 값은 게임에서 정한 보드 좌표 기준을 따른다.

`promotion`은 카드 효과가 폰의 위치를 변경할 수 있고 프로모션 처리에 대한 별도 규칙이 있을 때만 기록한다.

`movement`는 다음 하위 필드를 필요할 때만 사용한다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `pattern` | enum | 이동 규칙. `STANDARD`는 해당 기물의 표준 체스 이동 규칙을 따른다. |
| `maxDistance` | number | 표준 이동이 가능한 최대 칸 수. 제한이 없으면 생략한다. |
| `destinationMustBe` | enum | 도착 칸 제약. `EMPTY`는 빈 칸으로만 이동할 수 있음을 의미한다. |
| `castlingRightsAfterMove` | enum | 킹 또는 룩 이동 효과 뒤 캐슬링 권리 처리. `REMOVE`는 해당 플레이어의 캐슬링 권리를 제거한다. |

`movement`는 이동 효과일 때만 기록한다. 폰의 고정 방향 이동처럼 이미 `direction`과 `distance`로 충분히 표현되는 효과에는 추가하지 않는다.

위 거리·변환 필드는 해당 효과에서만 사용하는 효과별 세부 필드다. `tiePolicy`를 사용하는 카드는 서버와 FE 계약에서 고정된 보드 좌표 순서까지 함께 정의해야 한다.

카드에 위 공통 필드가 필요하지 않으면 억지로 `null`을 넣지 말고 해당 필드를 생략한다. 새로운 필드가 꼭 필요할 때는 기존 필드와 의미가 겹치지 않는지 확인한 뒤 추가한다.

## 조건과 효과 적용 실패

- `additionalConditions`: 효과 적용 전에 확인하는 추가 제약
- `failureConditions`: 추가 조건을 통과했지만 실제 효과를 적용하는 시점에 효과 적용이 불가능한 경우

`failureConditions`가 발생하면 보드와 카드 효과 결과는 변경하지 않는다. 그러나 카드는 사용된 것으로 처리하며 마나는 차감되고 행동도 소비된다.
현재 MVP 카드 정의에서는 `additionalConditions`를 통과한 뒤 `failureConditions`가 발생하는 경우가 없으므로, 해당 카드의 `failureConditions`는 빈 배열로 둘 수 있다.

모든 카드 사용은 마나, 사용 시기, 대상, 추가 조건, 체크 상태, 최종 체스 상태를 서버에서 공통 검증한다.
`additionalConditions`를 충족하지 못한 일반적인 사용 거부는 마나와 행동을 소비하지 않는다.

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

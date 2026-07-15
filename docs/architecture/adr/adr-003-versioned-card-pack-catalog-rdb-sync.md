---
id: "ARCH-ADR-003"
status: "accepted"
decision_scope: "server-architecture"
fixed_reference: "docs/architecture/fixed-20260714/impl-fixed.md"
supersedes: []
source_documents:
  - "docs/spec/spec-fixed.md"
  - "docs/prd.md"
  - "docs/features/card-collection-deck/prd.md"
  - "docs/architecture/interview-20260714/interview-log.md"
---

# ARCH-ADR-003. 버전 카드팩 catalog를 RDB와 동기화하고 배포로 활성화

## Context

카드팩 개봉은 적용 확률 버전을 식별하고 감사할 수 있어야 하며, 관리자 런타임 편집은 MVP 범위가 아니다. 기존 아키텍처는 카드 정의에 대해 저장소 JSON 작성 원천, 검증된 애플리케이션 산출물, RDB 불변 버전 동기화와 배포 기반 활성 전환을 채택했지만 카드팩 정의와 확률 버전의 작성 원천·동기화는 명시적으로 미확정이었다.

제품 문서는 카드팩 지급 결과와 확률 의미를 소유한다. 이번 결정은 그 제품 정책을 다시 정하지 않고, 팩 master 변경을 검토 가능하게 만들고 실행 시점의 활성 정의를 일관되게 조회하기 위한 저장·배포 구조만 선택한다.

## Decision

버전 관리되는 `docs/card-packs`의 팩 JSON과 별도 활성 버전 manifest를 카드팩 정의의 작성·배포 원천으로 사용한다. 검증된 팩 catalog를 애플리케이션 산출물에 포함하고, RDB에는 배포된 모든 팩 식별자·버전을 불변으로 동기화한다. 이미 존재하는 동일 식별자·버전의 내용이 다르면 기동을 실패시키며 누락된 새 버전만 추가한다.

현재 활성 팩 버전은 RDB의 실행·조회 원천으로 두되, 운영 중 RDB를 직접 수정해 전환하지 않는다. 활성 manifest를 변경하고 검증한 새 애플리케이션 배포만 활성 전환 경로로 인정한다. `cardcollection` 모듈이 카드·팩 catalog 동기화와 활성 버전 조회 application port를 소유한다.

팩 schema의 제품 필드, 확률값, REST 표현, 테이블·컬럼과 감사 payload는 이 ADR이 정하지 않는다. 기존 카드 catalog 검증·Testcontainers 경계를 팩 catalog까지 확장하고 새 인프라나 외부 설정 서비스를 추가하지 않는다.

## Alternatives

| 대안 | 장점 | 단점/위험 | 현재 상황에서의 적합성 | 선택 또는 제외 이유 |
| --- | --- | --- | --- | --- |
| 저장소 JSON 원천 + 패키징 + RDB 불변 동기화 | 제품 정의 변경을 코드 리뷰와 함께 추적하고 배포·rollback 경계를 카드 catalog와 통일한다. | 작성 파일과 RDB 표현 사이의 동기화·drift 검증이 필요하다. | 이미 카드 catalog에 같은 구조와 하네스 방향이 확정되어 있다. | 선택. 새 인프라 없이 기존 검증·배포·모듈 경계를 재사용할 수 있다. |
| RDB/Flyway만 원천 | 실행 원천이 하나이며 별도 기동 동기화기가 필요 없다. | 팩 확률 변경이 migration에 결합되고 문서·계약 검토와 분리되며 운영 DB 수정 우회 가능성이 커진다. | 관리자 런타임 편집이 없고 저장소 기반 제품 정의 검토를 사용하는 MVP와 맞지 않는다. | 제외. 카드 catalog와 다른 authoring workflow를 만들 이유가 부족하다. |
| 애플리케이션 설정만 실행 원천 | 초기 구현이 단순하고 RDB master schema가 필요 없다. | 모든 배포 버전 보존, 활성 버전 조회와 감사 연결 책임이 설정 파일에 집중되고 관계형 데이터와 drift가 생긴다. | MySQL이 카드팩 감사와 master 실행 데이터를 보존하는 현재 경계와 맞지 않는다. | 제외. 영속 실행·조회 원천과 버전 불변성 검증을 약화한다. |

## Consequences

- 카드팩 master 변경에는 저장소의 새 불변 버전, 활성 manifest 변경, catalog 검증과 새 배포가 필요하다.
- RDB에는 검증·배포된 과거 팩 버전이 남으며 같은 식별자·버전은 정상 운영에서 수정하지 않는다.
- 작성 원천과 실행 원천이 분리되므로 구조, 참조, fingerprint, 동일 버전 충돌과 활성 manifest를 Hard gate와 기동 검증으로 확인해야 한다.
- 카드와 팩 catalog가 `cardcollection`의 동일한 공개 동기화 경계를 사용하지만 상세 schema와 persistence model은 후속 TRD·issue에서 분리 설계할 수 있다.
- 관리자 런타임 팩 편집, 외부 configuration service, 다중 애플리케이션 버전의 동시 활성화가 필요해지면 이 결정을 재검토한다.

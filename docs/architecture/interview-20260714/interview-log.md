# Architecture Interview Log - 2026-07-14

## 범위

- 카드 정의의 작성 원천과 RDB 동기화
- 카드 버전 불변성, 활성 버전 선택과 경기별 고정
- 카드 정의·효과 처리·계약 완결성 검증
- 과거 경기 재현과 기존 `GameEvent` 아키텍처의 연결

## 기존 결정 재사용

- Java 25, Spring Boot 4.0.6, 기능 우선 모듈러 모놀리스와 헥사고날/클린 원칙을 유지한다.
- MySQL/JPA/Flyway, 단일 인스턴스·단일 writer, `GameEvent` 기반 기보를 유지한다.
- 클라우드, 컴퓨팅, CD, RPO/RTO/SLO와 분산 시스템 결정은 변경하지 않는다.

## 질문 1. 카드 정의 원천과 실행 저장소

- 질문: 카드 추가·변경을 어떤 원천에서 작성하고 실행 RDB에 어떻게 반영할 것인가?
- 선택지:
  1. 버전 관리되는 `docs/cards` JSON을 작성 원천으로 삼고, 검증된 빌드 산출물에 포함해 RDB로 동기화한다.
  2. RDB/Flyway를 유일 원천으로 삼고 `docs/cards`는 설명 문서로만 둔다.
  3. RDB 동기화 없이 패키징된 JSON만 실행 원천으로 사용한다.
- 추천 답변: 1번. 제품 정의·FE/BE 계약·코드 리뷰가 같은 저장소 변경으로 추적되고, RDB 조회·관계·감사 요구도 유지할 수 있다.
- 사용자 답변: 추천안 채택.
- 영향받는 문서: `server-architecture.md`, `infrastructure-architecture.md`, `deployment-view.md`, `fixed-20260714/impl-fixed.md`, `fixed-20260714/infra-fixed.md`
- 상위 산출물 재검토 필요: 없음. spec과 PRD의 카드 식별자·버전 불변성 및 경기별 고정 정책을 구현 구조로 구체화한다.

## 질문 2. 카드 추가·변경과 활성화

- 질문: 카드 JSON을 추가하거나 버전을 올리면 어떤 조건에서 실제 경기에 적용할 것인가?
- 추천 답변:
  - 신규 카드는 새 영구 식별자와 버전 1로 추가한다.
  - 기존 카드 변경은 식별자를 유지하고 새 버전 파일을 추가하며 기존 버전은 수정·삭제하지 않는다.
  - JSON으로 표현할 수 없는 대상 선택·보드 규칙·공개 결과 변경에는 해당 버전의 효과 처리와 계약 검증을 함께 추가한다.
  - 별도 활성 버전 목록은 카드별로 신규 경기에 사용할 버전을 하나만 지정한다.
  - 배포된 모든 버전은 RDB에 보존하고, 활성 버전 변경은 기존 경기와 과거 기보에 영향을 주지 않는다.
- 추천 이유: 데이터 변경이 실행 로직을 자동 생성한다고 오해하지 않게 하고, 배포·롤백·기보 재현을 분리할 수 있다.
- 사용자 답변: 추천안 채택. RDB에는 검증·배포된 모든 버전을 보존하고 추후 TDD에서 활성 버전만 신규 경기에 사용하도록 구현한다.
- 영향받는 문서: `server-architecture.md`, `cicd-architecture.md`, `harness-guardrails.md`, `architecture-traceability.md`, `fixed-20260714/impl-fixed.md`, `fixed-20260714/harness-fixed.md`
- 상위 산출물 재검토 필요: 없음.

## 승인된 결정 요약

- `docs/cards`의 버전별 JSON과 별도 활성 버전 목록을 카드 작성 원천으로 사용한다.
- 빌드 산출물은 검증된 카드 정의와 활성 버전 목록을 포함한다.
- RDB에는 검증·배포된 모든 카드 버전을 불변으로 보존하고 카드별 현재 활성 버전을 별도로 유지한다.
- 이미 존재하는 같은 카드 식별자·버전의 내용이 다르면 동기화와 기동을 실패시킨다. 정상 동기화는 누락된 새 버전만 추가한다.
- 신규 경기는 활성 카드 버전을 조회해 경기 덱에 고정한다. 활성 버전 변경은 이미 생성된 경기에 영향을 주지 않는다.
- 과거 기보는 저장된 권위 결과와 당시 카드 식별자·버전을 사용하며 최신 효과 처리를 재실행하지 않는다.
- 기존 효과 처리로 표현할 수 없는 카드 추가·변경은 해당 버전의 효과 처리, 선택 계약, 공개/비공개 결과와 검증 fixture를 동반한다.
- 카드 정의·활성 목록·효과 처리·계약이 불완전하거나 서로 다르면 배포 가능한 산출물을 만들지 않는다.

## 하네스 분류

- 카드 catalog 구조·중복·활성 버전 참조 검증: 구현되는 즉시 Hard gate
- 카드 식별자/버전과 효과 처리·선택·결과·fixture 완결성 검증: fixed FE/BE 계약과 구현이 생기는 즉시 Hard gate
- RDB 불변 동기화와 경기 버전 고정 통합 테스트: persistence 구현 시 Testcontainers MySQL Conditional gate를 활성화해 Hard required check에 포함

## 변경하지 않는 영역

- 서버 아키텍처 스타일, 패키지 기본 구조, 클라우드/컴퓨팅/네트워크, Redis/메시징, 인증/보안, 관측 도구, CD는 기존 결정을 유지한다.
- 기능 코드와 상세 테이블·컬럼은 이번 아키텍처 결정에서 작성하지 않고 후속 TRD·issue·TDD로 넘긴다.

## 승인

- 사용자 승인: 2026-07-14, 추천안 채택
- 상태: 카드 catalog 결정 architecture review 완료

## 추가 범위: 카드팩 master와 확률 버전

- 상위 제품 결정은 `docs/features/card-collection-deck/prd.md`가 소유한다. 단일 편집 덱, 카드팩 지급 식별자, 확률 버전 감사와 신규 경기의 운영 활성 카드 버전 적용을 아키텍처 문서에서 다시 정의하지 않는다.
- 이번 추가 인터뷰는 카드팩 정의의 작성·배포 원천, RDB 동기화, 활성 버전 전환과 검증 책임만 다룬다.

## 질문 3. 카드팩 정의 원천과 실행 저장소

- 질문: BASIC 카드팩 정의와 확률 버전의 작성·배포 원천을 어떤 방식으로 관리할 것인가?
- 선택지:
  1. 버전 관리되는 `docs/card-packs` JSON과 별도 활성 버전 manifest를 작성 원천으로 삼고 검증된 산출물을 RDB에 동기화한다.
  2. RDB/Flyway만 작성·실행 원천으로 사용한다.
  3. 애플리케이션 설정값만 실행 원천으로 사용한다.
- 추천 답변: 1번. 기존 카드 catalog의 작성 원천·배포 검토·불변 동기화 경계를 재사용하고, 확률 버전과 활성 전환을 저장소 변경으로 추적한다.
- 사용자 답변: 추천안 채택.
- 영향받는 문서: `server-architecture.md`, `infrastructure-architecture.md`, `deployment-view.md`, `cicd-architecture.md`, `harness-guardrails.md`, `fixed-20260714/*`
- 상위 산출물 재검토 필요: 없음. 제품 의미는 먼저 최신화된 card-collection-deck PRD를 따른다.

## 질문 4. 제품 정책과 아키텍처 경계

- 질문: 카드팩 지급 식별자, 과거 개봉 표시와 신규 경기 카드 버전 적용을 아키텍처 결정에 포함할 것인가?
- 추천 답변: 해당 동작은 PRD·FE/BE 계약이 소유하고, 아키텍처는 그 정책을 구현하는 버전 원천·RDB 동기화·활성 전환만 소유한다.
- 사용자 답변: 추천안 채택. 카드팩 감사의 제품 의미는 card-collection-deck PRD가 소유하도록 분리한다.
- 영향받는 문서: `docs/features/card-collection-deck/prd.md`, `docs/architecture/fixed-20260714/impl-fixed.md`, ARCH-ADR-003
- 상위 산출물 재검토 필요: card-collection-deck PRD를 먼저 갱신했고 architecture 입력으로 사용한다.

## 추가 승인된 아키텍처 결정 요약

- 버전 관리되는 `docs/card-packs`의 팩 정의와 별도 활성 버전 manifest를 작성·배포 원천으로 사용한다.
- 검증된 팩 catalog를 애플리케이션 산출물에 포함하고 RDB에 배포된 모든 팩 버전을 불변으로 보존한다.
- RDB는 현재 활성 팩 버전의 실행·조회 원천이다.
- 이미 존재하는 같은 팩 식별자·버전의 내용이 다르면 동기화와 기동을 실패시키고 누락된 새 버전만 추가한다.
- 활성 팩 버전은 RDB 직접 변경이 아니라 manifest를 변경한 새 배포에서만 전환한다.
- `cardcollection` 모듈이 카드·팩 catalog 동기화와 활성 버전 조회 port를 함께 소유한다.
- 기존 카드 catalog validator와 persistence 통합 테스트 경계를 팩 catalog까지 확장하며 새 인프라와 라이브러리는 추가하지 않는다.

## 추가 범위 승인

- 사용자 승인: 2026-07-14, 제품 정책과 아키텍처 경계를 분리한 요약대로 문서 작성 승인
- 상태: architecture review loop 02 진행

## 추가 범위: canonical 계약 번들의 FE 공유와 drift 차단

- 전체 계약 협상의 final coverage에서 `contract-fixture`가 양쪽 저장소의 동일 bundle·source BE commit pin을 요구하지만, 기존 harness 문서는 FE 공유 방식을 미확정으로 남긴 충돌을 확인했다.
- 이번 추가 인터뷰는 REST·STOMP payload를 정하지 않고 계약 번들의 소유 저장소, FE 동기화 방식, CI drift gate와 runtime 의존 경계만 다룬다.

## 질문 5. 계약 번들 소유권과 FE 동기화

- 질문: OpenAPI 3.1, STOMP JSON Schema, fixture와 manifest/fingerprint로 구성한 canonical 계약 번들을 어느 저장소가 소유하고 FE가 어떻게 동일 버전을 사용할 것인가?
- 선택지:
  1. BE 저장소가 canonical bundle을 소유하고 FE는 적용할 BE git commit을 명시적으로 pin한 뒤 해당 bundle을 checked-in copy로 동기화한다. 양쪽 CI가 manifest·fingerprint와 생성 산출물을 재계산한다.
  2. package/artifact registry에 번들을 게시하고 양쪽 저장소가 버전 dependency로 받는다.
  3. FE와 BE가 각 저장소에 계약 파일을 독립 작성하고 수동으로 비교한다.
- 추천 답변: 1번. 현재 MVP에 새 registry·배포 인프라와 runtime 네트워크 의존을 추가하지 않으면서, 계약 변경과 FE 채택 시점을 각각 커밋으로 검토하고 drift를 기계적으로 차단할 수 있다.
- 사용자 답변: 추천안 확정.
- 영향받는 문서: `harness-guardrails.md`, `cicd-architecture.md`, `architecture-traceability.md`, `fixed-20260714/harness-fixed.md`, ARCH-ADR-004
- 상위 산출물 재검토 필요: 없음. 협상에서 확정한 동일 bundle 요구를 구현·CI 구조로 구체화한다.

## 추가 승인된 아키텍처 결정 요약

- BE 저장소가 canonical 계약 번들의 유일한 작성 원천을 소유한다.
- FE는 적용할 BE git commit을 명시적으로 pin하고 그 commit의 bundle을 checked-in copy로 동기화한다.
- BE CI는 source에서 manifest·fingerprint와 generated output을 재계산하고 drift 또는 생성 누락을 실패시킨다.
- FE CI는 pin된 commit, checked-in bundle, 생성 TypeScript·validator·fixture 결과의 일치를 검증한다.
- 계약 변경은 BE bundle commit과 FE pin 갱신의 두 리뷰 가능한 단계로 전달하며, FE가 pin을 갱신하기 전에는 기존 계약을 계속 사용한다.
- build와 CI는 pin된 checkout 또는 checked-in copy만 사용하고 runtime 원격 의존과 MVP artifact registry를 두지 않는다.

## 계약 번들 범위 승인

- 사용자 승인: 2026-07-14, 추천안 채택
- 상태: architecture review loop 03 완료, 차단 없음

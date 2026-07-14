# Implementation Architecture Fixed

## 확정된 결정

- `fixed-20260710/impl-fixed.md`의 Java 25, Spring Boot 4.0.6, 단일 Gradle 모듈, 기능 우선 모듈러 모놀리스와 헥사고날/클린 원칙을 유지한다.
- MySQL/JPA/Flyway, application service 트랜잭션 경계, `GameEvent` 기보 원천과 메모리 활성 경기 결정을 유지한다.
- 버전 관리되는 `docs/cards` JSON과 별도 활성 버전 목록을 카드 정의의 작성·배포 원천으로 사용한다.
- RDB는 검증·배포된 모든 카드 식별자·버전과 카드별 현재 활성 버전의 실행·조회 원천이다.
- 같은 카드 식별자·버전은 불변이다. RDB에 같은 버전의 다른 내용이 있으면 기동을 실패시키고 누락된 새 버전만 추가한다.
- 활성 버전은 RDB 직접 수정이 아니라 활성 버전 목록을 변경한 새 배포에서만 전환한다.
- `cardcollection` 모듈이 catalog 동기화와 활성 버전 조회의 공개 application port를 소유한다. `gameplay`는 이 port로 신규 경기의 카드 버전을 고정하며 `cardcollection` 저장소를 직접 참조하지 않는다.
- 활성화·롤백 가능한 모든 카드 버전은 효과 처리, 선택 계약, 공개/비공개 결과와 fixture를 함께 유지한다.
- 기존 효과 처리로 표현할 수 없는 변경은 같은 식별자의 새 버전과 새 효과 처리를 추가한다. JSON만으로 실행 로직이 자동 생성된 것으로 간주하지 않는다.
- 과거 기보는 저장된 권위 `GameEvent` 결과와 당시 카드 식별자·버전을 사용하며 최신 효과 처리를 재실행하지 않는다.

## 문서화 가정

- 카드 catalog는 빌드 산출물에 포함되고 애플리케이션 기동 시 검증·동기화된다.
- 활성 버전 목록은 카드별 신규 경기에 사용할 버전을 하나만 가리킨다.
- 상세 resource 경로, 테이블·컬럼, 동기화 use case와 효과 처리 registry 구조는 후속 TRD·issue에서 구체화한다.

## 미확정 또는 상위 산출물 재검토

- 카드팩 정의와 확률 버전의 작성 원천·RDB 동기화 범위
- 카드 통계의 사용자 노출 범위, 집계 기간과 버전별 해석

## 후속 스킬 연계

- `negotiate-fe-be-contract`: 카드 선택·공개 결과와 fixture 계약 fixed
- `create-trd`: catalog resource, 동기화 경계, persistence와 effect registry 상세 설계
- `create-issues-adr`: Flyway·동기화·활성 버전·검증 gate 구현 이슈 분리
- `tdd-workflow`: 불변 버전 추가, 활성 버전 경기 고정, 롤백과 기보 재현을 이슈 단위로 구현

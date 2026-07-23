# Architecture Review Loop 01

## 리뷰 입력

- 기준 인터뷰: `interview-20260714/interview-log.md`
- 기준 문서: spec, 허브·gameplay·card-collection-deck·match-history PRD, 기존 `fixed-20260710`, 변경된 architecture 문서와 ARCH-ADR-002 초안
- 기준 repo 설정: `build.gradle`, `src/main`, `src/test`, `.github/workflows/backend-ci.yml`

## 리뷰 결과

- 검토 범위: 데이터·카드 저장, `cardcollection`/`gameplay` 모듈 경계, 배포·기동 검증, 하네스 gate, 과거 기보 연결
- 생략 범위와 사유: 서버 스타일·기본 패키지, 클라우드·컴퓨팅·네트워크, Redis/메시징, 인증·secret, 관측, CD는 관련 입력과 설정이 변하지 않아 기존 결정을 유지했다.
- 핵심 이슈:
  - 기존 문서의 “MySQL 영속 원천”과 새 결정의 “`docs/cards` 원천”이 역할을 구분하지 않으면 충돌로 읽힐 수 있다.
  - 활성 버전이 RDB 직접 수정으로 바뀔 수 있으면 Git 변경·검증·배포 추적을 우회한다.
  - 이전 버전 롤백을 보장하려면 JSON뿐 아니라 실행 가능한 효과 처리와 계약도 함께 유지해야 한다.
- 재결정 필요 항목: 원천 역할 구분, 활성 전환 경로, 롤백 대상 효과 처리 보존

## 재인터뷰 결정

- 질문: 위 세 경계를 추천안대로 명확히 해 아키텍처를 확정할 것인가?
- 추천 답변:
  - `docs/cards`는 작성·배포 원천, RDB는 검증·배포된 버전의 실행·조회 원천으로 구분한다.
  - 활성 버전 전환은 버전 관리되는 활성 목록을 변경한 새 배포에서만 허용한다.
  - 활성화·롤백 가능한 모든 버전의 효과 처리·계약·fixture를 유지한다.
- 사용자 답변: 확정
- 승인 여부: 승인
- 반영 문서/설정: server/infrastructure/cicd/harness 문서, ARCH-ADR-002, fixed-20260714. 기능 코드와 repo 설정은 후속 TDD로 이관한다.

## 재리뷰 결과

- 해소됨: 작성 원천과 실행 원천 충돌, RDB 직접 활성화 우회, 이전 버전 롤백 실행 가능성
- 남은 이슈: 없음
- 다음 조치: fixed 문서·ADR·현재 포인터 확정, 아키텍처 산출물 최신성 기록

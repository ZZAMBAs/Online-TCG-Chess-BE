# Architecture Review Loop 02

## 리뷰 입력

- 기준 인터뷰: `interview-20260714/interview-log.md`
- 기준 문서: 최신 card-collection-deck PRD, ARCH-ADR-003, `fixed-20260714/*`, server/infrastructure/deployment/CI/harness/traceability 문서
- 기준 repo 설정: `build.gradle`, `.github/workflows/backend-ci.yml`, 현재 구현·테스트 skeleton

## 리뷰 결과

- 검토 범위: 카드팩 master 작성·실행 원천, RDB 불변 동기화, 활성 전환, `cardcollection` 모듈 경계, 배포 artifact와 검증 gate
- 생략 범위와 사유: 서버 스타일, 패키지 기본 구조, 클라우드/컴퓨팅/네트워크, 인증·secret, 관측, Redis/메시징, CD는 관련 입력과 repo 설정 변화가 없어 생략
- 핵심 이슈: 초기 반영 요약에 신규 경기 카드 버전과 과거 개봉 표시 같은 제품 정책이 섞여 architecture ownership을 넘었다.
- 재결정 필요 항목: 제품 동작은 PRD·계약으로 돌리고 architecture에는 팩 catalog 저장·동기화 구조만 남길 것

## 재인터뷰 결정

- 질문: 카드팩 지급·감사·게임 적용 정책과 팩 master 저장·동기화 구조의 문서 소유권을 어떻게 나눌 것인가?
- 추천 답변: 전자는 card-collection-deck PRD와 FE/BE 계약, 후자는 architecture fixed와 ADR이 소유한다.
- 사용자 답변: 추천안 채택. 카드팩 감사의 제품 의미는 card-collection-deck PRD가 소유하도록 분리한다.
- 승인 여부: 승인
- 반영 문서/설정: card-collection-deck PRD·traceability를 먼저 최신화하고 architecture 문서에는 `docs/card-packs`·RDB·배포 활성화·검증 경계만 반영. repo 설정 변경 없음

## 재리뷰 결과

- 해소됨: 제품 정책과 architecture 책임 혼합, 카드팩 master 미확정, 카드 catalog와 팩 catalog의 배포·검증 경계 불일치
- 남은 이슈: 상세 팩 schema, endpoint/payload, 테이블·컬럼, 동기화 use case는 후속 계약·TRD·issue 소유
- 다음 조치: architecture artifact freshness와 테스트를 검증한 뒤 `card-collection-deck-rest` 협상을 재개

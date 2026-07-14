# PRD Traceability

## 목적

이 문서는 [`docs/spec/spec-fixed.md`](spec/spec-fixed.md)의 큰 번호 섹션과 PRD 산출물의 연결을 추적한다. 원천 명세의 기술 계약·서버 내부 책임·운영 구현 항목은 PRD에서 제품 요구사항 경계만 유지하고 후속 기술 문서로 넘긴다.

## 원천 섹션 매핑

| 원천 섹션 | 분류 | PRD 산출물 | 비고 |
| --- | --- | --- | --- |
| 1. 개요 | 허브 | [`docs/prd.md`](prd.md) | 전체 제품 목적과 서버 권위 원칙 |
| 2. 문서 목적과 범위 | 허브 | [`docs/prd.md`](prd.md) | MVP 범위·제외 범위 |
| 3. 용어 정의 | 공통 | [`docs/prd.md`](prd.md), 기능별 PRD | 용어를 기능 문맥에 재사용 |
| 4. 사용자 역할과 권한 | 공통 | [`docs/prd.md`](prd.md), `identity-account`, `matchmaking`, `community`, `trust-safety-admin` | 계정 상태·역할·제재의 공통 기준 |
| 5. 주요 사용자 시나리오 | 기능 분해 | 기능별 PRD 전체 | 첫 플레이, 매칭, 게임, 카드, 커뮤니티 흐름 재배치 |
| 6. MVP 범위 | 허브·기능 | [`docs/prd.md`](prd.md), 기능별 PRD 전체 | 포함·제외 범위 |
| 7. 인증 및 계정 | 기능 | [`identity-account`](features/identity-account/prd.md) | 가입·로그인·세션·탈퇴·설정 |
| 8. 실시간 통신 | 공통 제품 경계 | `gameplay`, `match-chat` | 최신 상태 복구·공개 범위·중복 결과 등 사용자 경험 반영 |
| 9. 사용자 상호작용 요구사항 | 공통 제품 경계 | [`docs/prd.md`](prd.md), `gameplay`, `match-chat` | 권한·오류 안내·복구 등 관찰 가능한 요구사항 반영 |
| 10. 매치메이킹 | 기능 | [`matchmaking`](features/matchmaking/prd.md) | 대기열·MMR·경기 생성 |
| 11. 체스 룰 | 기능 | [`gameplay`](features/gameplay/prd.md) | 체스·승패·무승부 |
| 12. 턴 진행 | 기능 | [`gameplay`](features/gameplay/prd.md) | 턴 단계·카드 행동 |
| 13. 시간 규칙 | 기능 | [`gameplay`](features/gameplay/prd.md) | 타이머·재접속·시간패·몰수패 |
| 14. 카드 시스템 | 기능 분해 | `gameplay`, `card-collection-deck`, `match-history` | 발동·효과 적용, 카드 식별자·버전, 당시 결과 기반 기보를 분리 반영 |
| 15. 마나 시스템 | 기능 | [`gameplay`](features/gameplay/prd.md) | 획득·소비·상한 |
| 16. 카드팩 및 컬렉션 | 기능 | [`card-collection-deck`](features/card-collection-deck/prd.md) | 카드팩·컬렉션·스타터 지급, 단일 편집 덱과 개봉 결과·확률 버전 감사 |
| 17. 전적 및 기보 | 기능 | [`match-history`](features/match-history/prd.md) | 결과·전적·기보·종료 경기 통계와 당시 카드 결과 재현 기준 |
| 18. 대전 채팅 | 기능 | [`match-chat`](features/match-chat/prd.md) | 채팅·마스킹·차단 전달 |
| 19. 커뮤니티 | 기능 | [`community`](features/community/prd.md) | 게시글 중심 커뮤니티 |
| 20. 신고, 차단, 관리자 | 기능 | [`trust-safety-admin`](features/trust-safety-admin/prd.md) | 보호·신고·관리자·제재 |
| 21. 마이페이지 및 설정 | 기능 분해 | [`identity-account`](features/identity-account/prd.md), [`match-history`](features/match-history/prd.md), [`card-collection-deck`](features/card-collection-deck/prd.md) | 사용자 자신의 집계·설정 허브 |
| 22. 운영 및 보호 장치 | 공통 기술 경계 | 허브·`gameplay`·`match-history`·`card-collection-deck` | 운영 메트릭과 card analytics의 제품 기준; 구현은 기술 문서 |
| 23. 기록과 보존 원칙 | 공통 제품 경계 | 허브·`gameplay`·`match-history`·`card-collection-deck`·`trust-safety-admin` | 보존·공개 범위와 통계 기록 기준만 반영 |
| 24. 예외 및 엣지 케이스 | 기능 재배치 | 기능별 PRD 전체 | 관련 상태 경계에 재배치 |
| 25. 핵심 수용 기준 | 기능 재배치 | 허브·기능별 PRD 전체 | 기능별 검증 가능한 기준으로 재배치 |
| 26. MVP 확정 정책과 후속 결정 경계 | 허브·후속 결정 추적 | [`docs/prd.md`](prd.md), 관련 기능 PRD | 카드 제품 정책과 후속 아키텍처·계약 결정 분리 |
| 27. MVP 제외 및 이후 확장 후보 | 허브·기능 | [`docs/prd.md`](prd.md), 관련 기능 PRD | MVP 범위 밖 항목과 확장 메모 |

## 기능별 산출물

| Feature | 제품 책임 | 관련 원천 섹션 |
| --- | --- | --- |
| `identity-account` | 계정 수명주기·인증·사용자 설정 | 3, 4, 5.1, 6, 7, 21, 24.1, 25.1~25.2 |
| `matchmaking` | 빠른 매치·대기열·MMR·경기 생성 | 4, 5.2, 6, 10, 24.2, 25.3, 26 |
| `gameplay` | 체스·카드 행동·마나·시간·실시간 경기 | 5.3, 8~9, 11~15, 23, 24.3~24.4, 25.4~25.6 |
| `card-collection-deck` | 카드팩·컬렉션·스타터·단일 편집 덱·개봉 감사 | 5.4, 6, 14, 16, 23.3, 23.5, 24.2~24.3, 25.3, 25.7, 26, 27.4 |
| `match-history` | 경기 결과·전적·MMR·기보 | 5.1, 17, 23, 24.4, 25.8, 26 |
| `match-chat` | 경기 채팅·마스킹·전달 제한·증거 | 8~9, 18, 20.1~20.2, 22.1, 24, 25.2·25.9 |
| `community` | 게시글·검색·상태·사용자 노출 | 5.5, 6, 19, 20.2, 24.5, 25.2·25.9 |
| `trust-safety-admin` | 차단·신고·숨김·제재·금칙어·감사 | 4, 18.5, 19.3·19.6~19.7, 20, 22.4, 24, 25.2·25.9~25.10 |

## 현재 확정된 주요 보완

- 이메일 인증 토큰과 비밀번호 재설정 토큰은 모두 5분 만료다.
- 신규 사용자 최초 MMR은 1400이며, 표준 Elo와 `K=32`를 사용한다.
- 매칭 범위는 0~10초 `±50`에서 시작해 10초마다 두 배로 확대한다.
- 동일 일반 카드는 덱에 최대 2장까지 포함한다.
- MVP 카드 12장의 발동 조건·효과·효과 실패 조건은 `docs/cards`에 확정되어 있다.
- 카드는 발동과 효과 적용을 구분하며, 발동 후 효과 실패에도 카드·마나·행동 기회 소비와 공개가 유지된다.
- 폰 일제 전진은 이동 가능한 폰만 전진시키고, 왕의 포섭은 사용자가 최단거리 후보 중 하나를 선택한다.
- 카드 방향은 사용자의 전진 방향을 기준으로 하며 경기 화면은 자신의 기물이 아래쪽에 보이도록 표시한다.
- 카드 식별자는 영구적이고 같은 버전의 의미는 배포 후 바꾸지 않으며, 과거 기보는 당시 확정 결과를 따른다.
- 컬렉션과 단일 편집 덱은 안정적인 카드 식별자를 사용하고, 신규 경기는 생성 시점의 운영 활성 버전을 적용하며 진행 중 경기는 고정 버전을 유지한다.
- 카드팩 감사 기록은 적용 확률 버전과 실제 지급 카드 식별자·슬롯 순서를 추적하며, 여러 저장 덱 관리는 추후 확장 사항이다.
- 최근 경기는 최대 10개씩 무한 스크롤하고, 승률은 소수점 첫째자리까지 반올림한다.
- 대국 중 상대방을 선택해 차단할 수 있다.
- 무효 경기는 무효 전까지의 기보를 보존하고 결과 표시에 무효임을 표시한다.

## 미확정 항목의 소유권

- 제품 정책 미확정: 각 기능 PRD의 `미확정 사항`
- 기술 계약 미확정: 후속 TRD·계약 문서
- 서버 구조·인프라·CI/CD·AI 하네스 미확정: 아키텍처 산출물
- 구현 순서·이슈·ADR 미확정: 후속 issue/ADR 산출물

현재 승인된 PRD는 위 소유권을 넘어서 통신 형식, 저장 구조와 서버 내부 설계를 임의 확정하지 않는다.

# Infrastructure Architecture Fixed

## 확정된 결정

- `fixed-20260710/infra-fixed.md`의 단일 백엔드 인스턴스·단일 writer, MySQL 호환 RDB, Redis/queue 미도입, 실행 JAR 배포 단위를 유지한다.
- 검증된 카드 JSON과 활성 버전 목록은 애플리케이션 산출물에 포함하며 별도 object storage를 요구하지 않는다.
- MySQL에는 검증·배포된 모든 카드 버전과 카드별 현재 활성 버전을 보존한다.
- 카드 버전 동기화는 기존 동일 버전 갱신을 금지하고 새 버전 추가와 검증된 활성 버전 선택만 허용한다.
- 활성 버전 전환은 버전 관리되는 활성 목록을 포함한 새 애플리케이션 배포로만 수행한다.
- 과거 경기 결과는 기존 MySQL `GameEvent` 보존과 backup/PITR 경계를 사용하며 현재 카드 효과 재실행에 의존하지 않는다.

## 문서화 가정

- 카드 동기화와 활성 버전 반영은 모든 catalog 검증을 통과한 뒤 하나의 일관된 경계에서 수행한다.
- RDB 직접 편집은 카드 작성·활성화 절차가 아니다.

## 미확정 또는 상위 산출물 재검토

- cloud provider, compute, managed DB, registry, Secret Manager, 관측 platform
- CD, migration 배포, smoke test, application artifact rollback 자동화
- RPO/RTO, backup 보존 기간, SLO, 비용 상한과 트래픽 목표

## 후속 스킬 연계

- provider/CD 확정 시 `$architecture-decision` 재실행
- 카드 catalog와 RDB 동기화 상세는 `create-trd`와 구현 이슈로 이관

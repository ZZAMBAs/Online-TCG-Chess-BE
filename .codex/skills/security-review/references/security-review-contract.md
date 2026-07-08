# Security Review Contract

`security-review`는 현재 이슈 디렉터리의 `security-review.md`에 보안 검토 결과를 기록한다. 모든 설명은 한국어로 쓴다.

## 상태

- `security-pass`: `Medium`/`High` finding이 없거나 모두 수정되었고 재검증이 통과했다.
- `security-low-only`: `Low` finding만 남아 있으며 completion을 차단하지 않는다.
- `security-blocked`: GREEN/BLUE 결과 부재, 대상 파일 불명확, 보안 요구사항 미확정, 테스트/도구 환경 문제 등으로 검토 또는 재검증을 끝낼 수 없다.
- `security-failed`: `Medium`/`High` finding이 남아 있거나 허용 범위 안에서 수정하지 못했다.

## 기록 규칙

- 실행 이력을 누적하지 말고 최신 스냅샷으로 덮어쓴다.
- 서브에이전트 finding은 근거가 확인된 항목만 남긴다.
- `Medium`/`High` finding은 차단 여부와 수정 여부를 반드시 남긴다.
- 새 보안 도구가 필요하지만 도입하지 않은 경우 후보 도구, 이유, 승인 필요 여부를 남긴다.

## 필드

- 대상 이슈
- 상태
- 검토 대상 파일
- 사용한 원천 문서
- 실행한 테스트 명령
- 실행한 보안/정적 분석 명령
- 서브에이전트 검토 수행 여부
- findings 요약
- `Low` findings
- `Medium` findings
- `High` findings
- 수정한 파일
- 재검증 결과
- 차단 또는 실패 요약
- 새 보안 도구 도입 후보

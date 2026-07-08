# Tooling Policy

보안 도구 사용은 검토 신뢰도를 높이기 위한 수단이다. 새 도구 도입은 허용되지만 기본 실행 중 무단으로 build/CI 설정을 바꾸지 않는다.

## 기본 순서

1. 대상 테스트와 가능한 전체 테스트를 실행한다.
2. 이미 프로젝트에 설정된 보안/정적 분석/품질 도구가 있으면 실행한다.
3. 현재 변경 범위와 명세를 기준으로 수동 보안 리뷰를 수행한다.
4. 새 도구가 필요하면 후보와 이유를 기록하고 사용자 승인 후 별도 변경으로 도입한다.

## 후보 도구

- OWASP Dependency-Check: 의존성 CVE 확인이 필요할 때
- Semgrep: Spring MVC, Security, SQL, logging, secret leak 패턴 점검이 필요할 때
- SpotBugs 또는 FindSecBugs: Java bytecode 기반 취약 패턴 확인이 필요할 때
- Gradle dependency verification 또는 locking: 공급망 무결성 정책을 확정해야 할 때

## 도입 기준

- 현재 이슈의 보안 위험을 기존 테스트와 수동 리뷰만으로 판단하기 어렵다.
- 반복적으로 같은 종류의 결함이 생길 가능성이 있다.
- 도구가 프로젝트의 Java/Spring/Gradle 버전과 호환된다.
- 실행 비용과 false positive를 감당할 수 있다.
- 사용자 승인이 있거나 별도 선행 이슈로 분리되어 있다.

## 기록 규칙

- 실행한 명령과 결과를 `security-review.md`에 남긴다.
- 실행하지 못한 명령은 원인과 영향 범위를 남긴다.
- 새 도구 후보는 도구명, 목적, 예상 파일 변경, 차단 여부를 남긴다.

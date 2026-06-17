# AI 구현 방어 장치 검토 초안

현재 저장소 기준 기술 스택은 `Java 25 + Spring Boot 4 + Gradle 9.5.1` 백엔드다. 아직 코드가 거의 없는 초기 상태이므로, 지금부터 AI가 잘못 구현하면 빌드, 커밋, PR 단계에서 실패하도록 품질 게이트를 먼저 고정하는 것이 효과적이다.

## 핵심 결론

가장 효과적인 조합은 다음 계층 구조다.

1. `./gradlew check` 하나로 모든 품질 게이트를 묶는다.
2. GitHub Actions에서 `check`를 필수 통과 조건으로 만든다.
3. ArchUnit으로 레이어, 도메인 경계, 의존성 방향을 강제한다.
4. Error Prone, SpotBugs, PMD, Spotless로 정적 품질을 강제한다.
5. Dependency Review, Dependabot, OWASP Dependency-Check, Gradle dependency verification으로 공급망을 방어한다.
6. pre-commit 또는 Husky로 로컬 커밋 전에 빠른 실패를 유도한다.
7. Testcontainers, Spring Security Test, mutation/property 테스트로 겉보기 통과를 방지한다.
8. 프론트엔드는 TypeScript strict, type-aware ESLint, OpenAPI/JSON Schema 기반 계약 생성, Playwright E2E를 필수 게이트로 둔다.
9. REST/STOMP 호출은 손으로 문자열을 조립하지 않고 생성 코드와 런타임 검증기를 통과하게 한다.

## 차단 강도와 검증도 재분류

아래 목록의 도구들은 모두 같은 의미의 "방어 장치"가 아니다. 하드 게이트로 만들 수 있는 도구, 규칙을 붙여야 차단되는 도구, 직접 차단보다는 관측과 분석을 돕는 도구로 나눠야 한다.

| 분류 | 의미 | 대표 도구 | AI 오작동 차단력 |
| --- | --- | --- | --- |
| Hard gate | 설정하면 빌드, 테스트, 커밋, PR을 실패시킬 수 있다. | Gradle `check`, ArchUnit, Spotless, PMD, SpotBugs, JaCoCo verification, `tsc --noEmit`, ESLint, dependency-cruiser, Vitest, Playwright, Gitleaks, CodeQL, Dependency Review, branch protection | 높음. 실제 차단 장치로 볼 수 있다. |
| Conditional gate | 도구 자체보다 규칙, schema, threshold, wrapper를 만들어야 실패 조건이 된다. | OpenAPI generated client, JSON Schema, Zod/Valibot, MSW, STOMP fake server, Lighthouse CI, size-limit, Storybook test-runner, axe-core | 중간-높음. 게이트화하면 강력하지만 설계가 필요하다. |
| Pattern enabler | 올바른 구현 패턴을 쉽게 만들지만, 단독으로 잘못된 구현을 막지는 않는다. | TanStack Query, React Hook Form, XState, Spring Modulith 일부 기능, Testcontainers, Instancio | 중간. 테스트나 아키텍처 규칙과 결합해야 한다. |
| Advisory / observability | 문제를 발견하거나 운영 중 추적한다. PR 차단 수단은 아니다. | Sentry, OpenTelemetry Web, Web Vitals, Storybook 문서화, OpenSSF Scorecard 일부 항목 | 낮음-중간. 품질 운영에는 유용하지만 방어벽으로 과대평가하면 안 된다. |
| 도입 주의 | 쓸 수는 있지만 현재 프로젝트 조건에서 호환성, 라이선스, 운영비용 검토가 필요하다. | Error Prone, NullAway, Checkstyle, jqwik, Pact, full visual regression | 조건부. 바로 필수 게이트로 넣기 전에 작은 PoC가 필요하다. |

따라서 "확실히 막는다"라고 말할 수 있는 것은 Hard gate로 CI와 branch protection에 연결한 항목들이다. 나머지는 반드시 테스트, 규칙, generated code diff, schema validation, threshold와 결합해야 한다.

### 실제 차단으로 인정할 기준

도구를 도입했다고 해서 방어 장치가 되는 것은 아니다. 다음 조건 중 하나 이상을 만족해야 실제 차단 수단으로 본다.

- 로컬 명령이 non-zero exit code로 실패한다.
- CI required check로 등록되어 실패 시 merge가 불가능하다.
- branch protection이 required check, PR review, force-push 제한을 강제한다.
- Git hook은 pre-commit/pre-push에서 실패할 수 있지만 우회 가능하므로 보조 수단으로만 본다.
- generated artifact drift를 검사해 손수 수정하거나 계약과 다르면 실패한다.
- 테스트 fixture가 정상 경로뿐 아니라 실패, 권한 없음, 중복, 역순, 지연, 재접속을 검증한다.

### 검증된 도구로 볼 수 있는 항목

다음은 생태계에서 널리 쓰이고 공식 문서상 CI/테스트/검증 용도로 명확히 제공되는 도구들이다.

| 도구 | 검증도 | 근거와 판단 |
| --- | --- | --- |
| ArchUnit | 높음 | Java 아키텍처 규칙을 JUnit 테스트로 실행할 수 있다. 레이어와 패키지 의존성 차단에 적합하다. |
| Gradle dependency locking / verification | 높음 | Gradle 공식 기능이다. resolved dependency 고정과 artifact 검증에 적합하다. |
| GitHub branch protection / required checks | 높음 | 원격 저장소 레벨 강제 장치다. 로컬 우회를 막는 최종 방어선이다. |
| typescript-eslint type-aware rules | 높음 | TypeScript 타입 정보를 사용하는 ESLint 규칙을 공식적으로 제공한다. Promise, unsafe any, exhaustiveness 계열 실수 차단에 적합하다. |
| Playwright | 높음 | cross-browser E2E, auto-wait assertion, screenshot/trace artifact를 제공한다. FE 최종 회귀 게이트로 적합하다. |
| Vitest | 높음 | TypeScript, JSX, coverage를 지원하는 Vite 기반 테스트 러너다. FE 단위/컴포넌트 테스트에 적합하다. |
| MSW | 높음 | browser와 Node에서 네트워크 레벨 API mocking을 제공한다. REST mock의 단일 원천으로 쓰기 좋다. |
| dependency-cruiser | 높음 | JS/TS import graph를 rule로 검증하고, 위반 시 exit code로 실패시킬 수 있다. FE 아키텍처 경계 강제에 적합하다. |
| Spotless, PMD, SpotBugs, JaCoCo | 높음 | Java/Gradle 생태계에서 오래 쓰인 정적 분석/포맷/커버리지 도구다. Gradle `check`에 묶기 쉽다. |
| Gitleaks, CodeQL, Dependency Review, Dependabot | 높음 | secret, code scanning, dependency diff, dependency update 자동화에 쓰이는 표준적인 GitHub 보안 장치다. |

### 검증은 되었지만 과대평가하면 안 되는 항목

| 도구 | 주의점 |
| --- | --- |
| TanStack Query | 서버 상태 관리 라이브러리이지 보안/계약 검증 도구는 아니다. wrapper와 테스트 없이 쓰면 잘못된 mutation이나 stale state를 막지 못한다. |
| Storybook | 컴포넌트 fixture와 리뷰에는 좋지만, test-runner/a11y/visual regression을 CI에 연결하지 않으면 차단 장치가 아니다. |
| Sentry / OpenTelemetry / Web Vitals | 운영 중 발견과 추적 도구다. PR 단계에서 AI 구현을 막지는 않는다. |
| Testcontainers | 실제 의존성 기반 테스트를 가능하게 하지만, 테스트를 작성해야 막는다. 도구만 추가하면 아무 것도 차단하지 않는다. |
| OpenAPI / JSON Schema | spec과 generated code drift, runtime validation, fixture test를 붙여야 차단된다. 문서만 있으면 차단 효과가 없다. |
| Lighthouse CI / bundle budget | threshold를 설정해야 차단된다. 환경 변동이 있으므로 모든 PR 필수 체크로 시작하면 flaky할 수 있다. |

### 도입 전 PoC가 필요한 항목

| 도구 | 이유 |
| --- | --- |
| Error Prone | 강력하지만 Java 25, Gradle 9.5.1, Lombok 조합에서 호환성 확인이 필요하다. |
| NullAway | NPE 방지에는 좋지만 Lombok과 함께 쓸 때 generated annotation 등 설정 검증이 필요하다. |
| Checkstyle | 스타일 강제에는 좋지만 최신 Java 문법 지원 범위를 확인하고 보수적으로 적용해야 한다. |
| jqwik | property-based testing 자체는 유효하지만 라이선스 문구를 먼저 검토해야 한다. |
| Pact | FE/BE가 같은 릴리스 단위인 MVP에서는 OpenAPI/JSON Schema/fixture가 먼저다. 분리 릴리스가 되면 검토한다. |

## 최우선 도입 대상

| 장치 | 막는 실수 | 판단 |
| --- | --- | --- |
| ArchUnit | Controller가 Repository 직접 접근, domain이 Spring/JPA에 오염, WebSocket 핸들러가 권한 검증 우회, 패키지 순환 | 필수. Java bytecode를 분석해 패키지, 레이어, 순환 규칙을 테스트로 검증할 수 있다. |
| GitHub branch protection / required checks | AI가 로컬 훅을 우회하고 바로 push/merge | 필수. status check, PR review, force push 차단을 원격 저장소에서 강제한다. |
| pre-commit 또는 Husky | 포맷, secret, 간단한 테스트 누락 | Java-only 저장소면 `pre-commit`이 더 자연스럽고, Node 도입을 받아들일 수 있으면 Husky도 가능하다. |
| Gradle dependency locking + verification | 의존성 버전이 몰래 바뀜, 동일 좌표의 artifact 변조 | 필수. lockfile로 resolved version을 고정하고 verification metadata로 checksum/signature를 검증한다. |
| Dependency Review Action + Dependabot | 취약하거나 라이선스가 맞지 않는 의존성 PR 유입 | GitHub 사용 시 강력 추천. PR dependency diff를 검사하고 보안/버전 업데이트 PR을 자동 생성한다. |

## 정적 분석

| 도구 | 추천도 | 검토 |
| --- | --- | --- |
| Error Prone | 높음 | javac에 붙어 일반 컴파일러가 못 잡는 Java 버그 패턴을 빌드 중 차단한다. Java 25, Gradle, Lombok 조합 호환성은 별도 확인이 필요하다. |
| NullAway | 중간-높음 | NPE 방지에 좋지만 이 저장소는 Lombok을 이미 쓰고 있어 주의가 필요하다. 도입한다면 `lombok.addLombokGeneratedAnnotation = true`부터 설정한다. |
| SpotBugs + FindSecBugs | 높음 | bytecode 기반 bug pattern 탐지. 보안 규칙은 FindSecBugs 확장을 고려한다. |
| PMD / CPD | 중간-높음 | unused code, empty catch, duplication, 복잡도 같은 AI 생성 코드 냄새를 탐지한다. |
| Checkstyle | 중간 | naming, import, Javadoc, 크기 규칙 강제에 좋다. 다만 최신 Java language feature 지원 범위를 확인하며 보수적으로 적용한다. |
| Spotless | 높음 | 포맷 논쟁 제거. `spotlessCheck` 실패와 `spotlessApply` 수정을 Gradle에 붙이기 좋다. |

## 아키텍처와 도메인 보호

| 도구 | 추천도 | 적용 포인트 |
| --- | --- | --- |
| Spring Modulith | 중간-높음 | `auth`, `game`, `match`, `card`, `community`, `admin` 같은 모듈이 생기면 모듈 의존성 검증에 유용하다. |
| OpenRewrite | 중간 | AI가 대량 변경한 코드의 스타일, 마이그레이션, 보안 수정 recipe를 기계적으로 정리할 때 좋다. |

## 테스트 방어

| 도구 | 추천도 | 적용 포인트 |
| --- | --- | --- |
| Testcontainers | 필수에 가까움 | MySQL, JPA, WebSocket 통합 테스트를 실제 의존성으로 검증한다. mock으로 통과하는 잘못된 persistence 구현을 방지한다. |
| Spring Security Test | 높음 | REST와 STOMP 인증, 권한, CSRF, 세션 정책을 테스트로 고정한다. |
| JaCoCo | 중간 | 최소 coverage gate. 단독으로는 약하지만 테스트 없는 AI 구현을 막는 기본선이다. |
| PIT Mutation Testing | 높음, 선택 도입 | assertion 없는 테스트나 의미 없는 커버리지를 잡는다. 핵심 도메인 규칙, 카드 효과, 턴 상태 전이에 특히 효과적이다. |
| Instancio | 중간 | 테스트 데이터 누락과 편향을 줄인다. random but reproducible 객체 생성으로 DTO/entity 테스트를 강화한다. |
| jqwik | 주의 | property-based testing 자체는 게임 상태 불변식에 적합하지만, jqwik 1.10부터 Anti-AI Usage Clause가 있어 사용 전 라이선스 검토가 필요하다. |

## 보안과 공급망

| 도구 | 추천도 | 검토 |
| --- | --- | --- |
| OWASP Dependency-Check | 높음 | Gradle plugin으로 CVE 기반 SCA가 가능하다. 초기 NVD 데이터 다운로드가 오래 걸릴 수 있으므로 CI 캐시가 필요하다. |
| CodeQL | 높음 | Java/Kotlin 코드의 취약점과 오류를 탐지하고 GitHub code scanning alert로 노출할 수 있다. |
| Semgrep | 중간-높음 | 커스텀 룰로 Controller에서 Repository 접근 금지, STOMP SEND 권한검사 누락 금지 같은 조직 규칙을 작성할 수 있다. |
| Gitleaks | 높음 | API key, token, password 커밋을 방지한다. pre-commit hook과 GitHub Action 모두 가능하다. |
| OpenSSF Scorecard | 중간 | 직접 코드 품질보다 저장소 운영 보안 관행 점검에 가깝다. |

## 프론트엔드 방어 장치 검토

명세상 프론트엔드는 React 클라이언트이며, 백엔드와 같은 사이트 배포를 전제로 REST API와 STOMP WebSocket 이벤트를 사용한다. 따라서 FE 하네스는 단순 포맷 검사보다 다음 위험을 막는 데 초점을 둔다.

- 백엔드 계약과 다른 요청/응답 타입을 손으로 작성한다.
- REST와 STOMP 오류 코드, `stateVersion`, 재접속 상태를 화면에서 다르게 해석한다.
- 클라이언트가 게임 결과, 카드 효과, 승패를 자체 계산해 서버 권위를 흐린다.
- 낙관적 UI가 실패 시 롤백되지 않거나 서버 확정 상태와 충돌한다.
- WebSocket 이벤트가 중복, 역순, 지연 도착했을 때 오래된 상태가 최신 상태를 덮어쓴다.
- 인증, CSRF, 세션 만료, 계정 정지, 제재 상태를 UI 라우팅만으로 처리하고 API/STOMP 실패를 놓친다.
- 접근성, 반응형 레이아웃, 로딩/빈 상태/오류 상태가 테스트되지 않는다.
- 의존성 업데이트, 번들 증가, secret 노출, XSS가 PR에서 걸러지지 않는다.

### FE 기본 스택 판단

| 영역 | 추천 | 판단 |
| --- | --- | --- |
| 앱 프레임워크 | Vite + React + TypeScript | MVP가 같은 사이트 SPA에 가깝고 SEO/SSR 요구가 없으므로 가장 단순하다. SSR, 파일 기반 라우팅, 서버 컴포넌트가 필요해지면 Next.js를 별도 검토한다. |
| 언어 설정 | TypeScript strict | `strict`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`를 켠다. AI가 `undefined`, optional field, switch 누락을 대충 처리하는 문제를 줄인다. |
| 패키지 매니저 | pnpm 또는 npm ci | FE 전용 lockfile을 고정한다. pnpm을 쓰면 `pnpm install --frozen-lockfile`을 CI 기본값으로 둔다. npm을 쓰면 `npm ci`를 사용한다. |
| 포맷 | Prettier | 포맷 논쟁을 제거한다. Biome도 가능하지만 type-aware lint와 React 생태계 규칙까지 한 번에 대체하기보다는 Prettier + ESLint 조합이 더 보수적이다. |
| 서버 상태 | TanStack Query | REST 조회, 캐시, 재시도, mutation, invalidation을 통제한다. 서버 상태를 Zustand/Context에 직접 복제하지 않는다. |
| 라우팅 | TanStack Router 또는 React Router | 타입 안전한 search/path params가 중요하면 TanStack Router, 단순 MVP면 React Router도 충분하다. 어떤 선택이든 route guard는 UX 보조이며 보안 판단으로 보지 않는다. |
| 복잡한 UI 상태 | XState 또는 명시적 reducer | 매칭, 게임 접속, 턴 단계, 재접속 같은 상태 전이는 ad-hoc boolean 여러 개보다 상태 기계나 discriminated union으로 고정한다. |
| 폼 | React Hook Form + Zod | 입력값 변환과 검증을 서버 계약과 맞춘다. 폼 상태와 서버 상태를 섞지 않는다. |
| 런타임 검증 | Zod, Valibot, TypeBox 중 하나 | API/STOMP 응답은 TypeScript 타입만 믿지 말고 런타임 schema를 통과시킨다. 팀 친숙도가 없으면 Zod가 가장 무난하다. |

### FE 정적 분석

| 도구 | 추천도 | 막는 문제 |
| --- | --- | --- |
| `tsc --noEmit` | 필수 | 타입 오류가 있어도 번들러가 지나가는 상황을 차단한다. CI에서 독립 스텝으로 둔다. |
| typescript-eslint type-aware rules | 필수 | `no-floating-promises`, `no-misused-promises`, `no-unsafe-*`, 불필요한 `any`, 잘못된 async handler를 잡는다. 공식 문서는 `recommended-type-checked`, `strict-type-checked`, `projectService: true` 구성을 제공한다. |
| eslint-plugin-react-hooks | 필수 | `useEffect`, `useMemo`, custom hook dependency 누락을 잡는다. WebSocket subscribe/unsubscribe 누락 방지에 중요하다. |
| eslint-plugin-jsx-a11y | 높음 | label, aria, keyboard interaction 같은 접근성 누락을 정적 단계에서 잡는다. |
| eslint-plugin-testing-library | 높음 | React Testing Library 테스트가 DOM 구현 세부에 결합되는 문제를 줄인다. |
| eslint-plugin-playwright | 중간-높음 | E2E 테스트에서 brittle selector, 잘못된 wait, skipped test를 줄인다. |
| dependency-cruiser 또는 eslint-plugin-boundaries | 높음 | FE 레이어와 feature 간 import 규칙을 강제한다. AI가 `features/game`에서 `pages/admin`을 직접 import하는 식의 오염을 막는다. |
| Knip | 중간-높음 | unused files, exports, dependencies를 탐지한다. AI가 만든 죽은 코드와 남은 의존성을 제거하는 데 좋다. |
| Madge | 중간 | 순환 의존성 탐지에 유용하다. dependency-cruiser를 쓰면 후순위다. |
| Stylelint | 중간 | CSS Modules, plain CSS, SCSS를 많이 쓸 때 유용하다. Tailwind 위주면 우선순위는 낮다. |
| publint | 낮음 | 라이브러리 패키지를 배포할 때 유용하다. 앱 저장소에서는 후순위다. |

권장 ESLint 방향은 다음과 같다.

- flat config 사용
- `@typescript-eslint/strict-type-checked`, `@typescript-eslint/stylistic-type-checked`
- `parserOptions.projectService = true`
- `no-floating-promises`, `no-misused-promises`, `switch-exhaustiveness-check`, `consistent-type-imports` 강화
- React Hooks, JSX a11y, Testing Library, Playwright 규칙 추가
- `eslint-disable`은 설명 주석을 요구하고, 전체 파일 disable은 금지

### FE 계약 보호

| 장치 | 추천도 | 적용 방식 |
| --- | --- | --- |
| OpenAPI | 필수 | REST 계약의 단일 원천. 백엔드에서 OpenAPI를 생성하거나 수동 spec을 관리한다. |
| openapi-typescript 또는 Orval | 필수 | OpenAPI에서 TS 타입과 client를 생성한다. endpoint path, method, response shape를 손으로 쓰지 않는다. |
| JSON Schema for STOMP | 필수 | `CONNECT` 이후 주고받는 command/event payload를 schema로 관리한다. event name, `gameId`, `turnNo`, `stateVersion`, `errorCode`를 검증한다. |
| Zod/Valibot/TypeBox runtime validator | 필수 | 서버 응답, STOMP 이벤트, localStorage/sessionStorage 복원값을 런타임에서 검증한다. |
| MSW | 높음 | REST mock을 fetch/XHR 레벨에서 제공한다. 컴포넌트 테스트와 Storybook이 같은 mock을 쓰게 한다. |
| STOMP fake server/harness | 높음 | E2E와 component test에서 이벤트 순서, 중복, 지연, 연결 끊김, 재접속을 재현한다. |
| Pact | 선택 | FE/BE가 별도 릴리스되거나 팀이 분리되면 consumer-driven contract로 검토한다. MVP 같은 릴리스 단위라면 OpenAPI/JSON Schema/fixture가 먼저다. |

계약 보호 규칙은 강하게 가져간다.

- `fetch('/api/...')` 직접 호출 금지. `src/api/generated` 또는 래핑된 `src/api/client`만 사용한다.
- `client.publish({ destination: '...' })` 직접 호출 금지. `src/realtime/commands`의 typed function만 사용한다.
- REST와 STOMP 오류는 같은 `AppError` 모델로 변환한다.
- 서버에서 온 `stateVersion`이 현재보다 낮으면 적용하지 않는다.
- 비공개 정보는 개인 채널 이벤트 schema에만 존재하게 하고, 공개 경기 채널 schema에는 들어가지 않게 fixture 테스트를 둔다.
- localStorage에는 인증 토큰을 저장하지 않는다. MVP는 same-site session cookie 전제다.

### FE 테스트 전략

| 계층 | 도구 | 필수 여부 | 검증 대상 |
| --- | --- | --- | --- |
| 타입 테스트 | `tsc --noEmit`, `tsd` 또는 `expect-type` | `tsc` 필수, 타입 테스트 선택 | public hook/client API의 타입 안정성, discriminated union exhaustiveness |
| 단위 테스트 | Vitest | 필수 | 순수 함수, reducer, 상태 전이, 에러 변환, event deduplication |
| 컴포넌트 테스트 | React Testing Library + user-event | 필수 | 사용자 관점 렌더링, 버튼/폼/키보드 조작, 로딩/오류/빈 상태 |
| API mock 테스트 | MSW | 높음 | REST 성공/실패/401/403/429/5xx, CSRF 실패, schema mismatch |
| WebSocket 테스트 | STOMP fake server + Vitest/Playwright | 높음 | 중복 이벤트, 역순 이벤트, reconnect, 개인 오류 채널, 권한 실패 |
| E2E | Playwright | 필수 | 로그인, 매칭, 게임 입장, 행동 제출, 불법 행동 실패, 재접속, 제재/세션 만료 |
| 접근성 | axe-core, jest-axe, Playwright axe, Storybook a11y | 높음 | aria, label, contrast, keyboard path, focus trap |
| 시각 회귀 | Playwright screenshot, Chromatic, Percy 중 하나 | 중간-높음 | 보드/카드/모달/반응형 깨짐 |
| 성능 | Lighthouse CI, bundle size check | 중간 | 초기 로딩, JS 번들 크기, Web Vitals 회귀 |

Playwright는 Chromium, Firefox, WebKit을 같은 API로 테스트하고, auto-waiting assertion, trace, screenshot, video artifact를 제공하므로 FE 최종 게이트로 적합하다. 단, 모든 E2E를 매 PR에 무겁게 돌리기보다 smoke E2E와 nightly full E2E를 분리한다.

### FE 아키텍처 규칙

초기 구조는 과하게 복잡하게 나누지 않되 import 경계는 명확히 둔다.

```text
src/
  app/             # provider, router, global error boundary
  pages/           # route 단위 composition
  features/        # auth, match, game, deck, community, admin
  entities/        # user, game, card 등 도메인 UI model
  shared/          # ui, lib, config, test, types
  api/
    generated/     # OpenAPI generated code. 수동 수정 금지
    client/        # fetch wrapper, error normalization
  realtime/
    generated/     # STOMP event/command schema types
    client/        # STOMP connection wrapper
    commands/      # typed command publish API
```

강제 규칙 예시:

- `shared`는 `features`, `pages`, `app`을 import하지 못한다.
- `entities`는 `features`, `pages`를 import하지 못한다.
- `features/*`는 다른 feature 내부 파일을 직접 import하지 않고 public API만 import한다.
- `pages`는 composition만 담당하고 fetch/STOMP 직접 호출을 하지 않는다.
- React component에서 `fetch`, `WebSocket`, `Client.publish`를 직접 호출하지 않는다.
- `api/generated`, `realtime/generated`는 수동 수정 금지 영역으로 둔다.
- 테스트 helper는 production code에서 import하지 못한다.
- admin feature는 일반 user feature에서 import하지 않는다.

이 규칙은 dependency-cruiser, eslint-plugin-boundaries, path alias 정책으로 CI에서 실패하게 만든다.

### FE 보안 방어

| 위험 | 방어 장치 |
| --- | --- |
| XSS | React 기본 escaping을 유지하고 `dangerouslySetInnerHTML` 금지. 사용자 작성 Markdown/HTML이 필요하면 DOMPurify 같은 sanitizer와 snapshot/security test를 둔다. |
| secret 노출 | `.env`에서 클라이언트 노출 prefix만 허용한다. Vite 기준 `VITE_` 변수만 클라이언트 노출 대상으로 관리하고, Gitleaks를 FE 파일에도 적용한다. |
| CSRF 누락 | 상태 변경 REST와 STOMP `CONNECT`에 CSRF header/token 처리 테스트를 둔다. 실패 시 UI가 재시도 루프에 빠지지 않게 한다. |
| 세션 만료 | REST `401`, STOMP 인증 실패, 개인 오류 이벤트를 같은 auth state transition으로 처리한다. |
| 권한/UI 불일치 | 라우트 guard는 UX 보조일 뿐이며, API/STOMP 실패를 최종 진실로 처리한다. admin UI는 서버 권한 실패 케이스를 반드시 테스트한다. |
| 공개/비공개 정보 혼합 | 공개 경기 채널 event schema에는 상대 legend card, 내부 MMR 등 비공개 필드가 들어가지 않게 fixture와 schema test를 둔다. |
| 클릭 연타/중복 제출 | mutation dedupe, idempotency key/actionId, disabled pending state, server response reconciliation을 함께 테스트한다. |
| 과도한 WebSocket 재연결 | exponential backoff, max retry, visibility change 처리, reconnect event test를 둔다. |
| supply chain | lockfile, frozen install, Dependabot, dependency review, npm/pnpm audit, license checker를 CI에 둔다. |

### FE 접근성과 UX 품질 게이트

AI가 만든 화면은 보통 정상 데이터 한 가지 경로만 예쁘게 통과한다. 다음 상태를 story/test fixture로 고정한다.

- 로딩, 빈 결과, 오류, 권한 없음, 세션 만료
- 모바일/태블릿/데스크톱 viewport
- 키보드만으로 매칭 시작, 카드 선택, 행동 취소, 모달 닫기
- 스크린 리더 label이 필요한 버튼, 아이콘 버튼, 탭, 메뉴
- 게임 보드 좌표, 선택된 말/카드, 가능한 행동의 시각적/비시각적 상태
- 네트워크 지연, 재시도 중, reconnect grace period countdown
- STOMP 연결 끊김과 복구 후 최신 서버 상태 재동기화

도구 조합:

- Storybook: 컴포넌트 상태 fixture와 문서화
- Storybook a11y addon 또는 axe-core: 접근성 기본 검증
- Playwright screenshot: 핵심 화면 시각 회귀
- Lighthouse CI: 성능/접근성/Best Practices budget
- size-limit 또는 bundlesize: 번들 크기 회귀 차단

### FE 관측과 장애 분석

| 도구 | 추천도 | 검토 |
| --- | --- | --- |
| Sentry | 중간-높음 | 런타임 에러, sourcemap, release tracking, replay를 제공한다. 카드/비공개 상태가 녹화나 breadcrumb에 남지 않도록 scrubber 설정이 필요하다. |
| OpenTelemetry Web | 중간 | 백엔드 tracing과 연결하려면 검토한다. MVP에서는 비용 대비 후순위일 수 있다. |
| Web Vitals | 중간 | 초기 로딩, interaction 지연, layout shift를 추적한다. 게임 화면에서 UI 지연을 잡는 데 유용하다. |
| LogRocket 등 session replay | 선택 | 재현 어려운 FE 버그 분석에는 좋지만 개인정보와 비공개 게임 정보 노출 정책을 먼저 정해야 한다. |

### FE CI 스크립트 초안

FE가 같은 저장소의 `frontend/` 또는 별도 저장소로 생긴다는 전제로 다음 스크립트를 둔다.

```json
{
  "scripts": {
    "format:check": "prettier --check .",
    "lint": "eslint . --max-warnings=0",
    "typecheck": "tsc --noEmit",
    "test": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:a11y": "playwright test --project=a11y",
    "build": "vite build",
    "analyze:deps": "knip",
    "analyze:boundaries": "depcruise src",
    "audit": "pnpm audit --audit-level high",
    "ci": "pnpm run format:check && pnpm run lint && pnpm run typecheck && pnpm run test && pnpm run build"
  }
}
```

CI 필수 체크 이름은 명확히 분리한다.

- `fe/install-frozen`
- `fe/format`
- `fe/lint`
- `fe/typecheck`
- `fe/unit`
- `fe/build`
- `fe/e2e-smoke`
- `fe/a11y`
- `fe/bundle-budget`
- `fe/contract-drift`

무거운 체크는 nightly로 분리한다.

- 전체 브라우저 E2E
- 전체 시각 회귀
- Lighthouse full run
- dependency audit full report

### FE 우선 도입 순서

1. TypeScript strict tsconfig, ESLint type-aware, Prettier를 먼저 고정한다.
2. OpenAPI 기반 REST client 생성과 STOMP JSON Schema를 정한다.
3. API/STOMP 직접 호출 금지 규칙을 ESLint 또는 dependency-cruiser로 강제한다.
4. TanStack Query로 REST 서버 상태를 관리하고, WebSocket 이벤트는 별도 realtime store/reducer로 제한한다.
5. Vitest + Testing Library + MSW로 상태별 컴포넌트 테스트를 만든다.
6. Playwright smoke E2E를 CI 필수 체크로 둔다.
7. axe-core 기반 a11y 테스트와 핵심 화면 screenshot 회귀를 추가한다.
8. Lighthouse CI, bundle size budget, Sentry 같은 운영 품질 도구를 후속으로 붙인다.

## 이 프로젝트의 권장 도입 순서

1. `spotless`, `archunit`, `spotbugs`, `pmd`, `jacoco`를 Gradle `check`에 묶는다.
2. GitHub Actions에서 `./gradlew check`를 필수화한다.
3. branch protection으로 required status checks, PR review, force push 차단을 설정한다.
4. Gradle dependency locking/verification을 생성하고 커밋한다.
5. Dependency Review Action, Dependabot, Gitleaks를 추가한다.
6. 도메인 코드가 생기면 ArchUnit 규칙을 구체화한다: `web -> application -> domain <- infrastructure`.
7. 게임 규칙과 상태 전이는 PIT 또는 property-based test로 강화한다.
8. FE 저장소 또는 `frontend/` 디렉터리가 생기면 `fe/typecheck`, `fe/lint`, `fe/unit`, `fe/build`, `fe/e2e-smoke`, `fe/contract-drift`를 필수 체크로 추가한다.
9. REST OpenAPI와 STOMP JSON Schema를 백엔드 변경 PR의 산출물로 만들고, FE CI에서 generated client/schema diff를 검사한다.
10. FE와 BE가 같은 릴리스 단위라면 contract fixture를 공유하고, 분리 릴리스로 바뀌면 Pact 같은 consumer-driven contract를 추가 검토한다.

## 우선 적용할 구체 규칙 예시

### ArchUnit

- `..web..` 또는 `..controller..`는 `..repository..`에 직접 접근하지 못한다.
- `..domain..`은 `org.springframework..`, `jakarta.persistence..`에 의존하지 않는다.
- `..application..`은 `..web..`에 의존하지 않는다.
- `..infrastructure..`는 `..web..`에 의존하지 않는다.
- `auth`, `game`, `match`, `card`, `community`, `admin` 모듈 간 순환 의존성을 금지한다.
- STOMP 핸들러는 공통 인증/권한 검사 컴포넌트를 거치도록 강제한다.

### Gradle check

- `compileJava`
- `test`
- `spotlessCheck`
- `pmdMain`, `pmdTest`
- `spotbugsMain`, `spotbugsTest`
- `jacocoTestCoverageVerification`
- `dependencyCheckAnalyze`
- ArchUnit 테스트

### Git Hook

- pre-commit: `spotlessCheck`, YAML/Markdown 기본 검사, Gitleaks
- pre-push: `./gradlew check`
- commit-msg: Conventional Commits 또는 issue key 형식 강제

## 주의할 점

- 로컬 훅은 우회 가능하므로 최종 방어선은 CI와 branch protection이어야 한다.
- coverage gate는 숫자만 높여도 의미 없는 테스트가 생길 수 있으므로 PIT나 도메인 불변식 테스트와 함께 써야 한다.
- Checkstyle, Error Prone, NullAway는 Java 25, Spring Boot 4, Lombok 조합에서 호환성 검증 후 적용한다.
- Dependency verification metadata는 생성 후 반드시 리뷰해야 한다. 이미 오염된 dependency를 기준으로 metadata를 만들면 오염을 고정할 수 있다.
- jqwik은 property-based testing 관점에서는 적합하지만 라이선스 문구를 먼저 확인한다.
- FE 로컬 라우트 guard, 버튼 disabled, 클라이언트 상태 검사는 UX 보조일 뿐 보안 경계가 아니다. 서버 실패 응답과 STOMP 개인 오류 이벤트를 최종 진실로 처리해야 한다.
- FE generated code는 수동 수정하지 않는다. 계약이 틀렸다면 schema 또는 백엔드 계약을 고친 뒤 다시 생성한다.
- Playwright E2E는 안정적인 role/text/test-id selector를 사용하고, 임의 timeout 대기는 금지한다.
- 시각 회귀와 Lighthouse는 환경 영향이 있으므로 모든 PR 필수 체크로 시작하기보다 핵심 smoke만 필수화하고 nightly full run으로 확장한다.

## 참고 공식 문서

- ArchUnit: https://www.archunit.org/userguide/html/000_Index.html
- Gradle dependency locking: https://docs.gradle.org/current/userguide/dependency_locking.html
- Gradle dependency verification: https://docs.gradle.org/current/userguide/dependency_verification.html
- Spring Modulith: https://spring.io/projects/spring-modulith
- typescript-eslint typed linting: https://typescript-eslint.io/getting-started/typed-linting/
- TypeScript tsconfig: https://www.typescriptlang.org/tsconfig/
- Vite guide: https://vite.dev/guide/
- TanStack Query: https://tanstack.com/query/latest/docs/framework/react/overview
- Playwright: https://playwright.dev/
- Vitest: https://vitest.dev/
- Mock Service Worker: https://mswjs.io/
- dependency-cruiser: https://github.com/sverweij/dependency-cruiser
- pre-commit: https://pre-commit.com/
- Husky: https://typicode.github.io/husky/

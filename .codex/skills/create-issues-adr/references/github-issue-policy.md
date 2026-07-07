# GitHub Issue Policy

GitHub Issue는 로컬 이슈 문서의 외부 추적 링크다. 로컬 문서가 우선이며, GitHub Issue는 명시 요청과 승인 없이 생성하지 않는다.

## 생성 조건

- 사용자가 GitHub Issue 생성을 명시적으로 요청해야 한다.
- 생성 전 대상 로컬 이슈 목록, 제목, 본문 요약을 사용자에게 보여주고 승인을 받아야 한다.
- `.github/ISSUE_TEMPLATE/feature-implementation.md`가 없으면 GitHub Issue 생성을 중단하고 로컬 문서만 유지한다.
- 연결 후 로컬 이슈 frontmatter와 `docs/issue-map.md`를 갱신해야 한다.

## 제목 규칙

```text
[{feature}-{nnn}] {title}
```

예:

```text
[matchmaking-001] 매칭 큐 입장 API 구현
```

GitHub Issue 번호는 GitHub가 부여하는 별도 번호다. 로컬 문서 번호와 같다고 가정하지 말고, 모든 상호 참조는 `{feature}-{nnn}`을 기준으로 한다.

## 본문 생성

GitHub Issue 본문은 `.github/ISSUE_TEMPLATE/feature-implementation.md`를 읽어 렌더링한다. template의 필드가 로컬 이슈 문서와 겹치면 로컬 이슈 문서 내용을 기준으로 채운다.

template에 없는 필수 대응 정보는 본문 하단에 `문서 연결` 섹션으로 추가한다.

```markdown
## 문서 연결

- Local issue: docs/features/{feature}/issues/{feature}-{nnn}-{slug}/issue.md
- Local issue ID: {feature}-{nnn}
- Feature PRD: docs/features/{feature}/prd.md
- Feature TRD: docs/features/{feature}/trd.md
- Related ADRs: {관련 ADR 링크 또는 없음}
- Depends on: {선행 로컬 이슈 ID 또는 없음}
```

본문에는 최소한 다음 정보를 포함한다.

- 로컬 이슈 ID
- 로컬 이슈 문서 경로
- 관련 feature PRD/TRD 경로
- 관련 ADR 문서 경로
- 의존 로컬 이슈 ID
- 핵심 Acceptance Criteria
- 테스트 시나리오 또는 TDD 관점
- 미확정 사항

## 생성 순서

1. 대상 로컬 이슈 목록과 GitHub 제목, 본문 요약, 관련 ADR, 의존 이슈 대응표를 사용자에게 제시한다.
2. 사용자가 승인한 이슈만 생성한다.
3. `gh auth status`로 CLI 인증을 확인한다.
4. `gh` CLI가 사용 가능하면 임시 본문 파일을 만들고 `gh issue create --title ... --body-file ...`로 생성한다.
5. `gh` CLI가 실패하거나 인증이 불가능하면 GitHub MCP/app connector를 탐색해 생성한다.
6. `gh` CLI와 GitHub MCP/app connector가 모두 실패하거나 사용할 수 없으면 GitHub Issue 생성은 건너뛰고 local-only 상태로 보고한다.

CLI 예시는 다음과 같다.

```bash
gh issue create --title "[{feature}-{nnn}] {title}" --body-file /tmp/create-issues-adr-gh/{feature}-{nnn}.md
```

현재 GitHub repository를 자동으로 찾지 못하면 `git remote -v`로 `origin`을 확인하고 `--repo OWNER/REPO`를 명시한다.

GitHub MCP/app connector가 필요한 경우 사용 가능한 GitHub 도구를 탐색하고, issue 생성 기능이 있는 도구만 사용한다. 도구를 찾을 수 없거나 권한이 없으면 local-only로 전환한다.

## 로컬 문서 연결

GitHub Issue 생성 후 로컬 이슈 frontmatter를 갱신한다.

```yaml
github_issue: 123
github_url: "https://github.com/{owner}/{repo}/issues/123"
```

`docs/issue-map.md`가 없으면 생성하고, 있으면 기존 표에 추가하거나 갱신한다.

```markdown
# Issue Map

| Local ID | Feature | Local Path | GitHub Issue | GitHub URL | Status |
| --- | --- | --- | --- | --- | --- |
| {feature}-{nnn} | {feature} | docs/features/{feature}/issues/{feature}-{nnn}-{slug}/issue.md | #{number} | {url} | draft |
```

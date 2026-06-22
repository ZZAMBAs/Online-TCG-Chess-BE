# GitHub Issue Policy

GitHub Issue는 로컬 이슈 문서의 외부 추적 링크다. 로컬 문서가 우선이며, GitHub Issue는 명시 요청과 승인 없이 생성하지 않는다.

## 생성 조건

- 사용자가 GitHub Issue 생성을 명시적으로 요청해야 한다.
- 생성 전 대상 로컬 이슈 목록, 제목, 본문 요약을 사용자에게 보여주고 승인을 받아야 한다.
- 연결 후 로컬 문서와 `docs/issue-map.md`를 갱신해야 한다.

## 제목 규칙

```text
[{feature}-{nnn}] {title}
```

예:

```text
[matchmaking-001] 매칭 큐 입장 API 구현
```

## 본문 권장 구조

```markdown
Local issue: docs/features/{feature}/issues/{feature}-{nnn}.md

## Summary

{로컬 이슈 목적 요약}

## Acceptance Criteria

{핵심 수용 기준}

## Related ADRs

{관련 ADR 링크 또는 없음}
```

## 로컬 문서 연결

GitHub Issue 생성 후 로컬 이슈 frontmatter를 갱신한다.

```yaml
github_issue: 123
github_url: "https://github.com/{owner}/{repo}/issues/123"
```

`docs/issue-map.md`가 없으면 생성하고, 있으면 기존 표에 추가한다.

```markdown
# Issue Map

| Local ID | Feature | Local Path | GitHub Issue | GitHub URL | Status |
| --- | --- | --- | --- | --- | --- |
| {feature}-{nnn} | {feature} | docs/features/{feature}/issues/{feature}-{nnn}.md | #{number} | {url} | draft |
```

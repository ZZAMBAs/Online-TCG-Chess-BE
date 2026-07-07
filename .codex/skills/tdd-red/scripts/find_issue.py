#!/usr/bin/env python3
"""Find a local feature issue directory for the tdd-red skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ARGUMENT_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]+$")


def parse_issue_argument(value: str) -> tuple[str, str, int]:
    argument = value.strip()
    if not argument:
        raise ValueError("이슈 인자가 비어 있습니다.")
    if not ARGUMENT_RE.fullmatch(argument):
        raise ValueError(
            "이슈 인자는 마지막 토큰이 숫자인 hyphen-case여야 합니다. 예: auth-1, auth-issues-1, xxx-yyy-1"
        )

    parts = argument.split("-")
    issue_number_raw = parts[-1]
    feature_parts = parts[:-1]
    if feature_parts and feature_parts[-1] == "issues":
        feature_parts = feature_parts[:-1]
    if not feature_parts:
        raise ValueError("feature 이름을 확인할 수 없습니다.")

    return "-".join(feature_parts), issue_number_raw, int(issue_number_raw)


def find_issue(root: Path, feature: str, issue_number: int) -> list[Path]:
    issues_dir = root / "docs" / "features" / feature / "issues"
    if not issues_dir.is_dir():
        raise FileNotFoundError(f"이슈 디렉터리가 없습니다: {issues_dir}")

    dirname_re = re.compile(rf"^{re.escape(feature)}-([0-9]+)(?:-.+)?$")
    matches: list[Path] = []
    for path in sorted(issues_dir.glob(f"{feature}-*")):
        if not path.is_dir():
            continue
        match = dirname_re.fullmatch(path.name)
        if match and int(match.group(1)) == issue_number and (path / "issue.md").is_file():
            matches.append(path)
    return matches


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find docs/features/{feature}/issues/{feature}-{nnn}-{slug}/issue.md from a flexible issue argument."
    )
    parser.add_argument("issue", help="Issue argument such as auth-1, auth-001, auth-issues-1, xxx-yyy-1")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()

    try:
        feature, issue_number_raw, issue_number = parse_issue_argument(args.issue)
        matches = find_issue(root, feature, issue_number)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not matches:
        print(
            f"ERROR: issue not found: feature={feature}, issue_number={issue_number}",
            file=sys.stderr,
        )
        return 1
    if len(matches) > 1:
        print(
            "ERROR: multiple issue directories found:\n"
            + "\n".join(str(path.relative_to(root)) for path in matches),
            file=sys.stderr,
        )
        return 1

    issue_dir = matches[0]
    result = {
        "argument": args.issue,
        "feature": feature,
        "issue_number_raw": issue_number_raw,
        "issue_number": issue_number,
        "issue_dir": str(issue_dir.relative_to(root)),
        "issue_file": str((issue_dir / "issue.md").relative_to(root)),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

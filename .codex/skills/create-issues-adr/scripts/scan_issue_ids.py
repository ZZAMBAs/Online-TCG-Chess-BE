#!/usr/bin/env python3
"""Scan local issue and ADR documents for duplicate identifiers.

This script is read-only. It exits with 1 when duplicate local issue IDs,
ADR IDs, or GitHub issue number mappings are found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*", re.DOTALL)
FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
GITHUB_URL_RE = re.compile(r"github\.com/[^/\s]+/[^/\s]+/issues/(\d+)")
ISSUE_STEM_RE = re.compile(r"^(.+)-(\d{3})(?:-.+)?$")
ADR_STEM_RE = re.compile(r"^adr-(\d{3})(?:-.+)?$")
ScanResult = dict[str, Any]


def iter_markdown(root: Path, pattern: str) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(root.glob(pattern))


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    values: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("-"):
            continue
        field_match = FIELD_RE.match(line)
        if not field_match:
            continue
        key, value = field_match.groups()
        values[key] = value.strip().strip('"').strip("'")
    return values


def issue_id_from_path(path: Path) -> str:
    issue_dir = path.parent if path.name == "issue.md" else path
    match = ISSUE_STEM_RE.match(issue_dir.name)
    if match:
        feature, number = match.groups()
        return f"{feature}-{number}"
    return issue_dir.name


def adr_id_from_path(path: Path) -> str:
    feature = path.parent.parent.name.upper()
    match = ADR_STEM_RE.match(path.stem)
    if match:
        return f"ADR-{feature}-{match.group(1)}"
    return path.stem


def collect_duplicates(items: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(paths) for key, paths in sorted(items.items()) if key and len(paths) > 1}


def scan(root: Path) -> ScanResult:
    issue_ids: dict[str, set[str]] = defaultdict(set)
    adr_ids: dict[str, set[str]] = defaultdict(set)
    github_issues: dict[str, set[str]] = defaultdict(set)

    issue_paths = list(iter_markdown(root, "docs/features/*/issues/*/issue.md"))
    adr_paths = list(iter_markdown(root, "docs/features/*/adr/*.md"))

    for path in issue_paths:
        rel = path.relative_to(root).as_posix()
        meta = parse_frontmatter(path)

        local_id = meta.get("id") or issue_id_from_path(path)
        issue_ids[local_id].add(rel)

        github_issue = meta.get("github_issue")
        if github_issue and github_issue.lower() not in {"null", "none"}:
            github_issues[github_issue.lstrip("#")].add(rel)

        github_url = meta.get("github_url")
        if github_url:
            match = GITHUB_URL_RE.search(github_url)
            if match:
                github_issues[match.group(1)].add(rel)

    for path in adr_paths:
        rel = path.relative_to(root).as_posix()
        meta = parse_frontmatter(path)
        adr_id = meta.get("id") or adr_id_from_path(path)
        adr_ids[adr_id].add(rel)

    duplicates = {
        "issue_ids": collect_duplicates(issue_ids),
        "adr_ids": collect_duplicates(adr_ids),
        "github_issues": collect_duplicates(github_issues),
    }

    return {
        "root": str(root),
        "counts": {
            "issues": len(issue_paths),
            "adrs": len(adr_paths),
        },
        "duplicates": duplicates,
        "ok": not any(duplicates.values()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan issue and ADR identifiers for duplicates.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def print_text_result(result: ScanResult) -> None:
    counts = result["counts"]
    print(f"Scanned {counts['issues']} issue document(s) and {counts['adrs']} ADR document(s).")

    if result["ok"]:
        print("No duplicate issue IDs, ADR IDs, or GitHub issue mappings found.")
    else:
        print_duplicates(result["duplicates"])


def print_duplicates(duplicates: dict[str, dict[str, list[str]]]) -> None:
    print("Duplicates found:")
    for category, values in duplicates.items():
        if not values:
            continue
        print(f"- {category}")
        for value, paths in values.items():
            print(f"  - {value}: {', '.join(paths)}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = scan(root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text_result(result)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

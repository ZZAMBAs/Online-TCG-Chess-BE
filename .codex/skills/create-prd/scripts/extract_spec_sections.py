#!/usr/bin/env python3
"""Extract numbered top-level sections from a Markdown spec."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")


@dataclass(frozen=True)
class Section:
    number: int
    title: str
    start_line: int
    end_line: int
    body: str


def parse_sections(path: Path) -> list[Section]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: list[tuple[int, int, str]] = []

    for index, line in enumerate(lines, start=1):
        match = SECTION_RE.match(line)
        if match:
            headings.append((int(match.group(1)), index, match.group(2)))

    sections: list[Section] = []
    for idx, (number, start_line, title) in enumerate(headings):
        end_line = headings[idx + 1][1] - 1 if idx + 1 < len(headings) else len(lines)
        body = "\n".join(lines[start_line - 1 : end_line])
        sections.append(
            Section(
                number=number,
                title=title,
                start_line=start_line,
                end_line=end_line,
                body=body,
            )
        )

    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract numbered sections from spec-fixed.md")
    parser.add_argument("--file", required=True, help="Markdown spec file path")
    parser.add_argument("--list", action="store_true", help="List numbered sections")
    parser.add_argument("--section", type=int, help="Print a single section by number")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    sections = parse_sections(path)

    if args.list:
        for section in sections:
            print(f"{section.number}. {section.title} ({section.start_line}-{section.end_line})")
        return 0

    if args.section is not None:
        for section in sections:
            if section.number == args.section:
                print(section.body)
                return 0
        print(f"Section not found: {args.section}", file=sys.stderr)
        return 1

    parser.error("Specify --list or --section")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

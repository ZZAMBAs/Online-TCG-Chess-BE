#!/usr/bin/env python3
"""Extract numbered top-level Markdown spec sections."""

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
    start: int
    end: int


def parse_sections(text: str) -> list[Section]:
    lines = text.splitlines()
    matches: list[tuple[int, int, str]] = []

    for index, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if match:
            matches.append((int(match.group(1)), index, match.group(2)))

    sections: list[Section] = []
    for idx, (number, start, title) in enumerate(matches):
        end = matches[idx + 1][1] if idx + 1 < len(matches) else len(lines)
        sections.append(Section(number=number, title=title, start=start, end=end))
    return sections


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"ERROR: file not found: {path}")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"ERROR: failed to read UTF-8 file: {path}: {exc}")


def parse_number_list(raw: str) -> list[int]:
    numbers: list[int] = []
    for part in raw.split(","):
        value = part.strip()
        if not value:
            continue
        try:
            numbers.append(int(value))
        except ValueError:
            raise SystemExit(f"ERROR: invalid section number: {value}")
    if not numbers:
        raise SystemExit("ERROR: no section numbers provided")
    return numbers


def section_map(sections: list[Section]) -> dict[int, Section]:
    result: dict[int, Section] = {}
    duplicates: set[int] = set()
    for section in sections:
        if section.number in result:
            duplicates.add(section.number)
        result[section.number] = section
    if duplicates:
        duplicate_text = ", ".join(str(number) for number in sorted(duplicates))
        raise SystemExit(f"ERROR: duplicate top-level section numbers: {duplicate_text}")
    return result


def print_sections(text: str, selected: list[Section]) -> None:
    lines = text.splitlines()
    chunks = ["\n".join(lines[section.start : section.end]).rstrip() for section in selected]
    print("\n\n".join(chunk for chunk in chunks if chunk))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Extract numbered Markdown spec sections.")
    parser.add_argument("--file", required=True, help="Markdown spec file path")
    parser.add_argument("--list", action="store_true", help="List top-level numbered sections")
    parser.add_argument("--section", type=int, help="Extract one top-level section by number")
    parser.add_argument("--sections", help="Extract comma-separated top-level sections by number")
    parser.add_argument("--all", action="store_true", help="Extract all top-level numbered sections")
    args = parser.parse_args()

    modes = [args.list, args.section is not None, args.sections is not None, args.all]
    if sum(1 for enabled in modes if enabled) != 1:
        parser.error("choose exactly one of --list, --section, --sections, or --all")

    path = Path(args.file)
    text = read_text(path)
    sections = parse_sections(text)
    if not sections:
        raise SystemExit("ERROR: no top-level numbered sections found")

    if args.list:
        for section in sections:
            print(f"{section.number}. {section.title}")
        return

    by_number = section_map(sections)
    if args.all:
        selected = sections
    elif args.section is not None:
        if args.section not in by_number:
            raise SystemExit(f"ERROR: section not found: {args.section}")
        selected = [by_number[args.section]]
    else:
        numbers = parse_number_list(args.sections)
        missing = [number for number in numbers if number not in by_number]
        if missing:
            missing_text = ", ".join(str(number) for number in missing)
            raise SystemExit(f"ERROR: section not found: {missing_text}")
        selected = [by_number[number] for number in numbers]

    print_sections(text, selected)


if __name__ == "__main__":
    main()

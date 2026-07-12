#!/usr/bin/env python3
"""Record and verify workflow artifact input/output fingerprints."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


STATE_PATH = Path(".codex/artifact-state.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"workspace outside path: {value}") from error
    return path


def collect(
    root: Path, paths: list[str], globs: list[str], optional_globs: list[str]
) -> dict[str, str]:
    collected: dict[str, str] = {}
    for value in paths:
        path = normalize(root, value)
        if not path.is_file():
            raise ValueError(f"missing file: {value}")
        collected[path.relative_to(root).as_posix()] = digest(path)
    for pattern in globs:
        matches = sorted(root.glob(pattern))
        if not matches:
            raise ValueError(f"glob matched no files: {pattern}")
        for path in matches:
            if path.is_file():
                collected[path.relative_to(root).as_posix()] = digest(path)
    for pattern in optional_globs:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                collected[path.relative_to(root).as_posix()] = digest(path)
    return dict(sorted(collected.items()))


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "artifacts": {}}
    return json.loads(path.read_text())


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def verify_files(root: Path, label: str, expected: dict[str, str]) -> list[str]:
    mismatches: list[str] = []
    for relative_path, expected_digest in expected.items():
        path = root / relative_path
        if not path.is_file():
            mismatches.append(f"{label} missing: {relative_path}")
        elif digest(path) != expected_digest:
            mismatches.append(f"{label} changed: {relative_path}")
    return mismatches


def record(args: argparse.Namespace, root: Path, state_path: Path) -> int:
    inputs = collect(root, args.input, args.input_glob, args.optional_input_glob)
    outputs = collect(root, args.output, args.output_glob, args.optional_output_glob)
    state = load_state(state_path)
    state["artifacts"][args.artifact] = {
        "status": "current",
        "inputs": inputs,
        "outputs": outputs,
    }
    write_state(state_path, state)
    print(f"recorded current artifact: {args.artifact}")
    return 0


def verify(args: argparse.Namespace, root: Path, state_path: Path) -> int:
    state = load_state(state_path)
    artifact = state["artifacts"].get(args.artifact)
    if artifact is None:
        print(f"artifact state missing: {args.artifact}")
        return 2

    mismatches = verify_files(root, "input", artifact.get("inputs", {}))
    mismatches.extend(verify_files(root, "output", artifact.get("outputs", {})))
    if mismatches:
        print(f"artifact stale: {args.artifact}")
        print("\n".join(mismatches))
        return 2

    print(f"artifact current: {args.artifact}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("artifact")
    record_parser.add_argument("--input", action="append", default=[])
    record_parser.add_argument("--input-glob", action="append", default=[])
    record_parser.add_argument("--optional-input-glob", action="append", default=[])
    record_parser.add_argument("--output", action="append", default=[])
    record_parser.add_argument("--output-glob", action="append", default=[])
    record_parser.add_argument("--optional-output-glob", action="append", default=[])

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("artifact")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd().resolve()
    state_path = root / STATE_PATH
    try:
        if args.command == "record":
            if not args.output and not args.output_glob:
                raise ValueError("record requires at least one output")
            return record(args, root, state_path)
        return verify(args, root, state_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"artifact state error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

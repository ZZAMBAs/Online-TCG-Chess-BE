#!/usr/bin/env python3
"""Read-only fingerprint helper for architecture review inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_fingerprint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}

    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.is_file())
        digest = hashlib.sha256()
        entries = []
        for file_path in files:
            relative = file_path.relative_to(path)
            data = file_path.read_bytes()
            file_hash = hashlib.sha256(data).hexdigest()
            digest.update(str(relative).replace("\\", "/").encode("utf-8"))
            digest.update(file_hash.encode("utf-8"))
            entries.append(
                {
                    "path": str(file_path),
                    "relative_path": str(relative).replace("\\", "/"),
                    "size": len(data),
                    "sha256": file_hash,
                }
            )
        return {
            "path": str(path),
            "exists": True,
            "type": "directory",
            "file_count": len(entries),
            "sha256": digest.hexdigest(),
            "files": entries,
        }

    data = path.read_bytes()
    return {
        "path": str(path),
        "exists": True,
        "type": "file",
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print read-only fingerprints for architecture review inputs."
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to fingerprint")
    args = parser.parse_args()

    result = {"inputs": [file_fingerprint(Path(path)) for path in args.paths]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

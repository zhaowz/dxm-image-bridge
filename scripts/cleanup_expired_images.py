#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


COMMIT_MESSAGE = "cleanup expired image cache"
IMAGES_DIR_NAME = "images"


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_design_cache_dir(path: Path) -> bool:
    return path.is_dir() and path.parent.name == IMAGES_DIR_NAME and not path.name.startswith(".")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean expired temporary image caches from dxm-image-bridge.")
    parser.add_argument("--days", type=float, default=3, help="Delete Design ID cache dirs older than this many days.")
    parser.add_argument("--dry-run", action="store_true", help="Print expired dirs without deleting or committing.")
    parser.add_argument("--no-push", action="store_true", help="Commit cleanup but do not push.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    images_dir = root / IMAGES_DIR_NAME
    cutoff_seconds = args.days * 24 * 60 * 60
    now = time.time()

    if not images_dir.exists():
        print("no expired cache")
        return 0

    expired: list[Path] = []
    for child in sorted(images_dir.iterdir()):
        if not is_design_cache_dir(child):
            continue
        age_seconds = now - child.stat().st_mtime
        if age_seconds > cutoff_seconds:
            expired.append(child)

    if not expired:
        print("no expired cache")
        return 0

    print("expired cache directories:")
    for path in expired:
        age_days = (now - path.stat().st_mtime) / (24 * 60 * 60)
        print(f"- {path.relative_to(root)} ({age_days:.2f} days old)")

    if args.dry_run:
        return 0

    for path in expired:
        shutil.rmtree(path)

    run_git(["add", "-A", IMAGES_DIR_NAME], root)
    status = run_git(["status", "--porcelain", "--", IMAGES_DIR_NAME], root).stdout.strip()
    if not status:
        print("no expired cache")
        return 0

    run_git(["commit", "-m", COMMIT_MESSAGE], root)
    if not args.no_push:
        run_git(["push"], root)

    print("cleanup committed and pushed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

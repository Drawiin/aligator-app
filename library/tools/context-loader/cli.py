#!/usr/bin/env python3
"""Suggest relevant files for a task via keyword match or optional manifest."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CLI = Path(__file__).resolve()


class Parser(argparse.ArgumentParser):
    """Usage errors exit 3 (invalid input). Stock argparse exits 2, which this
    toolset reserves for "no results"."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        parts = self.prog.split(" ", 1)
        rest = f" {parts[1]}" if len(parts) > 1 else ""
        print(f"Fix the arguments and retry; for usage run: python3 {CLI}{rest} --help", file=sys.stderr)
        raise SystemExit(3)


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from None
    if number < 1:
        raise argparse.ArgumentTypeError(f"{number} is < 1; pass a positive file count, e.g. --limit 20")
    return number


SKIP_DIRS = {
    ".git",
    ".venv",
    ".data",
    ".secrets",
    "__pycache__",
    "node_modules",
    ".memory",
    "graphify-out",
}

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".txt",
    ".sh",
}


def _keywords(task: str) -> list[str]:
    raw = task.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return [w for w in raw.split() if len(w) >= 2]


def _load_manifest(root: Path) -> list[str] | None:
    for name in ("manifest.json", "context-manifest.json"):
        path = root / ".context" / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"manifest parse failed: {exc}", file=sys.stderr)
            print("Fix .context/manifest.json or omit manifest.", file=sys.stderr)
            sys.exit(1)
        files = data.get("files") or data.get("paths") or []
        if isinstance(files, list):
            return [str(f) for f in files]
    return None


def _score_path(rel: str, keywords: list[str]) -> int:
    hay = rel.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return sum(1 for kw in keywords if kw in hay)


def _iter_files(root: Path) -> list[str]:
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            found.append(rel)
    return found


def cmd_load(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root not found: {root}", file=sys.stderr)
        print("Pass --root to an existing directory.", file=sys.stderr)
        return 3

    keywords = _keywords(args.task)
    manifest = _load_manifest(root)
    scored: list[tuple[int, str]] = []

    if manifest:
        for entry in manifest:
            rel = entry.lstrip("./")
            full = root / rel
            if full.is_file():
                score = _score_path(rel, keywords) + 10
                scored.append((score, rel))

    for rel in _iter_files(root):
        score = _score_path(rel, keywords)
        if score > 0:
            scored.append((score, rel))

    seen: set[str] = set()
    ranked: list[str] = []
    for _, rel in sorted(scored, key=lambda x: (-x[0], x[1])):
        if rel in seen:
            continue
        seen.add(rel)
        ranked.append(rel)
        if len(ranked) >= args.limit:
            break

    payload = {
        "task": args.task,
        "root": str(root),
        "keywords": keywords,
        "count": len(ranked),
        "files": ranked,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"task: {args.task}")
        print(f"matches: {len(ranked)}")
        for rel in ranked:
            print(rel)
        if not ranked:
            print(
                "No matches. Try broader keywords or add .context/manifest.json.",
                file=sys.stderr,
            )
            return 2

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        prog="context-loader",
        description="Suggest relevant files for a task (keyword match + optional manifest).",
        epilog=(
            "Examples:\n"
            "  context-loader load --task \"spec validation\" --root .\n"
            "  context-loader load --task \"memory cli\" --json --limit 5"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    load = sub.add_parser("load", help="Suggest files for a task")
    load.add_argument("--task", required=True, help="Task description for keyword routing")
    load.add_argument("--root", default=".", help="Repository root (default: .)")
    load.add_argument("--limit", type=_positive_int, default=20, help="Max files to return, >= 1 (default: 20)")
    load.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    load.set_defaults(func=cmd_load)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Persist run-scoped markdown memory under .ai/memory/{run_id}.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CLI = Path(__file__).resolve()

# Canonical run-file sections, in schema order (.ai/memory/README.md).
SCHEMA_SECTIONS = ("## Task state", "## Decisions", "## Notes")

# Timestamp marker line as written by cmd_write.
MARKER_RE = re.compile(r"^<!-- memory write \S+ -->$")


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


def _memory_dir(root: Path) -> Path:
    # Canonical location per NEW_DIRECTION.md § Agnostic layout: memory lives in .ai/.
    return root / ".ai" / "memory"


def _memory_path(root: Path, run_id: str) -> Path:
    safe = run_id.replace("/", "_").replace("\\", "_")
    return _memory_dir(root) / f"{safe}.md"


def _resolve_content(args: argparse.Namespace) -> str:
    """Content comes from --content verbatim, or from --content-file (- = stdin).
    The shell does not turn \\n escapes into newlines; files/stdin carry real ones."""
    if args.content is not None:
        return args.content
    if args.content_file == "-":
        return sys.stdin.read()
    source = Path(args.content_file)
    if not source.is_file():
        print(f"content file not found: {source}", file=sys.stderr)
        print("Pass an existing file path, or - to read from stdin.", file=sys.stderr)
        raise SystemExit(3)
    try:
        return source.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read content file: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


def cmd_write(args: argparse.Namespace) -> int:
    content = _resolve_content(args)
    root = Path(args.root).resolve()
    path = _memory_path(root, args.run)
    path.parent.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = f"\n\n<!-- memory write {stamp} -->\n{content.rstrip()}\n"

    if path.exists() and args.append:
        path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")
        mode = "appended"
    else:
        header = f"# Run memory: {args.run}\n"
        path.write_text(header + block.lstrip(), encoding="utf-8")
        mode = "written"

    payload = {"run": args.run, "path": str(path.relative_to(root)), "mode": mode}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{mode}: {path.relative_to(root)}")
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    path = _memory_path(root, args.run)
    if not path.is_file():
        print(f"memory not found for run: {args.run}", file=sys.stderr)
        print(f"Expected: {path.relative_to(root)}", file=sys.stderr)
        print("Run: memory write --run ID --content \"...\"", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    if args.json:
        print(json.dumps({"run": args.run, "path": str(path.relative_to(root)), "content": text}))
    else:
        print(text, end="" if text.endswith("\n") else "\n")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    mem_dir = _memory_dir(root)
    runs: list[dict[str, str]] = []
    if mem_dir.is_dir():
        for path in sorted(mem_dir.glob("*.md")):
            if path.name == "README.md":  # store schema doc, not a run
                continue
            runs.append(
                {
                    "run": path.stem,
                    "path": str(path.relative_to(root)),
                    "bytes": str(path.stat().st_size),
                }
            )

    if args.json:
        print(json.dumps({"count": len(runs), "runs": runs}, indent=2))
    else:
        print(f"runs: {len(runs)}")
        for item in runs:
            print(f"{item['run']}\t{item['path']}\t{item['bytes']} bytes")
    return 0


def cmd_compact(args: argparse.Namespace) -> int:
    """Merge the duplicate section headers that --append accumulates into one
    canonical section set. Content order stays chronological (file order);
    each chunk keeps its originating timestamp marker as a sub-entry."""
    root = Path(args.root).resolve()
    path = _memory_path(root, args.run)
    if not path.is_file():
        print(f"memory not found for run: {args.run}", file=sys.stderr)
        print(f"Expected: {path.relative_to(root)}", file=sys.stderr)
        print("Run: memory list to see stored runs", file=sys.stderr)
        return 2

    lines = path.read_text(encoding="utf-8").splitlines()

    # Title: first non-empty line when it is an h1; else synthesize it.
    title = f"# Run memory: {args.run}"
    body_start = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# ") and not line.startswith("## "):
            title = line.rstrip()
            body_start = i + 1
        break

    # Attribute every content line to (section, marker). Markers precede the
    # section headers of their append block, so a marker stays current across
    # headers until the next marker; a chunk is a maximal run of content lines
    # under one (section, marker) pair. section None = content above any header.
    chunks: list[tuple[str | None, str | None, list[str]]] = []
    section: str | None = None
    marker: str | None = None
    for line in lines[body_start:]:
        stripped = line.strip()
        if MARKER_RE.match(stripped):
            marker = stripped
            continue
        if line.startswith("## "):
            section = line.rstrip()
            continue
        if chunks and chunks[-1][0] == section and chunks[-1][1] == marker:
            chunks[-1][2].append(line)
        elif stripped:
            chunks.append((section, marker, [line]))

    # Merge chunks per section, preserving file (= chronological) order.
    merged: dict[str | None, list[tuple[str | None, list[str]]]] = {}
    unknown_order: list[str] = []
    for section, marker, chunk_lines in chunks:
        while chunk_lines and not chunk_lines[-1].strip():
            chunk_lines.pop()
        if not chunk_lines:
            continue
        bucket = merged.setdefault(section, [])
        if bucket and bucket[-1][0] == marker:
            bucket[-1][1].append("")
            bucket[-1][1].extend(chunk_lines)
        else:
            bucket.append((marker, chunk_lines))
        if section is not None and section not in SCHEMA_SECTIONS and section not in unknown_order:
            unknown_order.append(section)

    out: list[str] = [title]
    emitted: list[str] = []
    for section in (None, *SCHEMA_SECTIONS, *unknown_order):
        if section not in merged:
            continue
        if section is not None:
            out.extend(["", section])
            emitted.append(section[3:])
        for marker, chunk_lines in merged[section]:
            out.append("")
            if marker is not None:
                out.append(marker)
            out.extend(chunk_lines)

    path.write_text("\n".join(out) + "\n", encoding="utf-8")

    payload = {"run": args.run, "path": str(path.relative_to(root)), "mode": "compacted", "sections": emitted}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"compacted: {path.relative_to(root)} (sections: {', '.join(emitted) if emitted else 'none'})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        prog="memory",
        description="Persist run-scoped markdown memory under .ai/memory/{run_id}.md.",
        epilog=(
            "Examples:\n"
            "  memory write --run feat-42 --content \"- context loaded\"\n"
            "  memory write --run feat-42 --append --content-file progress.md\n"
            "  memory read --run feat-42\n"
            "  memory compact feat-42\n"
            "  memory list --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", default=".", help="Repository root (default: .)")

    sub = parser.add_subparsers(dest="command", required=True)

    write = sub.add_parser("write", help="Write or replace run memory")
    write.add_argument("--run", required=True, help="Run identifier (ticket, feature name)")
    content = write.add_mutually_exclusive_group(required=True)
    content.add_argument("--content", help="Markdown content to store (verbatim; shell \\n is not a newline)")
    content.add_argument("--content-file", help="Read the markdown content from this file (- for stdin)")
    write.add_argument("--append", action="store_true", help="Append instead of replace")
    write.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    write.set_defaults(func=cmd_write)

    read = sub.add_parser("read", help="Read run memory")
    read.add_argument("--run", required=True, help="Run identifier")
    read.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    read.set_defaults(func=cmd_read)

    lst = sub.add_parser("list", help="List stored run memories")
    lst.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    lst.set_defaults(func=cmd_list)

    compact = sub.add_parser("compact", help="Merge duplicate appended sections into one canonical set")
    compact.add_argument("run", help="Run identifier")
    compact.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    compact.set_defaults(func=cmd_compact)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

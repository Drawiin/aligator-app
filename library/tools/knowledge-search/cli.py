#!/usr/bin/env python3
"""Search project knowledge: graphify index (when present) + ripgrep over knowledge roots."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

CLI = Path(__file__).resolve()

DEFAULT_ROOTS = ("references", "library/docs")
OPTIONAL_ROOTS = (".ai/knowledge", "library/knowledge")
CATEGORIES = ("rules", "procedures")
SNIPPET_MAX = 200
GRAPHIFY_NODE = re.compile(r"^NODE (.+) \[src=(\S+) loc=L(\d+)")


GRAPHIFY_HOME = "library/tools/graphify"


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
        raise argparse.ArgumentTypeError(f"{number} is < 1; pass a positive hit count, e.g. --limit 20")
    return number


def _graphify_bin(root: Path) -> str | None:
    on_path = shutil.which("graphify")
    if on_path:
        return on_path
    shim = root / GRAPHIFY_HOME / "graphify"
    return str(shim) if shim.is_file() else None


def _resolve_roots(root: Path, explicit: list[str], category: str) -> tuple[list[str], int]:
    """Return (roots relative to repo root, exit_code). exit_code 0 means OK."""
    if category:
        cat_roots = [r for base in OPTIONAL_ROOTS if (root / base / category).is_dir()
                     for r in [f"{base}/{category}"]]
        if not cat_roots:
            print(f"--category {category}: no category directory on disk", file=sys.stderr)
            print(
                "Expected library/knowledge/{rules,procedures}/ (or .ai/knowledge/{rules,procedures}/); "
                "restore it, or search without --category.",
                file=sys.stderr,
            )
            return [], 3
        return cat_roots, 0
    if explicit:
        missing = [r for r in explicit if not (root / r).is_dir()]
        if missing:
            print(f"root(s) not found: {', '.join(missing)}", file=sys.stderr)
            print("Pass --roots with directories that exist under the repo root.", file=sys.stderr)
            return [], 3
        return explicit, 0
    roots = [r for r in DEFAULT_ROOTS if (root / r).is_dir()]
    roots += [r for r in OPTIONAL_ROOTS if (root / r).is_dir()]
    return roots, 0


def _truncate(text: str) -> str:
    text = text.strip()
    return text if len(text) <= SNIPPET_MAX else text[: SNIPPET_MAX - 1] + "…"


def _within_roots(path: str, roots: list[str]) -> bool:
    """True when a repo-root-relative path falls under one of the given roots."""
    clean = PurePosixPath(path).as_posix()
    for raw in roots:
        base = PurePosixPath(raw).as_posix()
        if base == "." or clean == base or clean.startswith(base + "/"):
            return True
    return False


def _run_graphify(query: str, root: Path, roots: list[str], limit: int) -> tuple[list[dict], str]:
    graph = root / GRAPHIFY_HOME / "graphify-out" / "graph.json"
    if not graph.is_file():
        return [], f"skipped (no {GRAPHIFY_HOME}/graphify-out/graph.json)"
    binary = _graphify_bin(root)
    if not binary:
        return [], "skipped (graphify binary not found)"
    try:
        proc = subprocess.run(
            [binary, "query", query, "--graph", str(graph)],
            cwd=root, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"error ({exc})"
    if proc.returncode != 0:
        return [], f"error (exit {proc.returncode}: {_truncate(proc.stderr)})"

    hits: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for line in proc.stdout.splitlines():
        match = GRAPHIFY_NODE.match(line)
        if not match:
            continue
        title, path, lineno = match.group(1), match.group(2), int(match.group(3))
        if (path, lineno) in seen:
            continue
        # graphify searches its whole index; keep only hits inside the requested roots.
        if not _within_roots(path, roots):
            continue
        seen.add((path, lineno))
        hits.append({"path": path, "line": lineno, "snippet": _truncate(title), "source": "graphify"})
        if len(hits) >= limit:
            break
    return hits, "used"


def _run_rg(pattern: str, roots: list[str], root: Path, limit: int, per_file: int) -> tuple[list[dict], int]:
    """Return (hits, exit_code). exit_code 0/2 are fine; 1 is a real error."""
    if not shutil.which("rg"):
        print("ripgrep (rg) not found on PATH", file=sys.stderr)
        print("Install ripgrep (e.g. brew install ripgrep) to use knowledge-search.", file=sys.stderr)
        return [], 1
    if not roots:
        return [], 2
    cmd = ["rg", "-n", "--no-heading", "-S", "-m", str(per_file), pattern, *roots]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if proc.returncode == 2:
        print(f"rg failed: {_truncate(proc.stderr)}", file=sys.stderr)
        print("Check the pattern (regex) and roots, then retry.", file=sys.stderr)
        return [], 1
    hits: list[dict] = []
    for line in proc.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, lineno, content = parts
        hits.append({"path": path, "line": int(lineno), "snippet": _truncate(content), "source": "rg"})
        if len(hits) >= limit:
            break
    return hits, 0


def _merge(graphify_hits: list[dict], rg_hits: list[dict], limit: int) -> list[dict]:
    """Deterministic merge: graphify title hits fill at most floor(limit/2) slots
    so rg content hits are never fully squeezed out; rg fills the remainder, and
    leftover graphify hits backfill only when rg runs short. Dedupe on (path, line)."""
    cap = limit // 2
    merged = graphify_hits[:cap]
    seen = {(h["path"], h["line"]) for h in merged}
    for pool in (rg_hits, graphify_hits[cap:]):
        for hit in pool:
            if len(merged) >= limit:
                break
            key = (hit["path"], hit["line"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(hit)
    return merged


def _emit(payload: dict, as_json: bool, empty_hint: str) -> int:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for hit in payload["hits"]:
            print(f"{hit['source']}\t{hit['path']}:{hit['line']}\t{hit['snippet']}")
        print(f"hits: {payload['count']}")
    if not payload["hits"]:
        print(empty_hint, file=sys.stderr)
        return 2
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    tokens = [t for t in re.split(r"[^A-Za-z0-9]+", args.query) if len(t) >= 2]
    if not tokens:
        print("empty query after tokenization", file=sys.stderr)
        print("Pass at least one word of 2+ characters.", file=sys.stderr)
        return 3
    roots, code = _resolve_roots(root, args.roots, args.category)
    if code:
        return code

    graphify_hits, graphify_status = _run_graphify(args.query, root, roots, args.limit)

    pattern = "(" + "|".join(re.escape(t) for t in tokens) + ")"
    rg_hits, rg_code = _run_rg(pattern, roots, root, args.limit * 2, per_file=3)
    if rg_code == 1 and not graphify_hits:
        return 1
    # Rank rg hits by how many distinct query tokens the line contains.
    for hit in rg_hits:
        low = hit["snippet"].lower()
        hit["_score"] = sum(1 for t in tokens if t.lower() in low)
    rg_hits.sort(key=lambda h: (-h["_score"], h["path"], h["line"]))
    for hit in rg_hits:
        del hit["_score"]

    merged = _merge(graphify_hits, rg_hits, args.limit)

    payload = {
        "query": args.query,
        "roots": roots,
        "graphify": graphify_status,
        "count": len(merged),
        "hits": merged,
    }
    return _emit(payload, args.json, "No hits. Reformulate the query or broaden --roots.")


def cmd_grep(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    roots, code = _resolve_roots(root, args.roots, args.category)
    if code:
        return code
    hits, rg_code = _run_rg(args.pattern, roots, root, args.limit, per_file=5)
    if rg_code == 1:
        return 1
    payload = {"pattern": args.pattern, "roots": roots, "count": len(hits), "hits": hits}
    return _emit(payload, args.json, "No hits. Loosen the pattern or broaden --roots.")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        prog="knowledge-search",
        description="Search project knowledge: graphify index (when present) + ripgrep over knowledge roots.",
        epilog=(
            "Examples:\n"
            "  knowledge-search search \"context engineering\"\n"
            "  knowledge-search search \"tool manifest\" --json --limit 10\n"
            "  knowledge-search grep \"Independent Judge\" --roots library/knowledge\n"
            "  knowledge-search search \"exit codes\" --category rules\n"
            "  knowledge-search search \"add a tool\" --category procedures --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", default=".", help="Repository root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    common = {
        "--roots": dict(nargs="*", default=[], help="Knowledge roots relative to repo root "
                        f"(default: {', '.join(DEFAULT_ROOTS)} + {', '.join(OPTIONAL_ROOTS)} when present)"),
        "--category": dict(default="", choices=("", *CATEGORIES),
                           help="Restrict to a knowledge category: searches library/knowledge/<category>/ "
                                "(and .ai/knowledge/<category>/ when present)"),
        "--limit": dict(type=_positive_int, default=20, help="Max hits to return, >= 1 (default: 20)"),
        "--json": dict(action="store_true", help="Emit JSON on stdout"),
    }

    search = sub.add_parser("search", help="Combined graphify + ripgrep search")
    search.add_argument("query", help="Task-relevant question or keywords")
    for flag, kwargs in common.items():
        search.add_argument(flag, **kwargs)
    search.set_defaults(func=cmd_search)

    grep = sub.add_parser("grep", help="Targeted ripgrep over knowledge roots")
    grep.add_argument("pattern", help="Regex pattern (rg syntax, smart-case)")
    for flag, kwargs in common.items():
        grep.add_argument(flag, **kwargs)
    grep.set_defaults(func=cmd_grep)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

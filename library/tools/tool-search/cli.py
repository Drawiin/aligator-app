#!/usr/bin/env python3
"""Search harness tools by indexing library/tools/*/tool.json manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLI = Path(__file__).resolve()

TYPES = ("research", "execution", "both", "inference")

# Deterministic scoring weights: tag exact match outranks name hits,
# which outrank when_to_use / helps_with keyword hits, which outrank
# description hits. Ties break alphabetically by tool name.
W_TAG = 10
W_NAME = 8
W_WHEN = 5
W_HELPS = 4
W_DESC = 2

# Weak-match threshold (T-06 friction fix): real matches observed at ~25-45,
# coincidental keyword hits at 2-8. Below 15 a hit cannot combine two
# meaningful signals (e.g. tag 10 + when_to_use 5); even a lone exact tag
# match (10) stays weak. When the TOP hit scores under this, the envelope
# gains weak_match + note so the caller knows "no relevant tool" is a
# legitimate answer. Exit codes are unaffected.
WEAK_MATCH_THRESHOLD = 15


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
        raise argparse.ArgumentTypeError(f"{number} is < 1; pass a positive hit count, e.g. --limit 5")
    return number


def _tools_root() -> Path:
    return CLI.parent.parent


def _guide_path(tool_dir: Path) -> str:
    # Absolute paths so hits resolve regardless of the caller's cwd
    # (NEW_DIRECTION.md § Constraints: always use absolute paths).
    for name in ("USAGE.md", "README.md"):
        candidate = tool_dir / name
        if candidate.is_file():
            return str(candidate.resolve())
    return ""


def _load_manifests(tools_root: Path) -> tuple[list[dict], list[dict]]:
    """Return (manifests, skipped). skipped records dirs whose tool.json is
    missing or unparseable, so JSON consumers can see the catalog is incomplete."""
    manifests: list[dict] = []
    skipped: list[dict] = []
    for tool_dir in sorted(p for p in tools_root.iterdir() if p.is_dir()):
        path = tool_dir / "tool.json"
        if not path.is_file():
            print(f"note: no tool.json in {tool_dir.name}; not searchable", file=sys.stderr)
            skipped.append({"name": tool_dir.name, "path": str(path), "reason": "no tool.json manifest"})
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skipping {path}: {exc}", file=sys.stderr)
            print("Fix the manifest JSON so this tool is searchable.", file=sys.stderr)
            skipped.append({"name": tool_dir.name, "path": str(path), "reason": str(exc)})
            continue
        data["_guide"] = _guide_path(tool_dir)
        manifests.append(data)
    return manifests, skipped


def _tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 2]


def _word_match(token: str, text: str) -> bool:
    """Whole-word match so e.g. token "for" does not match inside "before"."""
    return re.search(rf"\b{re.escape(token)}\b", text) is not None


def _score(manifest: dict, tokens: list[str]) -> tuple[int, list[str]]:
    tags = [str(t).lower() for t in manifest.get("tags", [])]
    name = str(manifest.get("name", "")).lower()
    when = " ".join(str(w).lower() for w in manifest.get("when_to_use", []))
    helps = str(manifest.get("helps_with", "")).lower()
    desc = str(manifest.get("description", "")).lower()

    score = 0
    matched: list[str] = []
    for token in tokens:
        if token in tags:
            score += W_TAG
            matched.append(f"tag:{token}")
        if _word_match(token, name):
            score += W_NAME
            matched.append(f"name:{token}")
        if _word_match(token, when):
            score += W_WHEN
            matched.append(f"when_to_use:{token}")
        if _word_match(token, helps):
            score += W_HELPS
            matched.append(f"helps_with:{token}")
        if _word_match(token, desc):
            score += W_DESC
            matched.append(f"description:{token}")
    return score, matched


def _hit(manifest: dict, score: int = 0, matched: list[str] | None = None) -> dict:
    hit = {
        "name": manifest.get("name", ""),
        "type": manifest.get("type", ""),
        "description": manifest.get("description", ""),
        "guide": manifest.get("_guide", ""),
    }
    if matched is not None:
        hit["score"] = score
        hit["matched"] = matched
    else:
        hit["tags"] = manifest.get("tags", [])
    return hit


def cmd_list(args: argparse.Namespace) -> int:
    manifests, skipped = _load_manifests(_tools_root())
    items = [_hit(m) for m in manifests]
    if args.json:
        print(json.dumps({"count": len(items), "tools": items, "skipped": skipped}, indent=2))
    else:
        print(f"tools: {len(items)}")
        for item in items:
            print(f"{item['name']}\t[{item['type']}]\t{item['description']}")
    if not manifests and skipped:
        print("No loadable tool.json manifests; fix the manifest errors above.", file=sys.stderr)
        return 1
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    tokens = _tokens(args.query)
    if not tokens:
        print("empty query after tokenization", file=sys.stderr)
        print("Pass at least one word of 2+ characters, e.g.: search \"run tests\"", file=sys.stderr)
        return 3
    if args.type and args.type not in TYPES:
        print(f"invalid --type: {args.type}", file=sys.stderr)
        print(f"Use one of: {', '.join(TYPES)}", file=sys.stderr)
        return 3
    wanted_tags = {t.strip().lower() for t in args.tags.split(",") if t.strip()} if args.tags else set()

    manifests, skipped = _load_manifests(_tools_root())
    hits: list[dict] = []
    for manifest in manifests:
        if args.type and manifest.get("type") != args.type:
            continue
        if wanted_tags and not wanted_tags & {str(t).lower() for t in manifest.get("tags", [])}:
            continue
        score, matched = _score(manifest, tokens)
        if score > 0:
            hits.append(_hit(manifest, score, matched))

    hits.sort(key=lambda h: (-h["score"], h["name"]))
    hits = hits[: args.limit]

    envelope: dict = {"query": args.query, "count": len(hits), "hits": hits, "skipped": skipped}
    if hits and hits[0]["score"] < WEAK_MATCH_THRESHOLD:
        envelope["weak_match"] = True
        envelope["note"] = (
            f"Top score {hits[0]['score']} is below the strong-match threshold ({WEAK_MATCH_THRESHOLD}): "
            "no strong match exists; 'no relevant tool' is a legitimate answer."
        )

    if args.json:
        print(json.dumps(envelope, indent=2))
    else:
        print(f"query: {args.query}")
        print(f"hits: {len(hits)}")
        for hit in hits:
            print(f"{hit['name']}\t{hit['score']}\t{','.join(hit['matched'])}\t{hit['guide']}")
        if envelope.get("weak_match"):
            print(f"weak match: {envelope['note']}")

    if not hits:
        print("No tools matched. Reformulate the query, drop --tags/--type,", file=sys.stderr)
        print("or run: tool-search list", file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        prog="tool-search",
        description="List and search harness tools by indexing library/tools/*/tool.json manifests.",
        epilog=(
            "Examples:\n"
            "  tool-search list\n"
            "  tool-search search \"save task state\" --json\n"
            "  tool-search search \"run tests\" --tags gradle,testing --limit 3\n"
            "  tool-search search \"summarize\" --type inference"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    lst = sub.add_parser("list", help="List all tools that have a tool.json manifest")
    lst.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    lst.set_defaults(func=cmd_list)

    search = sub.add_parser("search", help="Rank tools against a task query")
    search.add_argument("query", help="Task description or keywords")
    search.add_argument("--tags", default="", help="Comma-separated tags; keep tools matching any")
    search.add_argument("--type", default="", help=f"Filter by type: {' | '.join(TYPES)}")
    search.add_argument("--limit", type=_positive_int, default=5, help="Max hits to return, >= 1 (default: 5)")
    search.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    search.set_defaults(func=cmd_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

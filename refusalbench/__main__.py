"""refusal-bench: measure how often a model refuses legitimate coding tasks.

Usage:
    export TARTARUS_TOKEN=...
    python -m refusalbench --endpoint https://api.tartarusai.dev/v1 --model tartarus-coder
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .classify import classify
from .runner import ApiError, complete

DEFAULT_PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "over_refusal.jsonl"


def load_prompts(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="refusal-bench")
    ap.add_argument("--endpoint", default="https://api.tartarusai.dev/v1")
    ap.add_argument("--model", default="tartarus-coder")
    ap.add_argument("--token", default=os.environ.get("TARTARUS_TOKEN", ""))
    ap.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--out", type=Path, help="write a Markdown scoreboard here")
    args = ap.parse_args(argv)

    if not args.token:
        print("error: no token (pass --token or set TARTARUS_TOKEN)", file=sys.stderr)
        return 2

    prompts = load_prompts(args.prompts)
    refused = 0
    rows = []

    for i, item in enumerate(prompts, 1):
        try:
            reply = complete(
                endpoint=args.endpoint,
                model=args.model,
                token=args.token,
                prompt=item["prompt"],
                max_tokens=args.max_tokens,
            )
        except ApiError as e:
            print(f"[{i:2}/{len(prompts)}] ERROR {item['id']}: {e}", file=sys.stderr)
            rows.append((item, "error", None))
            continue

        verdict = classify(reply)
        if verdict.refused:
            refused += 1
        status = "REFUSED" if verdict.refused else "ok"
        print(f"[{i:2}/{len(prompts)}] {status:8} {item['id']}  ({item['category']})")
        rows.append((item, status, verdict.phrase))

    total = len(prompts)
    rate = (refused / total * 100) if total else 0.0
    print("-" * 48)
    print(f"{args.model}: {refused}/{total} refused  ({rate:.1f}% refusal rate)")

    if args.out:
        write_markdown(args.out, args.model, rows, refused, total, rate)
        print(f"wrote {args.out}")

    return 0


def write_markdown(path, model, rows, refused, total, rate) -> None:
    lines = [
        f"# Refusal scoreboard: `{model}`",
        "",
        f"**{refused}/{total} refused ({rate:.1f}%)**",
        "",
        "| # | id | category | verdict |",
        "|---|---|---|---|",
    ]
    for i, (item, status, phrase) in enumerate(rows, 1):
        note = f" ({phrase})" if phrase else ""
        lines.append(f"| {i} | {item['id']} | {item['category']} | {status}{note} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

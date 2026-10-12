"""Machine-readable context recovery entry point."""

from __future__ import annotations

import argparse
import json

from .snapshot import build_context_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit a compact, read-only Gnozis context handoff"
    )
    parser.add_argument("--root", default=".", help="project checkout root")
    parser.add_argument(
        "--include-source-documents",
        action="store_true",
        help="include full canonical documents for debugging (opt-in)",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            build_context_snapshot(
                args.root,
                include_source_documents=args.include_source_documents,
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

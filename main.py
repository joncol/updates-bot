#!/usr/bin/env python3
"""Changelog reporter — posts a summary of new changelog entries to Slack."""

import argparse
from datetime import datetime, timedelta

from changelog_parser import collect_entries
from slack_reporter import build_blocks, post_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Post changelog report to Slack")
    parser.add_argument(
        "--since",
        help="ISO date to look back from (default: 7 days ago)",
    )
    parser.add_argument(
        "--author",
        help="Filter commits by author (name or email). Default: current git user",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Slack message instead of posting it",
    )
    args = parser.parse_args()

    since = args.since or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    entries_by_section = collect_entries(since, author=args.author)

    if args.dry_run:
        import json

        blocks = build_blocks(entries_by_section, since)
        print(json.dumps(blocks, indent=2))
        print()
        total = sum(len(v) for v in entries_by_section.values())
        print(f"Found {total} entries across {len(entries_by_section)} sections.")
    else:
        post_report(entries_by_section, since)
        total = sum(len(v) for v in entries_by_section.values())
        print(f"Posted report with {total} entries to Slack.")


if __name__ == "__main__":
    main()

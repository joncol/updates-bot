"""Format changelog entries as Slack Block Kit messages and post them."""

from slack_sdk import WebClient

import config
from changelog_parser import ChangelogEntry


def build_blocks(
    entries_by_section: dict[str, list[ChangelogEntry]],
    since: str,
) -> list[dict]:
    """Build Slack Block Kit blocks from grouped changelog entries."""
    blocks: list[dict] = []

    # Header
    blocks.append(
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Changelog Report (since {since})",
            },
        }
    )

    if not entries_by_section:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No new changelog entries found.",
                },
            }
        )
        return blocks

    # Highlight banner if there are important sections
    highlight_sections_present = [
        s for s in config.HIGHLIGHT_SECTIONS if s in entries_by_section
    ]
    if highlight_sections_present:
        labels = [config.SECTION_LABELS.get(s, s) for s in highlight_sections_present]
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":warning: *Heads up — this report includes: {', '.join(labels)}*",
                },
            }
        )
        blocks.append({"type": "divider"})

    # Sections in display order
    for section_key in config.SECTION_DISPLAY_ORDER:
        entries = entries_by_section.get(section_key)
        if not entries:
            continue

        label = config.SECTION_LABELS.get(section_key, section_key)
        is_highlight = section_key in config.HIGHLIGHT_SECTIONS
        section_header = f":rotating_light: *{label}*" if is_highlight else f"*{label}*"

        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": section_header},
            }
        )

        lines = []
        for entry in entries:
            tag_prefix = f"<https://scriveab.atlassian.net/browse/{entry.tag}|[{entry.tag}]> " if entry.tag else ""
            lines.append(f"• {tag_prefix}{entry.title}")
            if entry.description:
                # Indent description under the bullet
                for desc_line in entry.description.strip().splitlines():
                    lines.append(f"    {desc_line}")
        text = "\n".join(lines)

        # Slack blocks have a 3000 char limit per text field
        while text:
            chunk, text = text[:3000], text[3000:]
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": chunk},
                }
            )

    # Summary count
    total = sum(len(v) for v in entries_by_section.values())
    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{total} changelog {'entry' if total == 1 else 'entries'} across {len(entries_by_section)} {'section' if len(entries_by_section) == 1 else 'sections'}",
                }
            ],
        }
    )

    return blocks


def post_report(
    entries_by_section: dict[str, list[ChangelogEntry]],
    since: str,
) -> None:
    """Post the changelog report to Slack."""
    if not config.SLACK_BOT_TOKEN:
        raise RuntimeError("SLACK_BOT_TOKEN environment variable is required to post")
    client = WebClient(token=config.SLACK_BOT_TOKEN)
    blocks = build_blocks(entries_by_section, since)

    client.chat_postMessage(
        channel=config.SLACK_CHANNEL,
        text=f"Changelog Report (since {since})",
        blocks=blocks,
    )

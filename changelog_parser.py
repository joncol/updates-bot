"""Parse changelog YAML files added since a given date using git history."""

import pathlib
import subprocess
from dataclasses import dataclass

import yaml

import config


@dataclass
class ChangelogEntry:
    section: str
    title: str
    description: str | None
    source_file: str
    tag: str | None


def get_new_changelog_files(since: str) -> list[str]:
    """Return changelog .yaml filenames added since `since` (ISO date or git ref).

    Uses git log on the kontrakcja repo to find newly added files.
    """
    result = subprocess.run(
        [
            "git",
            "log",
            "master",
            f"--since={since}",
            "--diff-filter=A",
            "--name-only",
            "--pretty=format:",
            "--",
            "doc/changelog.d/*.yaml",
        ],
        cwd=config.KONTRAKCJA_REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(set(files))


def parse_changelog_file(filepath: pathlib.Path) -> list[ChangelogEntry]:
    """Parse a single changelog YAML file, returning one entry per document."""
    entries = []
    with open(filepath) as f:
        for record in yaml.safe_load_all(f):
            if record is None:
                continue
            record_type = record.get("type", "issue")
            if record_type not in ("issue", None):
                # Skip summaries — we only report issues
                continue
            section = record.get("section")
            title = record.get("title")
            if not section or not title:
                continue
            tag = _tag_from_filename(filepath.name)
            entries.append(
                ChangelogEntry(
                    section=section,
                    title=title,
                    description=record.get("description"),
                    source_file=filepath.name,
                    tag=tag,
                )
            )
    return entries


def _tag_from_filename(filename: str) -> str | None:
    """Derive a tag like CORE-8650 or PR-9002 from the filename."""
    stem = pathlib.Path(filename).stem
    parts = stem.split("-", 1)
    if len(parts) == 2:
        prefix, number = parts
        if number.isdigit():
            return f"{prefix.upper()}-{number}"
    return stem.upper()


def collect_entries(since: str) -> dict[str, list[ChangelogEntry]]:
    """Collect all new changelog entries since `since`, grouped by section."""
    changelog_dir = pathlib.Path(config.CHANGELOG_DIR)
    new_files = get_new_changelog_files(since)

    entries_by_section: dict[str, list[ChangelogEntry]] = {}
    included_sections = set(config.SECTION_DISPLAY_ORDER)
    for rel_path in new_files:
        filepath = pathlib.Path(config.KONTRAKCJA_REPO) / rel_path
        if not filepath.exists():
            continue
        for entry in parse_changelog_file(filepath):
            if entry.section in included_sections:
                entries_by_section.setdefault(entry.section, []).append(entry)

    return entries_by_section

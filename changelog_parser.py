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
    author: str | None


def get_new_changelog_files(since: str, author: str | None = None) -> dict[str, str]:
    """Return a mapping of changelog .yaml relative paths to their commit author.

    Uses git log on the kontrakcja repo to find newly added files.
    If *author* is given, only commits by that author are considered.
    """
    cmd = [
        "git",
        "log",
        "master",
        f"--since={since}",
        "--diff-filter=A",
        "--name-only",
        "--pretty=format:COMMIT_AUTHOR:%aN",
    ]
    if author:
        cmd.append(f"--author={author}")
    cmd += [
        "--",
        "doc/changelog.d/*.yaml",
    ]
    result = subprocess.run(
        cmd,
        cwd=config.KONTRAKCJA_REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    file_to_author: dict[str, str] = {}
    current_author = ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("COMMIT_AUTHOR:"):
            current_author = line.removeprefix("COMMIT_AUTHOR:")
        elif line not in file_to_author:
            file_to_author[line] = current_author
    return file_to_author


def read_file_from_git(rel_path: str) -> str | None:
    """Read file content from the latest master commit that introduced it."""
    result = subprocess.run(
        [
            "git",
            "log",
            "master",
            "-1",
            "--diff-filter=A",
            "--pretty=format:%H",
            "--",
            rel_path,
        ],
        cwd=config.KONTRAKCJA_REPO,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if not commit:
        return None
    result = subprocess.run(
        ["git", "show", f"{commit}:{rel_path}"],
        cwd=config.KONTRAKCJA_REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def parse_changelog_yaml(
    content: str, filename: str, author: str | None = None
) -> list[ChangelogEntry]:
    """Parse changelog YAML content, returning one entry per document."""
    entries = []
    for record in yaml.safe_load_all(content):
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
        tag = _tag_from_filename(filename)
        entries.append(
            ChangelogEntry(
                section=section,
                title=title,
                description=record.get("description"),
                source_file=filename,
                tag=tag,
                author=author,
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


def collect_entries(
    since: str, author: str | None = None
) -> dict[str, list[ChangelogEntry]]:
    """Collect all new changelog entries since `since`, grouped by section."""
    file_to_author = get_new_changelog_files(since, author=author)

    entries_by_section: dict[str, list[ChangelogEntry]] = {}
    included_sections = set(config.SECTION_DISPLAY_ORDER)
    for rel_path, commit_author in file_to_author.items():
        filepath = pathlib.Path(config.KONTRAKCJA_REPO) / rel_path
        if filepath.exists():
            content = filepath.read_text()
        else:
            content = read_file_from_git(rel_path)
        if content is None:
            continue
        filename = pathlib.Path(rel_path).name
        for entry in parse_changelog_yaml(content, filename, author=commit_author):
            if entry.section in included_sections:
                entries_by_section.setdefault(entry.section, []).append(entry)

    return entries_by_section

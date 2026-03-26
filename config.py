import os

# Path to the kontrakcja changelog directory (relative to this repo or absolute)
CHANGELOG_DIR = os.environ.get(
    "CHANGELOG_DIR",
    os.path.join(os.path.dirname(__file__), "..", "kontrakcja", "doc", "changelog.d"),
)

# Path to the kontrakcja repo root (for git operations)
KONTRAKCJA_REPO = os.environ.get(
    "KONTRAKCJA_REPO",
    os.path.join(os.path.dirname(__file__), "..", "kontrakcja"),
)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#updates")

# Sections considered "highlight-worthy" — shown with extra emphasis
HIGHLIGHT_SECTIONS = {
    "breaking_api",
    "migrations",
    "configuration",
    "rollout_flags",
    "feature_flags",
}

# Sections to include in the report, in display order
SECTION_DISPLAY_ORDER = [
    "breaking_api",
    "migrations",
    "configuration",
    "rollout_flags",
    "feature_flags",
    "esign",
    "revert",
    "validation",
    "bugfix",
]

SECTION_LABELS = {
    "breaking_api": "Breaking API Changes",
    "migrations": "Migrations",
    "configuration": "Configuration",
    "rollout_flags": "Rollout Flags",
    "feature_flags": "Feature Flags",
    "esign": "eSign",
    "revert": "Reverts",
    "validation": "Validation",
    "bugfix": "Bugfixes",
}

#!/usr/bin/env python3
"""
SpecKit helper script.

Use this to verify local tooling and get quick instructions for the
immersive SpecKit + OpenSpec workflow.
"""

from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECKIT_DIR = REPO_ROOT / ".speckit"
OPEN_SPEC_DIR = REPO_ROOT / "openspec"
DOC_PATH = REPO_ROOT / "docs" / "spec-kit.md"


def heading(title: str) -> None:
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def check_paths() -> None:
    heading("Directory Layout")
    missing = []

    if SPECKIT_DIR.exists():
        print(f"✅ .speckit directory found at {SPECKIT_DIR}")
        commands = list((SPECKIT_DIR / "commands").glob("*.md"))
        print(f"   ├─ command templates: {len(commands)} files")
        templates = list((SPECKIT_DIR / "templates").glob("*"))
        print(f"   └─ supporting templates: {len(templates)} files")
    else:
        print("❌ .speckit directory is missing")
        missing.append(".speckit/")

    if OPEN_SPEC_DIR.exists():
        changes = OPEN_SPEC_DIR / "changes"
        specs = OPEN_SPEC_DIR / "specs"
        print(f"✅ OpenSpec directory found at {OPEN_SPEC_DIR}")
        print(f"   ├─ active changes: {len(list(changes.glob('*')))} folders")
        print(f"   └─ published specs: {len(list(specs.glob('*')))} folders")
    else:
        print("❌ openspec directory is missing")
        missing.append("openspec/")

    if DOC_PATH.exists():
        print(f"✅ SpecKit guide available: {DOC_PATH.relative_to(REPO_ROOT)}")
    else:
        print("⚠️  SpecKit guide not found (docs/spec-kit.md)")

    if missing:
        print("\nTo bootstrap SpecKit run:")
        print("  mkdir -p .speckit/commands .speckit/templates")
        print("  # copy templates from spec-kit repo or download release bundle")


def check_tooling() -> None:
    heading("Tooling Check")

    python_version = sys.version.split()[0]
    print(f"• Current Python: {python_version} ({platform.system()})")
    if sys.version_info < (3, 11):
        print("  - SpecKit CLI needs Python ≥ 3.11 (consider using `uv` or `pipx`)")
    else:
        print("  - Meets SpecKit CLI requirement (≥ 3.11)")

    for tool in ("uv", "uvx", "pipx"):
        available = shutil.which(tool) is not None
        status = "✅" if available else "⚠️"
        print(f"{status} {tool} {'found' if available else 'not detected'}")
        if not available and tool == "uv":
            print("   install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        if not available and tool == "pipx":
            print("   install with: python3 -m pip install --user pipx && pipx ensurepath")


def suggested_commands() -> None:
    heading("Suggested Next Commands")

    suggestions = [
        ("Constitution", "/speckit.constitution", ".speckit/constitution.md"),
        ("Specify feature", "/speckit.specify", "openspec/changes/<change>/specs/.../spec.md"),
        ("Plan feature", "/speckit.plan", "openspec/changes/<change>/proposal.md"),
        ("Create tasks", "/speckit.tasks", "openspec/changes/<change>/tasks.md"),
        ("Quality checklist", "/speckit.checklist", "openspec/changes/<change>/checklists/requirements.md"),
    ]

    for label, command, target in suggestions:
        print(f"- {label:<18} → run {command:<20} → update {target}")

    print("\nFull guide: docs/spec-kit.md")
    print("OpenSpec primer: openspec/AGENTS.md")


def main() -> None:
    heading("SpecKit Helper")
    check_paths()
    check_tooling()
    suggested_commands()


if __name__ == "__main__":
    main()

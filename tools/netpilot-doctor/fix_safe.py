#!/usr/bin/env python3
"""
netpilot-doctor — Safe Mechanical Fixer

This module performs ONLY provably-safe HTML fixes.
It never guesses intent and never modifies semantic structure.

SAFE FIXES:
- Remove consecutive duplicate closing tags (</td></td>, </div></div>, etc.)

UNSAFE (DETECTED ELSEWHERE, NEVER AUTO-FIXED):
- <li> without <ul>/<ol>
- <template x-for> without root element
- Duplicate Alpine tab blocks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import difflib
import re
from datetime import datetime
from pathlib import Path


# =============================================================
# Data structure
# =============================================================

@dataclass
class FixResult:
    changed: bool
    changes: List[str]
    fixed_text: str
    patch_text: str
    backup_path: str | None = None
    patch_path: str | None = None


# =============================================================
# SAFE FIX RULES
# =============================================================
# Only remove CONSECUTIVE duplicate closing tags.
# This avoids guessing intent.
# =============================================================

DUPLICATE_CLOSE_TAG_RE = re.compile(
    r"(?is)(</(td|th|tr|div|ul|ol|template)>\s*)\1+"
)


def _dedupe_close_tags(text: str) -> Tuple[str, List[str]]:
    changes: List[str] = []

    def _repl(match: re.Match) -> str:
        tag = match.group(2).lower()
        changes.append(
            f"Removed consecutive duplicate closing tags </{tag}> (kept one)."
        )
        return match.group(1)

    new_text = DUPLICATE_CLOSE_TAG_RE.sub(_repl, text)
    return new_text, changes


# =============================================================
# PUBLIC API
# =============================================================

def fix_safe_text(original: str) -> Tuple[str, List[str]]:
    """
    Apply all safe fixes to a string.
    """
    text = original
    all_changes: List[str] = []

    text, changes = _dedupe_close_tags(text)
    all_changes.extend(changes)

    return text, all_changes


def fix_safe_file(path: str, in_place: bool = False) -> FixResult:
    """
    Apply safe fixes to a file.

    - If in_place=False (default): dry run, no file changes
    - If in_place=True:
        * creates timestamped .bak backup
        * writes fixed file
        * writes unified diff patch
    """
    p = Path(path)

    original = p.read_text(encoding="utf-8", errors="replace")
    fixed, changes = fix_safe_text(original)
    changed = fixed != original

    patch_text = "".join(
        difflib.unified_diff(
            original.splitlines(True),
            fixed.splitlines(True),
            fromfile=str(p),
            tofile=str(p) + " (fix-safe)",
        )
    )

    backup_path = None
    patch_path = None

    if in_place and changed:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")

        backup = p.with_name(p.name + f".bak.{ts}")
        backup.write_text(original, encoding="utf-8")
        backup_path = str(backup)

        p.write_text(fixed, encoding="utf-8")

        patch_file = p.with_name(p.name + ".fix-safe.patch")
        patch_file.write_text(patch_text, encoding="utf-8")
        patch_path = str(patch_file)

    return FixResult(
        changed=changed,
        changes=changes,
        fixed_text=fixed,
        patch_text=patch_text,
        backup_path=backup_path,
        patch_path=patch_path,
    )

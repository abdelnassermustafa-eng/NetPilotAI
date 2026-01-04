#!/usr/bin/env python3
"""
netpilot-doctor — Semantic HTML Inspector (READ-ONLY)

Detects semantic HTML issues that break Alpine.js and DOM structure.
This tool NEVER modifies files.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path


# =============================================================
# Data model
# =============================================================

@dataclass
class Finding:
    code: str
    severity: str  # error | warn | info
    line: int
    message: str
    excerpt: str = ""


# =============================================================
# Utilities
# =============================================================

def _line_of_index(text: str, idx: int) -> int:
    return text.count("\n", 0, max(idx, 0)) + 1


def _excerpt_around(text: str, idx: int, radius: int = 120) -> str:
    start = max(0, idx - radius)
    end = min(len(text), idx + radius)
    return text[start:end].replace("\n", "\\n")


def effective_parent(stack: List[Tuple[str, int, int]]) -> Optional[str]:
    """
    Return the nearest non-template parent.

    Alpine <template> is render-time only and should be
    transparent for semantic validation.
    """
    for tag, _, _ in reversed(stack):
        if tag != "template":
            return tag
    return None


# =============================================================
# Lightweight semantic inspection
# =============================================================

TAG_RE = re.compile(
    r"(?is)<\s*(/)?\s*([a-zA-Z][a-zA-Z0-9:_-]*)\b([^>]*)>",
    re.MULTILINE,
)

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def semantic_inspect(html: str) -> List[Finding]:
    findings: List[Finding] = []
    stack: List[Tuple[str, int, int]] = []

    template_xfor_stack: List[Tuple[int, int]] = []
    template_root_seen: List[bool] = []

    for m in TAG_RE.finditer(html):
        is_close = bool(m.group(1))
        tag = m.group(2).lower()
        attrs = m.group(3) or ""
        idx = m.start()
        line = _line_of_index(html, idx)

        if tag.startswith("!") or tag.startswith("?"):
            continue

        self_closing = (
            tag in VOID_TAGS or
            (not is_close and m.group(0).strip().endswith("/>"))
        )

        if not is_close:
            parent = effective_parent(stack)

            # ---------- Alpine-aware rules ----------

            if tag == "li" and parent not in ("ul", "ol"):
                findings.append(Finding(
                    "SEM.LI_PARENT", "error", line,
                    f"<li> must be inside <ul>/<ol> (parent={parent})",
                    _excerpt_around(html, idx),
                ))

            if tag == "td" and parent != "tr":
                findings.append(Finding(
                    "SEM.TD_PARENT", "error", line,
                    f"<td> must be inside <tr> (parent={parent})",
                    _excerpt_around(html, idx),
                ))

            # ---------- template / x-for handling ----------

            if tag == "template" and "x-for" in attrs:
                template_xfor_stack.append((idx, line))
                template_root_seen.append(False)

            elif template_xfor_stack and tag != "template":
                if not template_root_seen[-1]:
                    template_root_seen[-1] = True

            if not self_closing:
                stack.append((tag, line, idx))

        else:
            if tag == "template" and template_xfor_stack:
                start_idx, start_line = template_xfor_stack.pop()
                root_seen = template_root_seen.pop()
                if not root_seen:
                    findings.append(Finding(
                        "SEM.TEMPLATE_XFOR_NO_ROOT", "error", start_line,
                        "<template x-for> has no root element (wrap content in a <div>)",
                        _excerpt_around(html, start_idx),
                    ))

            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    stack = stack[:i]
                    break
            else:
                findings.append(Finding(
                    "SEM.ORPHAN_CLOSE", "warn", line,
                    f"Closing </{tag}> has no matching opener",
                    _excerpt_around(html, idx),
                ))

    return findings


# =============================================================
# CLI
# =============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Semantic HTML inspector (read-only)"
    )
    parser.add_argument("file", help="HTML file to inspect")
    args = parser.parse_args()

    html = Path(args.file).read_text(encoding="utf-8", errors="replace")
    findings = semantic_inspect(html)

    if not findings:
        print("✅ Semantic inspector: no issues found.")
        return 0

    print("🔎 Semantic inspector findings:")
    for f in findings:
        print(f"- {f.severity.upper()} {f.code} @ line {f.line}: {f.message}")

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

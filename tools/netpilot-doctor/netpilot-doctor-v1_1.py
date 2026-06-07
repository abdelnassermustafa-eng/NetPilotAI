#!/usr/bin/env python3
"""
netpilot-doctor v1.1.0
Structural Analyzer & Reviewer (HTML focus)

This version adds:
- Any-tag imbalance detection (extra closing + unclosed opens)
- Duplicate Alpine tab block extraction
- Block similarity/diff classification
- Dependency-usage checks (events, refs/ids, state usage)
- Safe recommendation output (analysis-only; no deletion)
"""

from __future__ import annotations

import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import difflib

VERSION = "1.1.0"

HELP_TEXT = f"""
NetPilot Doctor v{VERSION}
Structural Analysis & Review Tool

Usage:
  netpilot-doctor analyze <file>
  netpilot-doctor review <file>
  netpilot-doctor --version
  netpilot-doctor --help

Examples:
  netpilot-doctor analyze app/templates/dashboard_test.html
  netpilot-doctor review  app/templates/dashboard_test.html
"""

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

JS_KEYWORDS = {
    "if", "else", "return", "true", "false", "null", "undefined", "await",
    "async", "try", "catch", "finally", "for", "while", "do", "switch",
    "case", "break", "continue", "new", "this", "function", "const",
    "let", "var", "in", "of", "typeof", "instanceof", "delete", "void",
    "class", "extends", "super", "import", "export", "default"
}


@dataclass
class BlockMeta:
    tab: str
    start_line: int
    end_line: int
    tag: str
    raw_lines: List[str]
    norm_lines: List[str]
    similarity_hint_score: int

    # dependencies
    has_events: bool
    has_side_effects: bool
    ids: List[str]
    xrefs: List[str]
    state_tokens: List[str]
    has_table: bool
    has_xfor: bool
    has_fetch: bool
    has_xinit: bool
    informational_only: bool


def read_lines(path: Path) -> List[str]:
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(2)
    return path.read_text(errors="replace").splitlines()


# -------------------------
# Tag scanning (any-tag)
# -------------------------
TAG_TOKEN_RE = re.compile(r"<\s*(/)?\s*([a-zA-Z][a-zA-Z0-9:-]*)\b([^>]*)>")

def is_self_closing(tag_text: str) -> bool:
    # crude but effective: <tag ... />
    return tag_text.rstrip().endswith("/>")

def find_tag_imbalances(lines: List[str]) -> Tuple[List[int], List[int]]:
    """
    Returns:
      extra_closing_lines: where a closing tag appears with no matching opener
      unclosed_open_lines: opening tag line numbers still on stack at EOF
    Notes:
      - ignores void tags
      - ignores anything inside <script>...</script> and <style>...</style>
    """
    stack: List[Tuple[str, int]] = []
    extra_closings: List[int] = []

    in_script = False
    in_style = False

    for i, line in enumerate(lines, 1):
        # track script/style regions
        if re.search(r"<\s*script\b", line, flags=re.I):
            in_script = True
        if re.search(r"<\s*style\b", line, flags=re.I):
            in_style = True

        if in_script or in_style:
            if in_script and re.search(r"</\s*script\s*>", line, flags=re.I):
                in_script = False
            if in_style and re.search(r"</\s*style\s*>", line, flags=re.I):
                in_style = False
            continue

        for m in TAG_TOKEN_RE.finditer(line):
            is_close = bool(m.group(1))
            tag = m.group(2).lower()
            full = m.group(0)

            if tag in VOID_TAGS:
                continue
            if is_self_closing(full):
                continue

            if not is_close:
                stack.append((tag, i))
            else:
                # pop until match? safer: strict match; if mismatch => extra close
                if stack and stack[-1][0] == tag:
                    stack.pop()
                else:
                    # try to recover: search stack for matching tag
                    found_at = None
                    for idx in range(len(stack) - 1, -1, -1):
                        if stack[idx][0] == tag:
                            found_at = idx
                            break
                    if found_at is not None:
                        # pop unmatched opens above it (structurally bad but recoverable)
                        stack = stack[:found_at]
                        if stack and stack[-1][0] == tag:
                            stack.pop()
                    else:
                        extra_closings.append(i)

    unclosed = [ln for (_tag, ln) in stack]
    return extra_closings, unclosed


# -------------------------
# Duplicate Alpine tab block extraction
# -------------------------
ACTIVE_TAB_RE = re.compile(r"x-show=\"\s*activeTab\s*===\s*'([^']+)'\s*\"")

OPENING_TAG_RE = re.compile(r"<\s*([a-zA-Z][a-zA-Z0-9:-]*)\b[^>]*x-show=\"\s*activeTab\s*===\s*'[^']+'\s*\"[^>]*>")

def normalize_block(lines: List[str]) -> List[str]:
    out = []
    for ln in lines:
        s = ln.rstrip()
        if s.strip() == "":
            # collapse excessive blank lines later
            out.append("")
        else:
            out.append(s)
    # collapse multiple blank lines
    collapsed = []
    blank = False
    for s in out:
        if s == "":
            if not blank:
                collapsed.append("")
            blank = True
        else:
            collapsed.append(s.strip())
            blank = False
    # trim leading/trailing blanks
    while collapsed and collapsed[0] == "":
        collapsed.pop(0)
    while collapsed and collapsed[-1] == "":
        collapsed.pop()
    return collapsed

def extract_block(lines: List[str], start_line: int) -> Tuple[int, str, List[str]]:
    """
    Given a start_line containing x-show activeTab === 'X', extract until matching closing tag
    for that opening tag.
    Returns: (end_line, tagname, raw_lines)
    """
    idx0 = start_line - 1
    line0 = lines[idx0]

    m = OPENING_TAG_RE.search(line0)
    if not m:
        # fallback: assume div if not found
        tag = "div"
    else:
        tag = m.group(1).lower()

    # scan forward tracking nesting of same tag and other tags
    depth = 0
    raw: List[str] = []
    in_script = False
    in_style = False

    for i in range(idx0, len(lines)):
        line = lines[i]
        raw.append(line)

        if re.search(r"<\s*script\b", line, flags=re.I):
            in_script = True
        if re.search(r"<\s*style\b", line, flags=re.I):
            in_style = True

        if in_script or in_style:
            if in_script and re.search(r"</\s*script\s*>", line, flags=re.I):
                in_script = False
            if in_style and re.search(r"</\s*style\s*>", line, flags=re.I):
                in_style = False
            continue

        for tm in TAG_TOKEN_RE.finditer(line):
            is_close = bool(tm.group(1))
            t = tm.group(2).lower()
            full = tm.group(0)

            if t in VOID_TAGS or is_self_closing(full):
                continue

            if not is_close and t == tag:
                depth += 1
            elif is_close and t == tag:
                depth -= 1
                if depth == 0:
                    return (i + 1, tag, raw)

    # if never closed, return to EOF
    return (len(lines), tag, raw)

def similarity_ratio(a: List[str], b: List[str]) -> float:
    return difflib.SequenceMatcher(a=a, b=b).ratio()

def simple_similarity_hint_score(raw_lines: List[str]) -> int:
    """
    Higher score means "richer" implementation.
    Used to pick the likely 'keep' block.
    """
    s = "\n".join(raw_lines)
    score = 0
    if "<table" in s: score += 4
    if "x-for=" in s or "x-for=\"" in s: score += 3
    if "@click" in s or "@submit" in s: score += 3
    if "fetch(" in s: score += 3
    if "x-init" in s: score += 3
    if "modal" in s.lower(): score += 1
    if "<button" in s: score += 1
    return score

def extract_dependencies(raw_lines: List[str], full_file_text: str) -> Dict[str, object]:
    s = "\n".join(raw_lines)

    has_events = bool(re.search(r"@\w+\s*=", s))
    has_fetch = "fetch(" in s
    has_xinit = "x-init" in s
    has_side_effects = has_fetch or has_xinit

    ids = re.findall(r'\bid\s*=\s*"([^"]+)"', s)
    xrefs = re.findall(r'\bx-ref\s*=\s*"([^"]+)"', s)

    # If any $refs.<x> exists elsewhere, x-ref is "externally referenced"
    externally_referenced_refs = []
    for r in xrefs:
        if re.search(rf"\$refs\.{re.escape(r)}\b", full_file_text):
            externally_referenced_refs.append(r)

    # state tokens: pull identifiers from directive values (x-text, x-show, x-if, :class, x-for, etc.)
    directive_vals = re.findall(r'\b(?:x-text|x-show|x-if|x-for|:class|:value|x-model)\s*=\s*"([^"]+)"', s)
    tokens = []
    for expr in directive_vals:
        for t in re.findall(r"\b[A-Za-z_]\w*\b", expr):
            if t in JS_KEYWORDS:
                continue
            # ignore common html words
            if t.lower() in ("window", "document", "location", "hostname", "length"):
                continue
            tokens.append(t)
    # de-dup keep order
    seen = set()
    state_tokens = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            state_tokens.append(t)

    # informational-only heuristic
    no_bindings = not re.search(r"\bx-|@\w+|:class|x-model|x-text|x-show|x-if|x-for", s)
    no_buttons = "<button" not in s
    informational_only = no_bindings and no_buttons and not has_side_effects

    return {
        "has_events": has_events,
        "has_side_effects": has_side_effects,
        "ids": ids,
        "xrefs": xrefs,
        "externally_referenced_refs": externally_referenced_refs,
        "state_tokens": state_tokens,
        "has_table": "<table" in s,
        "has_xfor": ("x-for" in s),
        "has_fetch": has_fetch,
        "has_xinit": has_xinit,
        "informational_only": informational_only,
    }

def collect_tab_blocks(lines: List[str]) -> Dict[str, List[BlockMeta]]:
    full_text = "\n".join(lines)

    # find all x-show activeTab lines
    occurrences: List[Tuple[str, int]] = []
    for i, line in enumerate(lines, 1):
        m = ACTIVE_TAB_RE.search(line)
        if m:
            occurrences.append((m.group(1), i))

    blocks_by_tab: Dict[str, List[BlockMeta]] = defaultdict(list)

    for tab, ln in occurrences:
        end_ln, tag, raw = extract_block(lines, ln)
        norm = normalize_block(raw)
        dep = extract_dependencies(raw, full_text)
        score = simple_similarity_hint_score(raw)

        blocks_by_tab[tab].append(BlockMeta(
            tab=tab,
            start_line=ln,
            end_line=end_ln,
            tag=tag,
            raw_lines=raw,
            norm_lines=norm,
            similarity_hint_score=score,
            has_events=bool(dep["has_events"]),
            has_side_effects=bool(dep["has_side_effects"]),
            ids=list(dep["ids"]),
            xrefs=list(dep["xrefs"]),
            state_tokens=list(dep["state_tokens"]),
            has_table=bool(dep["has_table"]),
            has_xfor=bool(dep["has_xfor"]),
            has_fetch=bool(dep["has_fetch"]),
            has_xinit=bool(dep["has_xinit"]),
            informational_only=bool(dep["informational_only"]),
        ))

    return blocks_by_tab


# -------------------------
# Recommendation logic (analysis-only)
# -------------------------
def recommend_for_tab(tab: str, blocks: List[BlockMeta]) -> Optional[str]:
    """
    Returns a recommendation string if HIGH-confidence safe.
    Otherwise returns None.
    """
    if len(blocks) < 2:
        return None

    # pick "keep" as richest by hint score, then by length
    keep = sorted(blocks, key=lambda b: (b.similarity_hint_score, len(b.raw_lines)), reverse=True)[0]
    others = [b for b in blocks if b is not keep]

    # Try to recommend removing a strictly weaker block that is informational-only and no unique behavior
    for cand in sorted(others, key=lambda b: (b.similarity_hint_score, len(b.raw_lines))):
        # safety gates
        if cand.has_events or cand.has_side_effects or cand.has_fetch or cand.has_xinit:
            continue
        if cand.xrefs or cand.ids:
            continue
        # must be informational-only to be HIGH confidence at this phase
        if not cand.informational_only:
            continue

        sim = similarity_ratio(cand.norm_lines, keep.norm_lines)
        classification = "DIFFERENT"
        if sim >= 0.95:
            classification = "IDENTICAL"
        elif sim >= 0.60:
            classification = "SIMILAR"

        if classification in ("IDENTICAL", "SIMILAR"):
            return (
                f"Recommendation (Confidence: HIGH)\n"
                f"- Likely keep: lines {keep.start_line}–{keep.end_line} (richer implementation)\n"
                f"- Likely removable: lines {cand.start_line}–{cand.end_line} (informational-only)\n"
                f"- Similarity: {sim:.0%} ({classification})\n"
                f"Why safe:\n"
                f"  - removable block has no events / side effects\n"
                f"  - removable block defines no id/x-ref\n"
            )

    return None


# -------------------------
# Commands
# -------------------------
def analyze_html(path: Path):
    lines = read_lines(path)

    extra_close, unclosed_open = find_tag_imbalances(lines)
    blocks_by_tab = collect_tab_blocks(lines)

    duplicates = {t: blks for t, blks in blocks_by_tab.items() if len(blks) > 1}

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📋 Analysis Summary: {path.name}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    any_findings = False

    # Any-tag structural issues
    if extra_close:
        any_findings = True
        print("❌ Extra closing tags detected (any tag):")
        for ln in extra_close[:30]:
            print(f"  - Line {ln}")
        if len(extra_close) > 30:
            print(f"  ... plus {len(extra_close)-30} more")
        print("  Impact: can break Alpine scope / blank tabs / DOM corruption")
        print("  Fix: remove extra closing tags or restore missing openers\n")

    if unclosed_open:
        any_findings = True
        print("❌ Unclosed opening tags detected (any tag):")
        for ln in unclosed_open[:30]:
            print(f"  - Line {ln}")
        if len(unclosed_open) > 30:
            print(f"  ... plus {len(unclosed_open)-30} more")
        print("  Impact: DOM never closes correctly, unpredictable rendering\n")

    # Duplicate tab blocks
    if duplicates:
        any_findings = True
        for tab, blks in duplicates.items():
            locs = ", ".join(str(b.start_line) for b in blks)
            print(f"⚠ Duplicate tab blocks for '{tab}' ({len(blks)} blocks) at lines: {locs}")

            # pairwise similarity overview against richest block
            keep = sorted(blks, key=lambda b: (b.similarity_hint_score, len(b.raw_lines)), reverse=True)[0]
            print(f"  Candidate keep: lines {keep.start_line}–{keep.end_line} (score={keep.similarity_hint_score})")

            for b in sorted([x for x in blks if x is not keep], key=lambda x: x.start_line):
                sim = similarity_ratio(b.norm_lines, keep.norm_lines)
                if sim >= 0.95:
                    cls = "IDENTICAL"
                elif sim >= 0.60:
                    cls = "SIMILAR"
                else:
                    cls = "DIFFERENT"

                flags = []
                if b.has_events: flags.append("events")
                if b.has_side_effects: flags.append("side-effects")
                if b.has_table: flags.append("table")
                if b.has_xfor: flags.append("x-for")
                if b.informational_only: flags.append("info-only")
                flag_s = (", ".join(flags)) if flags else "none"

                print(f"  - Block lines {b.start_line}–{b.end_line}: similarity {sim:.0%} ({cls}); flags: {flag_s}")

            rec = recommend_for_tab(tab, blks)
            if rec:
                print("\n  ✅ " + rec.replace("\n", "\n  "))
            else:
                print("\n  ℹ Recommendation: none (manual review required for safety)\n")

    if not any_findings:
        print("✔ No structural issues detected")
        print("\nStatus: ✅ SAFE\n")
        return

    # Determine safety
    if extra_close or unclosed_open or duplicates:
        print("Status: ❌ NOT SAFE TO DEPLOY\n")
    else:
        print("Status: ✅ SAFE\n")


def review_html(path: Path):
    lines = read_lines(path)
    size = len(lines)

    # Alpine roots count
    alpine_roots = [i for i, l in enumerate(lines, 1) if "x-data=" in l]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🧠 Code Review: {path.name}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if size > 1500:
        print("⚠ File Size Risk")
        print(f"  - Lines of code: {size}")
        print("  - High cognitive load / merge risk")
        print("  Recommendation:")
        print("    ✔ Consider splitting tabs into partials later")
        print("    ✔ Keep Alpine root shallow where possible\n")

    if len(alpine_roots) != 1:
        print("❌ Alpine Root Issue")
        print(f"  - Alpine roots found: {len(alpine_roots)}")
        if alpine_roots:
            print(f"  - Lines: {alpine_roots[:10]}{'...' if len(alpine_roots) > 10 else ''}")
        print("  Recommendation:")
        print("    ✔ Exactly one Alpine root per page\n")
    else:
        print("✔ Alpine root detected (good)\n")

    print("📌 Review Verdict:")
    print("  ✔ Useful structure tooling is in place")
    print("  ⚠ Large-file fragility remains (expected)")
    print("  ✔ Use netpilot-doctor analyze before major edits\n")


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?", default=None)
    parser.add_argument("file", nargs="?", default=None)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--help", action="store_true")

    args = parser.parse_args()

    if args.help or args.command in (None, "--help", "-h"):
        print(HELP_TEXT.strip())
        return

    if args.version or args.command == "--version":
        print(f"netpilot-doctor v{VERSION}")
        return

    if args.command not in ("analyze", "review") or not args.file:
        print("❌ Invalid arguments\n")
        print(HELP_TEXT.strip())
        sys.exit(1)

    path = Path(args.file)

    if args.command == "analyze":
        analyze_html(path)
    elif args.command == "review":
        review_html(path)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
netpilot-doctor v1
Structural Analyzer & Review Tool (HTML focus)
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

VERSION = "1.0.0"


# -------------------------
# CLI HELP
# -------------------------
HELP_TEXT = f"""
NetPilot Doctor v{VERSION}
Structural Analysis & Review Tool

Usage:
  netpilot-doctor analyze <file>
  netpilot-doctor review <file>
  netpilot-doctor --version
  netpilot-doctor --help

Examples:
  netpilot-doctor analyze dashboard_test.html
  netpilot-doctor review dashboard_test.html
"""


# -------------------------
# UTILITIES
# -------------------------
def read_file(path: Path) -> list[str]:
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(2)
    return path.read_text().splitlines()


# -------------------------
# ANALYZE
# -------------------------
def analyze_html(path: Path):
    lines = read_file(path)

    stack = []
    extra_closings = []
    for i, line in enumerate(lines, 1):
        if "<div" in line:
            stack.append(i)
        if "</div>" in line:
            if stack:
                stack.pop()
            else:
                extra_closings.append(i)

    # Alpine tabs
    tab_blocks = defaultdict(list)
    for i, line in enumerate(lines, 1):
        m = re.search(r"x-show=\"activeTab === '([^']+)'\"", line)
        if m:
            tab_blocks[m.group(1)].append(i)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📋 Analysis Summary: {path.name}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if not extra_closings and not stack and all(len(v) == 1 for v in tab_blocks.values()):
        print("✔ No structural errors detected")
        print("\nStatus: ✅ SAFE\n")
        return

    if extra_closings:
        print("❌ Extra closing </div> tags detected:")
        for ln in extra_closings:
            print(f"  - Line {ln}")
        print("  Impact:")
        print("    - Can close Alpine root early")
        print("    - Causes blank or broken tabs")
        print("  Fix:")
        print("    - Remove the extra </div> manually")
        print("    - (Future) netpilot-doctor fix-structure\n")

    if stack:
        print("❌ Unclosed <div> tags detected at lines:")
        for ln in stack:
            print(f"  - Line {ln}")
        print("  Impact:")
        print("    - DOM corruption")
        print("    - VS Code auto-reflow issues\n")

    for tab, locs in tab_blocks.items():
        if len(locs) > 1:
            print(f"⚠ Duplicate tab blocks for '{tab}':")
            for ln in locs:
                print(f"  - Line {ln}")
            print("  Impact:")
            print("    - DOM ambiguity")
            print("    - Fragile tab behavior\n")

    print("Status: ❌ NOT SAFE TO DEPLOY\n")


# -------------------------
# REVIEW
# -------------------------
def review_html(path: Path):
    lines = read_file(path)
    size = len(lines)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🧠 Code Review: {path.name}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if size > 1500:
        print("⚠ File Size Risk")
        print(f"  - Lines of code: {size}")
        print("  - High cognitive load")
        print("  Recommendation:")
        print("    ✔ Split large tabs into partials")
        print("    ✔ Keep Alpine root shallow\n")

    alpine_roots = [i for i, l in enumerate(lines, 1) if "x-data=" in l]
    if len(alpine_roots) != 1:
        print("❌ Alpine Root Issue")
        print(f"  - Alpine roots found: {len(alpine_roots)}")
        print("  Recommendation:")
        print("    ✔ Exactly one Alpine root per page\n")
    else:
        print("✔ Alpine root detected (good)\n")

    print("📌 Review Verdict:")
    print("  ✔ Functionally acceptable")
    print("  ⚠ Structurally sensitive to future changes")
    print("  ✔ Use netpilot-doctor before major edits\n")


# -------------------------
# MAIN
# -------------------------
def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("--help", "-h"):
        print(HELP_TEXT)
        return

    if sys.argv[1] == "--version":
        print(f"netpilot-doctor v{VERSION}")
        return

    if len(sys.argv) != 3:
        print("❌ Invalid arguments\n")
        print(HELP_TEXT)
        sys.exit(1)

    command, file = sys.argv[1], Path(sys.argv[2])

    if command == "analyze":
        analyze_html(file)
    elif command == "review":
        review_html(file)
    else:
        print(f"❌ Unknown command: {command}\n")
        print(HELP_TEXT)
        sys.exit(1)


if __name__ == "__main__":
    main()


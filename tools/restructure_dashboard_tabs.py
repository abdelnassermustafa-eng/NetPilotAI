#!/usr/bin/env python3
import re
import sys
from pathlib import Path

FILE = Path("app/templates/dashboard.html")
BACKUP = FILE.with_suffix(".html.bak")

TABS = [
    "routes",
    "igws",
    "nat",
    "validation",
    "observability",
]

TAB_RE = re.compile(
    r'(<div\s+[^>]*x-show\s*=\s*"activeTab\s*===\s*\'(?P<tab>\w+)\'"[^>]*>)',
    re.MULTILINE
)

def find_matching_div(text, start_index):
    """Find matching closing </div> accounting for nesting."""
    depth = 0
    for match in re.finditer(r'</?div\b', text[start_index:]):
        tag = match.group()
        if tag.startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = start_index + match.end()
                return end
    raise RuntimeError("Unbalanced <div> detected")

def main():
    if not FILE.exists():
        print("ERROR: dashboard.html not found")
        sys.exit(1)

    text = FILE.read_text()

    matches = list(TAB_RE.finditer(text))
    found_tabs = [m.group("tab") for m in matches]

    for tab in TABS:
        if found_tabs.count(tab) != 1:
            print(f"ERROR: tab '{tab}' appears {found_tabs.count(tab)} times")
            sys.exit(1)

    blocks = {}
    for m in matches:
        tab = m.group("tab")
        start = m.start()
        end = find_matching_div(text, m.start())
        blocks[tab] = text[start:end]

    # Remove all tab blocks from original text
    stripped = text
    for block in blocks.values():
        stripped = stripped.replace(block, "")

    # Reassemble in correct order
    rebuilt = stripped.rstrip() + "\n\n"
    for tab in TABS:
        rebuilt += (
            f"\n<!-- ================= TAB: {tab.upper()} (START) ================= -->\n"
            + blocks[tab]
            + f"\n<!-- ================= TAB: {tab.upper()} (END) ================= -->\n"
        )

    # Backup
    FILE.rename(BACKUP)
    FILE.write_text(rebuilt)

    print("✅ dashboard.html restructured successfully")
    print(f"🗂 Backup created: {BACKUP}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import re
import sys
from pathlib import Path

FILE = Path("app/templates/dashboard.html")

TABS = ["routes", "igws", "nat", "validation", "observability"]

TAB_OPEN_RE = re.compile(
    r'<div\s+[^>]*x-show\s*=\s*"activeTab\s*===\s*\'(?P<tab>\w+)\'"[^>]*>'
)

DIV_RE = re.compile(r'</?div\b')

def find_matching_div(text, start):
    depth = 0
    for m in DIV_RE.finditer(text[start:]):
        tag = m.group()
        if tag.startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start + m.end()
    return None

def audit():
    text = FILE.read_text()
    matches = list(TAB_OPEN_RE.finditer(text))

    found = [m.group("tab") for m in matches]

    print("\n🔍 DASHBOARD STRUCTURAL AUDIT\n")

    # Rule 1: exactly one tab each
    failed = False
    for tab in TABS:
        count = found.count(tab)
        if count != 1:
            print(f"✖ Tab '{tab}' appears {count} times (expected 1)")
            failed = True
        else:
            print(f"✔ Tab '{tab}' found exactly once")

    # Rule 2: balanced div blocks
    blocks = {}
    for m in matches:
        tab = m.group("tab")
        start = m.start()
        end = find_matching_div(text, start)
        if not end:
            print(f"✖ Tab '{tab}' has unbalanced <div>")
            failed = True
        else:
            blocks[tab] = (start, end)
            print(f"✔ Tab '{tab}' div structure balanced")

    # Rule 3: no nesting
    for outer in blocks:
        o_start, o_end = blocks[outer]
        for inner in blocks:
            if outer == inner:
                continue
            i_start, _ = blocks[inner]
            if o_start < i_start < o_end:
                print(f"✖ Tab '{inner}' is nested inside '{outer}'")
                failed = True

    print("\n📋 RESULT\n")
    if failed:
        print("STATUS: ❌ UNSAFE — NO AUTOMATED CHANGES ALLOWED\n")
        print("Required actions:")
        print("- Close all tabs before the next one begins")
        print("- Ensure all activeTab containers are siblings")
        sys.exit(1)
    else:
        print("STATUS: ✅ SAFE TO RESTRUCTURE\n")
        print("You may now run the restructure script.")
        sys.exit(0)

if __name__ == "__main__":
    if not FILE.exists():
        print("ERROR: dashboard.html not found")
        sys.exit(1)
    audit()


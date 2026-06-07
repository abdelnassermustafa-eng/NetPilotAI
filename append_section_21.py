from pathlib import Path

file_path = Path("app/templates/observability/_tools_operational_guidance.html")

section_21 = """
<!-- ============================================================= -->
<!-- SECTION 21: THE OPERATOR IS PART OF THE SYSTEM (FINAL) -->
<!-- ============================================================= -->

<section class="space-y-4">

  <h3 class="text-base font-semibold text-slate-800">
    🧭 The Operator Is Part of the System
  </h3>

  <p class="text-sm text-slate-700">
    In NetPilot’s model, the system does not end at AWS resources,
    APIs, or automation pipelines. The operator is part of the system.
  </p>

  <p class="text-sm text-slate-700">
    Decisions made under pressure, assumptions carried forward,
    shortcuts taken, or warnings ignored all become system behavior.
    Incidents are rarely caused by a single command — they are caused
    by human interaction with incomplete understanding.
  </p>

  <ul class="list-disc list-outside pl-5 text-sm text-slate-700 space-y-1">
    <li>Systems fail where understanding is shallow</li>
    <li>Automation amplifies both correctness and mistakes</li>
    <li>Speed without clarity creates invisible risk</li>
    <li>Silence in dashboards does not imply safety</li>
  </ul>

  <p class="text-sm text-slate-700">
    This is why NetPilot separates <strong>thinking</strong> from
    <strong>execution</strong>, and <strong>inspection</strong> from
    <strong>change</strong>.
  </p>

  <p class="text-xs text-slate-500 italic">
    This document ends here by design.
    Understanding is the final dependency.
  </p>

</section>
"""

with file_path.open("a", encoding="utf-8") as f:
    f.write(section_21)

print("✅ Section 21 appended successfully")

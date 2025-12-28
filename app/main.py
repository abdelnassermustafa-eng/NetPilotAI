from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# ----------------------------
# Core Routers (VALID)
# ----------------------------
from app.api.v1.routers.dashboard import router as dashboard_router
from app.api.v1.routers.aws import router as aws_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.ops_docs import router as ops_docs_router

from app.db.init_db import init_db

# ----------------------------
# Future / Not-present Routers (COMMENTED)
# ----------------------------
# from app.api.v1.routers.aws_subnet_inspect import router as aws_subnet_inspect_router
# from app.api.v1.routers.aws_vpcs import router as aws_vpcs_router
# from app.api.v1.routers.aws_route_tables import router as aws_route_tables_router
# from app.api.v1.routers.aws_internet_gateways import router as aws_igw_router
# from app.api.v1.routers.aws_nat_gateways import router as aws_nat_router


templates = Jinja2Templates(directory="app/templates")


app = FastAPI(
    title="NetPilot AI Backend",
    description="Multi-cloud & Network Automation Platform",
    version="1.0.0",
)

# ----------------------------
# Routers
# ----------------------------
app.include_router(health_router, prefix="/api/v1")
app.include_router(aws_router, prefix="/api/v1/aws")
app.include_router(dashboard_router, prefix="/api/v1/dashboard")
app.include_router(ops_docs_router, prefix="/api/v1/ops", tags=["validation", "operations"])

# ----------------------------
# Future / Not-present Routers (COMMENTED)
# ----------------------------
# app.include_router(aws_subnet_inspect_router, prefix="/api/v1")
# app.include_router(aws_vpcs_router, prefix="/api/v1")
# app.include_router(aws_route_tables_router, prefix="/api/v1")
# app.include_router(aws_igw_router, prefix="/api/v1")
# app.include_router(aws_nat_router, prefix="/api/v1")



# ----------------------------
# Dashboard (Root UI)
# ----------------------------
@app.get("/", tags=["dashboard"])
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ============================================================
# Sidebar Placeholder Pages (Formatted / Professional)
# ============================================================
def _placeholder_page(
    request: Request,
    title: str,
    status_label: str,
    status_color: str,
    purpose: str,
    why_staged: str,
    planned: list[str],
    notes: list[str] | None = None,
) -> HTMLResponse:
    """
    Server-rendered placeholder pages:
    - Keep UI stable even when JS modules are evolving
    - Provide clear intent + roadmap + safety rationale
    """
    # Basic status color mapping for badge
    badge_classes = {
        "orange": "bg-orange-100 text-orange-800 border-orange-300",
        "blue": "bg-blue-100 text-blue-800 border-blue-300",
        "green": "bg-green-100 text-green-800 border-green-300",
        "slate": "bg-slate-100 text-slate-800 border-slate-300",
        "red": "bg-red-100 text-red-800 border-red-300",
    }
    badge = badge_classes.get(status_color, badge_classes["slate"])

    planned_html = "\n".join(
        [f'<li class="leading-relaxed">{item}</li>' for item in planned]
    )
    notes_html = ""
    if notes:
        notes_html = "\n".join(
            [f'<li class="leading-relaxed">{item}</li>' for item in notes]
        )

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title} • NetPilot AI</title>

  <!-- Tailwind build -->
  <link rel="stylesheet" href="/static/css/output.css" />
</head>

<body class="bg-slate-100 text-slate-900">
  <div class="max-w-6xl mx-auto px-6 py-10 space-y-10">

    <!-- Header -->
    <!-- Header -->
    <div class="bg-white rounded-xl shadow border border-slate-200 p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-6">

      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-semibold {badge}">
          <span class="h-2 w-2 rounded-full bg-current opacity-70"></span>
          <span>{status_label}</span>
        </div>

        <h1 class="mt-4 text-3xl font-bold tracking-tight text-slate-900">{title}</h1>
        <p class="mt-2 text-slate-600">
          This module is currently staged and presented as a stable placeholder while the backend and automation
          layers evolve safely.
        </p>
      </div>

      <a href="/" class="shrink-0 inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 shadow">
        ← Back to Dashboard
      </a>
    </div>

    <!-- Content Grid -->
    <div class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Purpose -->
      <div class="bg-white rounded-xl shadow p-6 border border-slate-200">
        <h2 class="text-lg font-semibold text-slate-900 uppercase tracking-wide text-sm">
        Purpose
        </h2>

        <p class="mt-3 text-slate-700 leading-relaxed">{purpose}</p>

        <div class="mt-6 rounded-lg bg-slate-50 border border-slate-200 p-4">
          <p class="text-sm text-slate-700 leading-relaxed">
            <span class="font-semibold">Design goal:</span>
            Make the platform predictable. Every workflow will rely on a consistent context layer
            (account, region, environment, and safety guardrails).
          </p>
        </div>
      </div>

      <!-- Why staged -->
      <div class="bg-white rounded-xl shadow p-6 border border-slate-200">
        <h2 class="text-lg font-bold text-slate-900">Why this module is staged</h2>
        <p class="mt-3 text-slate-700 leading-relaxed">{why_staged}</p>

        <div class="mt-6 border-l-4 border-slate-400 bg-slate-50 rounded-lg p-4">
          <p class="text-sm text-orange-900 leading-relaxed">
            <span class="font-semibold">Safety-first:</span>
            NetPilot AI will not expose destructive or account-scoped actions until identity, scope,
            and guardrails are validated.
          </p>
        </div>
      </div>

      <!-- Planned capabilities -->
      <div class="bg-white rounded-xl shadow p-6 border border-slate-200">
        <h2 class="text-lg font-bold text-slate-900">Planned capabilities</h2>
        <ul class="mt-3 list-disc list-inside space-y-2 text-slate-700">
          {planned_html}
        </ul>

        <div class="mt-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
          <p class="text-sm text-blue-900 leading-relaxed">
            <span class="font-semibold">Implementation note:</span>
            This page is intentionally rendered server-side to keep the UI stable while API contracts
            and automation orchestration mature.
          </p>
        </div>
      </div>

    </div>

    <!-- Optional Notes -->
    {""
      if not notes
      else f'''
    <div class="mt-6 bg-white rounded-xl shadow p-6 border border-slate-200">
      <h2 class="text-lg font-bold text-slate-900">Operational notes</h2>
      <ul class="mt-3 list-disc list-inside space-y-2 text-slate-700">
        {notes_html}
      </ul>
    </div>
    '''}

    <!-- Footer -->
    <div class="mt-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-sm text-slate-500">
      <div>
        <span class="font-semibold text-slate-700">NetPilot AI</span> • staged module placeholder • safe evolution path
      </div>
      <div class="text-slate-500">
        When ready, this module will be wired into the dashboard with live state, validation, and audit logging.
      </div>
    </div>

  </div>
</body>
</html>
"""
    return HTMLResponse(content=html)


# ----------------------------
# Sidebar Routes (Placeholders)
# ----------------------------
@app.get("/cloud", response_class=HTMLResponse, tags=["placeholders"])
def cloud_context(request: Request):
    return _placeholder_page(
        request=request,
        title="Cloud Context",
        status_label="Module status: Under Active Development",
        status_color="orange",
        purpose=(
            "Defines cloud account identity, region scope, and environmental boundaries used by all NetPilot AI "
            "automation workflows."
        ),
        why_staged=(
            "Cloud context must be established before allowing automation. This prevents accidental execution in the "
            "wrong account, wrong region, or wrong environment (prod vs dev)."
        ),
        planned=[
            "AWS account & identity verification (STS)",
            "Region and environment selection",
            "Global safety guardrails (prevent accidental prod impact)",
            "Cross-cloud abstraction (AWS → Azure → GCP)",
        ],
        notes=[
            "This page is a stable placeholder while identity and region validation are implemented.",
            "Once enabled, all automation routes will depend on Cloud Context state.",
        ],
    )


@app.get("/vendors", response_class=HTMLResponse, tags=["placeholders"])
def vendors_providers(request: Request):
    return _placeholder_page(
        request=request,
        title="Vendors & Providers",
        status_label="Module status: Staged for Integration",
        status_color="blue",
        purpose=(
            "A capability registry for supported providers (cloud + network), used to map NetPilot AI workflows to "
            "provider-specific APIs and constraints."
        ),
        why_staged=(
            "Provider abstraction must be modeled first (capabilities, limits, region/service availability) so that "
            "automation steps remain consistent and safe across providers."
        ),
        planned=[
            "AWS / Azure / GCP provider capability profiles",
            "Network vendor adapters (Cisco / Juniper) for inventory + automation",
            "Credentials and session isolation per provider",
            "Provider health checks and API error normalization",
        ],
        notes=[
            "Provider adapters will be introduced progressively, starting with AWS VPC primitives.",
            "Every provider integration will ship with safe defaults, auditing, and rollback-aware workflows.",
        ],
    )


@app.get("/automation", response_class=HTMLResponse, tags=["placeholders"])
def automation_workflows(request: Request):
    return _placeholder_page(
        request=request,
        title="Automation Workflows",
        status_label="Module status: Under Active Development",
        status_color="orange",
        purpose=(
            "Composable workflows built on validated primitives (VPCs, Subnets, Route Tables, IGWs, NATs) with "
            "guardrails, dry-run support, and audit logging."
        ),
        why_staged=(
            "Automation is gated until dependency discovery, safe delete behavior, and rollback patterns are "
            "proven stable. This avoids partial builds and broken environments."
        ),
        planned=[
            "Workflow runner with dry-run mode (plan → apply)",
            "Dependency-aware provisioning (public/private subnet patterns)",
            "Rollback/cleanup strategy for partial failures",
            "Audit logging for every execution step",
        ],
        notes=[
            "Workflows will be enabled gradually: inventory → safe operations → controlled automation.",
            "Each workflow will include pre-checks (identity, region, quotas) before execution.",
        ],
    )


@app.get("/settings", response_class=HTMLResponse, tags=["placeholders"])
def settings_governance(request: Request):
    return _placeholder_page(
        request=request,
        title="Settings & Governance",
        status_label="Module status: Planned",
        status_color="slate",
        purpose=(
            "Global controls for safety mode, logging, preferences, and governance rules that protect production "
            "environments and enforce good operational hygiene."
        ),
        why_staged=(
            "Governance defaults should evolve from real usage patterns. These controls will be introduced after the "
            "core AWS inventory and safe operations are stable."
        ),
        planned=[
            "Safe mode toggles and environment locks (dev/test/prod)",
            "Audit log viewer and export",
            "Global defaults (region, timeouts, retry policy)",
            "API rate-limit handling and backoff tuning",
        ],
        notes=[
            "Settings will become the single place to control guardrails for all modules.",
            "Governance will support both UI-based changes and API-based policy enforcement.",
        ],
    )


# ----------------------------
# Startup event
# ----------------------------
@app.on_event("startup")
def startup_event():
    init_db()
    print("NetPilot AI backend started successfully.")

from app.api.v1.routers.aws_health import router as aws_health_router
app.include_router(aws_health_router, prefix="/api/v1")
from app.api.v1.routers.aws_health_legacy import router as aws_health_legacy_router
app.include_router(aws_health_legacy_router, prefix="/api/v1")

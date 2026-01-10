# NetPilot AI — Observability Roadmap (Priority + Truth-Based)

## Phase 0 — Scope guardrails (NOW)
- Observability is read-only (no infrastructure modifications).
- UI text must never imply delivery beyond what exists.
- Anything not implemented is labeled: Planned / Under construction.

## Phase 1 — Logs (ship-quality baseline)
Goal: Logs are the first vendor-trust deliverable.

### ✅ Ready to ship (completed)
- Application Logs (CloudWatch Logs)
- Log Stream Viewer
- Auto-refresh logs (working)

### ⚠️ Partial (ship as partial with labels)
- Lambda Logs (limited coverage / not fully wired)
- ECS / EC2 Logs (subset of sources / not fully wired)

### 🚧 Not yet (do not claim delivered)
- Kubernetes Logs (future)

Exit criteria:
- Logs tab stable, no UI bleed into other pages
- Clear labels: implemented vs partial vs planned

## Phase 2 — Metrics (minimum useful, honest)
Goal: Situational awareness without fake precision.

### ✅ Ready to ship (acceptable baseline)
- Metrics UI present + auto-refresh control
- Backend Status cards (Running, etc.) as informational

### ⚠️ Partial
- CloudWatch metrics basics (CPU/Memory where available; others may show —)
- Errors/Throttles placeholders acceptable if labeled partial

### 🚧 Not yet
- Full Lambda metrics coverage
- Load Balancer metrics coverage
- Custom metrics

Exit criteria:
- Partial metrics labeled clearly
- No implied completeness

## Phase 3 — Alerts (status-only, read-only)
Goal: Awareness only, no actions.

### ✅ Ready to ship
- Display current alerts list (read-only)

### ⚠️ Partial
- If alerts are limited/hardcoded/not fully sourced, label as partial

### 🚧 Not yet
- Alert configuration, creation, suppression, remediation workflows

Exit criteria:
- Alerts are “awareness only”
- No operational actions

## Phase 4 — Events (informational, not wired)
Goal: Keep scope visible, avoid false claims.

### 🚧 Not yet (informational only)
- CloudWatch Events / EventBridge timeline
- SQS events
- SNS notifications
- System events timeline

Exit criteria:
- Events tab clearly marked planned or hidden until wired

## Phase 5 — Tools (read-only playbooks only)
Goal: Guidance, not execution.

### 🚧 Not yet (scope only until implemented)
- AWS CLI read-only examples
- Bash scripts
- Ansible playbooks
- Terraform modules
- Doctor-generated safe playbooks

Exit criteria:
- If shown: examples only / no execution in app

## Phase 6 — Terminal (advanced, last)
Goal: Auditable and consent-based.

### 🚧 Not yet
- Read-only command preview (default)
- User-executed commands (explicit consent)
- Session audit log

Exit criteria:
- Only after security + audit model is complete

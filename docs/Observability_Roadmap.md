# Observability Roadmap — NetPilot AI

This document defines the Observability architecture for NetPilot AI.
It is a **design contract**, not an implementation file.

---

## 📊 Observability (Parent Page)

Observability is the **user-facing operational insight layer**.
It aggregates health, logs, metrics, alerts, events, and tooling.

CloudWatch and other AWS services are **data providers**, not the UI.

---

## 🟢 Always Visible (Top Section)

- Backend Health Status
  - Service name (e.g. netpilot-backend)
  - Status: healthy / degraded / unreachable
  - Source: `/api/v1/health`

This block is always visible when Observability is active.

---

## 📜 Logs

Purpose: inspect application and infrastructure logs.

### Subsections
- Application Logs (CloudWatch Logs)
- Lambda Logs
- ECS / EC2 Logs
- Kubernetes Logs (future)
- Log Stream Viewer

Notes:
- Read-only by default
- Local development shows placeholder state
- CloudWatch becomes active only when deployed to AWS

---

## 📈 Metrics

Purpose: visualize performance and capacity.

### Subsections
- CloudWatch Metrics
  - CPU / Memory
  - Network
  - Errors & Throttles
- Lambda Metrics
- Load Balancer Metrics
- Custom Metrics (future)

---

## 🚨 Alerts

Purpose: proactive issue detection.

### Subsections
- CloudWatch Alarms
- Threshold-based Alerts
- Health Warnings

Notes:
- Advisory only (no auto-remediation)
- Linked to Metrics and Events

---

## 📡 Events

Purpose: understand system behavior and triggers.

### Subsections
- CloudWatch Events / EventBridge
- SQS Events
- SNS Notifications
- System Events Timeline

---

## 🛠 Tools

Purpose: operational support and reproducibility.

### Subsections
- AWS CLI (read-only examples)
- Bash Scripts
- Ansible Playbooks
- Terraform Modules
- NetPilot-Doctor generated safe playbooks

Notes:
- Tools are curated
- All destructive actions documented, not auto-executed

---

## 🖥 Terminal (Advanced)

Purpose: expert-level execution surface.

### Subsections
- Read-only command preview (default)
- User-executed commands (explicit consent)
- Session audit log

Notes:
- User responsibility
- Explicit warnings required
- Full audit trail

---

## Design Principles

- Observability is the parent UI
- CloudWatch is a provider, not a page
- Everything is safe-by-default
- Read-only first, opt-in execution
- Scalable to new AWS services

---

## Status

- Design approved
- Implementation pending
- Protected by NetPilot-Doctor intent checks


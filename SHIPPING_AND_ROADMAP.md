# 📦 Shipping Status & Roadmap

## Current Release: **v1 — MVP (Read-Only)**

NetPilot AI is currently shipped as a **read-only, observability-first control plane** for AWS networking and infrastructure validation.

This release focuses on **visibility, safety, and correctness**, intentionally delaying automation until trust and operational clarity are established.

---

## 🟢 Phase 1 — MVP (Complete)

**Status:** ✅ Shipped

### Included Capabilities

- **AWS Network Visibility**
  - VPCs & Subnets
  - Route Tables
  - Internet Gateways
  - NAT Gateways
  - Validation & Operations views

- **Observability**
  - Logs
  - Metrics
  - Alerts
  - Events
  - Tools
  - Terminal
  - Overview dashboard

- **Platform Foundations**
  - Stable sidebar navigation
  - Modular UI architecture
  - Read-only safety model (no write actions)

This version is safe to run in real AWS environments.

---

## 🟡 Phase 2 — Operational Maturity (Pre-Ship Enhancements)

**Status:** In Progress

Phase 2 focuses on making NetPilot AI **team-ready** without introducing operational risk.

### Planned Enhancements

- **Onboarding & Guidance**
  - Clear first-use explanations
  - Contextual help and safe-operation messaging

- **Basic RBAC / Authentication**
  - Viewer vs Admin roles
  - Backend-enforced access controls

- **Improved Error Handling & Recovery UX**
  - User-friendly error messages
  - Retry and recovery guidance
  - Partial-failure awareness

- **Initial Multi-Account Support**
  - Cross-account IAM role access
  - Account selection and isolation

> Phase 2 does **not** introduce automation or destructive actions.

---

## 🔵 Phase 3 — Controlled Automation & Expansion

**Status:** Planned

Phase 3 introduces automation **carefully and deliberately**, preserving trust and safety.

### Planned Enhancements

- **Safe Automation / Write Actions**
  - Explicit create / update / delete workflows
  - Pre-flight validation and confirmations
  - Rollback and audit logging

- **Advanced Multi-Account Federation**
  - Large-scale account management
  - MSP and consulting workflows

- **Theming & Branding**
  - Custom themes
  - Light / dark modes
  - Brand customization

- **Mobile Optimization**
  - Responsive layouts
  - Read-only mobile dashboards
  - Executive-friendly views

---

## 🧭 Product Philosophy

NetPilot AI is built on the following principles:

- Read before write  
- Validate before automate  
- Safety over speed  
- Clarity over complexity  

This roadmap reflects a deliberate, engineering-driven approach to building a trustworthy operations platform.

---

## 🚦 Shipping Policy

- Phase 1 is **shippable and complete**
- Phase 2 and Phase 3 are **iterative enhancements**, not blockers
- Features are added only if they:
  - Improve trust
  - Reduce risk
  - Preserve clarity

---

## ✅ Status Summary

| Phase | Status | Notes |
|------|--------|------|
| Phase 1 | ✅ Complete | Ready for shipping |
| Phase 2 | ⏳ In Progress | Operational maturity |
| Phase 3 | 🔮 Planned | Automation & scale |

---

*NetPilot AI is shipped with intention — not haste.*

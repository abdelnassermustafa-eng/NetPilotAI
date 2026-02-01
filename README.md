# 🚀 NetPilot AI

**NetPilot AI** is a **read-only AWS Network & Observability control plane** designed to help engineers **see the truth of their cloud network and operational state**—clearly, safely, and without risk.

It brings together **network topology, routing, gateways, observability signals, and operational tooling** into a single, opinionated dashboard that prioritizes **visibility, correctness, and safety**.

> NetPilot AI is intentionally **non-destructive** in its MVP form.  
> No infrastructure changes are executed from the UI.

---

## 🧭 Why NetPilot AI Exists

Modern cloud environments are complex:

- Network state is spread across many AWS services
- Observability data lives in multiple dashboards
- Engineers are forced to jump between consoles, CLIs, and logs
- Visibility is fragmented, and **mistakes are expensive**

NetPilot AI was created to answer a simple but critical question:

> **“What is actually happening in my AWS network and operations—right now?”**

Without:
- Clicking through dozens of AWS pages
- Risking accidental changes
- Needing elevated permissions

---

## 🎯 Design Philosophy

NetPilot AI follows a few strict principles:

- 🔒 **Read-Only First** – Safety over power
- 🧠 **State over Guessing** – Show real backend truth
- 🧩 **Modular by Design** – Each domain stands on its own
- 🛠️ **CLI + UI Harmony** – UI mirrors operational reality
- 📈 **MVP → Platform** – Built to evolve, not to demo

---

## ✨ Key Features (MVP v1)

### 🌐 Network Intelligence
- VPCs & Subnets
- Route Tables
- Internet Gateways
- NAT Gateways
- Validation & Operations (non-destructive)

### 📊 Observability
- Logs
- Metrics
- Alerts
- Events
- Tools (operational references)
- Terminal (read-only execution model)

### 🧭 Overview
- High-level system context
- Entry point for understanding environment state

### 🔐 Safety Model
- No write actions
- No destructive operations
- No hidden automation


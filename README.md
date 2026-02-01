🚀 NetPilot AI

**NetPilot AI** is a **read-only AWS Network & Observability control plane** designed to help engineers **see the truth of their cloud network and operational state**—clearly, safely, and without risk.

It brings together **network topology, routing, gateways, observability signals, and operational tooling** into a single, opinionated dashboard that prioritizes **visibility, correctness, and safety**.

> NetPilot AI is intentionally **non-destructive** in its MVP form.  
> No infrastructure changes are executed from the UI.

---

🧭 Why NetPilot AI Exists

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

🎯 Design Philosophy

NetPilot AI follows a few strict principles:

- 🔒 **Read-Only First** – Safety over power
- 🧠 **State over Guessing** – Show real backend truth
- 🧩 **Modular by Design** – Each domain stands on its own
- 🛠️ **CLI + UI Harmony** – UI mirrors operational reality
- 📈 **MVP → Platform** – Built to evolve, not to demo

---

✨ Key Features (MVP v1)

🌐 Network Intelligence
- VPCs & Subnets
- Route Tables
- Internet Gateways
- NAT Gateways
- Validation & Operations (non-destructive)

📊 Observability
- Logs
- Metrics
- Alerts
- Events
- Tools (operational references)
- Terminal (read-only execution model)

🧭 Overview
- High-level system context
- Entry point for understanding environment state

🔐 Safety Model
- No write actions
- No destructive operations
- No hidden automation


---

👤 Personal Use Cases

NetPilot AI is ideal for:

- Individual cloud engineers
- DevOps learners and practitioners
- Network engineers transitioning to AWS
- Architects validating existing environments
- Educators teaching cloud networking and observability

Use NetPilot AI to:
- Understand AWS networking visually
- Correlate routing, gateways, and traffic paths
- Tie logs, metrics, and events to real infrastructure state
- Practice **safe operational thinking** without risk

---

🏢 Enterprise & Team Use Cases

For organizations, NetPilot AI can serve as:

- A **read-only visibility layer** across AWS environments
- A **network & observability truth dashboard**
- A **training and onboarding tool** for engineers
- A **pre-change validation interface**
- A **foundation for future automation platforms**

Planned enterprise extensions include:
- Role-Based Access Control (RBAC)
- Multi-account and multi-region federation
- Guarded automation with approvals
- Audit-aligned execution models

---

🛠️ Technology Stack

- **Backend:** Python (FastAPI)
- **Frontend:** HTML, Tailwind CSS, Alpine.js
- **Cloud Provider:** AWS (read-only APIs)
- **Architecture:** Modular routers and UI templates
- **Execution Model:** Read-only by design (MVP)

---

📦 Repository Structure (Simplified)

NetPilotAI/
├── app/
│ ├── api/
│ ├── backend/
│ ├── templates/
│ │ ├── observability/
│ │ └── dashboard.html
│ └── main.py
├── README.md
├── SHIPPING_AND_ROADMAP.md
└── requirements.txt

---

⬇️ How to Pull the Repository

Using SSH (recommended):

```bash
git clone git@github.com:abdelnassermustafa-eng/NetPilotAI.git
cd NetPilotAI

===============
SSH is recommended to avoid password authentication and email verification issues.

▶️ How to Run (Local Development)

⚠️ AWS credentials must be configured
Read-only IAM permissions are sufficient.

1️⃣ Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the backend
uvicorn app.main:app --reload

4️⃣ Open in your browser
http://localhost:8000

------------------

🔐 AWS Permissions (MVP)

NetPilot AI requires read-only AWS permissions only.
Typical policies include:

ec2:Describe*

logs:Get*

cloudwatch:Get*

autoscaling:Describe*

elasticloadbalancing:Describe*

❌ No write, modify, or delete permissions are required.

🗺️ Roadmap (High-Level)

For full details, see SHIPPING_AND_ROADMAP.md.

Phase 2 — Enhancements (Planned)

Guarded automation (opt-in, safety-checked)

Advanced RBAC / authentication

Multi-account and multi-region federation

Operational validation layers

Phase 3 — Platform Vision

Mobile optimization

Enterprise theming and branding

Advanced error recovery UX

Plugin-style extensibility

---

⚠️ Current Limitations (Intentional)

The following limitations are **by design** in MVP v1:

- No infrastructure mutations
- No destructive actions
- No automated write operations
- No production-grade authentication model yet

These choices prioritize:
- Safety
- Trust
- Visibility before control

Write capabilities are planned for future phases and will be **opt-in, guarded, and auditable**.

---

👤 Author

**Nasser Abdelghani**  
Senior Network, Automation & Cloud Engineer

NetPilot AI reflects long-term hands-on experience in:
- Networking & routing
- Cloud infrastructure (AWS)
- Observability systems
- Operational safety and automation design

This project was built to demonstrate how **clarity, correctness, and safety** can coexist in modern cloud tooling.

---

✅ Project Status

**✔ MVP v1 — Shipped**  
**✔ Stable**  
**✔ Read-only & safe by design**  
**🚀 Actively evolving**

NetPilot AI is now in a **shippable, reviewable, and extensible** state.



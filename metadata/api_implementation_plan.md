# NetPilot AI — API Implementation Plan (Phase 2)

This file documents the complete API endpoint development sequence for NetPilot AI.  
Follow this order to maintain architecture integrity and UI/backend synchronization.

---

## 📌 Step 1 — System API Endpoints
### ✔ /health
- Basic backend availability check
- Used by dashboard, CI/CD, load balancers

### ✔ System Metrics (future)
- Uptime
- CPU / RAM stats
- DB connectivity

---

## 📌 Step 2 — Dashboard API Endpoints
### ✔ /dashboard
- Basic system summary
- Counts of modules, clouds, vendors
- Version information

Future:
- Workflow queue stats
- Last automation job
- Cloud inventory preview

---

## 📌 Step 3 — Cloud Provider Endpoints

### AWS API Endpoints
- /api/cloud/aws/vpcs
- /api/cloud/aws/security-groups
- /api/cloud/aws/route-tables
- /api/cloud/aws/tgw
- /api/cloud/aws/igw
- /api/cloud/aws/nat
- /api/cloud/aws/elb
- /api/cloud/aws/peering
- /api/cloud/aws/monitoring

### Azure API Endpoints
- /api/cloud/azure/vnets
- /api/cloud/azure/subnets
- /api/cloud/azure/nsg
- /api/cloud/azure/route-tables
- /api/cloud/azure/load-balancers
- /api/cloud/azure/vwan
- /api/cloud/azure/private-link

### GCP API Endpoints
- /api/cloud/gcp/vpcs
- /api/cloud/gcp/subnets
- /api/cloud/gcp/firewalls
- /api/cloud/gcp/load-balancers
- /api/cloud/gcp/routers
- /api/cloud/gcp/nat

---

## 📌 Step 4 — Vendor Network Automation APIs

### Cisco
- IOS-XE: /api/vendor/cisco/iosxe
- NX-OS:  /api/vendor/cisco/nxos
- IOS-XR: /api/vendor/cisco/iosxr
- Meraki: /api/vendor/cisco/meraki
- DNAC:   /api/vendor/cisco/dnac

### Juniper
- Junos: /api/vendor/juniper/junos
- Mist:  /api/vendor/juniper/mist

### Arista
- EOS: /api/vendor/arista/eos
- CVP: /api/vendor/arista/cvp

### Palo Alto
- Panorama: /api/vendor/paloalto/panorama
- Firewalls: (future)

### Fortinet
- FortiGate: /api/vendor/fortinet/fortigate

### Check Point
- Management API: /api/vendor/checkpoint/mgmt

### VMware
- NSX-T: /api/vendor/vmware/nsxt
- vCenter: /api/vendor/vmware/vcenter

---

## 📌 Step 5 — Automation Jobs API
- Trigger workflow runs
- List automation jobs
- Query job status/results

Future:
- Asynchronous task engine
- Event logs

---

## 📌 Step 6 — Compliance Engine API
- Cross-cloud security checks
- Policy compliance
- Drift detection
- SG/NSG/Firewall comparison engine

---

## 📌 Step 7 — Inventory API
- Cloud resource inventory
- Vendor device inventory
- Multi-cloud topology

---

## 📌 Step 8 — Configuration Engine API
- Render Jinja2 templates
- Push configurations
- Versioned config storage

---

## 📌 Step 9 — Logging API
- System logs
- Workflow logs
- Vendor/cloud audit logs

---

## 📌 Step 10 — Authentication API (Phase 3)
- Login
- JWT tokens
- API keys
- Role-based access control

---

# This file is the master reference for API development ordering.

# NetPilot AI — Future Capabilities Roadmap

This document tracks all modules that include planned future enhancements, upcoming features, and extended automation capabilities. It will be updated continuously as new vendors, cloud platforms, and functionalities are added.

---

## 1. Core Backend

### File: `core/config.py`
**Future Capabilities:**
- Multi-environment profiles (dev, prod, test)
- Secrets backend integration
- Hierarchical configuration overrides

### File: `api/v1/routers/health.py`
**Future Capabilities:**
- Database connectivity checks
- Cloud provider status probing
- System uptime and metrics

### File: `utils/templates.py`
**Future Capabilities:**
- Jinja2 template engine integration
- Vendor template directories
- Template versioning and rollback

### File: `utils/s3_backup.py`
**Future Capabilities:**
- S3 backup/restore automation
- Versioned config snapshot storage
- Encryption and lifecycle policies

---

## 2. Cisco Modules

### File: `cisco/iosxe_api.py`
**Future Capabilities:**
- RESTCONF automation
- NETCONF/YANG support
- Advanced onboarding workflows
- Route, VLAN, and ACL automation

### File: `cisco/nxos_api.py`
**Future Capabilities:**
- NX-API JSON-RPC automation
- vPC automation
- VXLAN/EVPN L2/L3 configuration

### File: `cisco/iosxr_api.py`
**Future Capabilities:**
- MPLS/BGP automation engine
- NETCONF/YANG RPC operations
- ISIS/Segment Routing integration

### File: `cisco/meraki_api.py`
**Future Capabilities:**
- Full wireless automation
- Firewall rules
- Traffic shaping and SSID operations

### File: `cisco/dnac_api.py`
**Future Capabilities:**
- Intent-based networking workflows
- Template deployment engine
- Assurance/Telemetry ingestion

---

## 3. Juniper Modules

### File: `juniper/junos_api.py`
**Future Capabilities:**
- NETCONF automation
- RPC configuration loader
- L2/L3 template generator

### File: `juniper/mist_api.py`
**Future Capabilities:**
- AI-driven WLAN insights
- Site creation and provisioning
- Switch/AP firmware automation

---

## 4. Arista Modules

### File: `arista/eos_api.py`
**Future Capabilities:**
- eAPI automation (JSON-RPC)
- VXLAN/EVPN configuration builder
- MLAG automation

### File: `arista/cvp_api.py`
**Future Capabilities:**
- Configlet lifecycle management
- Zero-touch provisioning workflows
- Container-based topology automation

---

## 5. Palo Alto Networks

### File: `paloalto/panorama_api.py`
**Future Capabilities:**
- Security policy automation
- NAT/object management
- Commit/publish operations
- Device onboarding

---

## 6. Fortinet

### File: `fortinet/fortigate_api.py`
**Future Capabilities:**
- Firewall rule automation
- Object creation (hosts, services)
- Backup retrieval/restore
- Policy packages

---

## 7. VMware

### File: `vmware/nsxt_api.py`
**Future Capabilities:**
- Segment creation workflows
- Tier-0 and Tier-1 gateway provisioning
- Firewall/security policy automation

### File: `vmware/vcenter_api.py`
**Future Capabilities:**
- VM lifecycle automation
- VM cloning and template deployment
- Host and cluster operations

---

## 8. Check Point

### File: `checkpoint/mgmt_api.py`
**Future Capabilities:**
- Install-policy automation
- Object and NAT policy workflows
- Advanced search and rule audit

---

## 9. Huawei

### File: `huawei/cloudengine_api.py`
**Future Capabilities:**
- NETCONF/YANG workflows
- EVPN/L2/L3 templates
- Device inventory automation

---

## 10. Aruba

### File: `aruba/aruba_api.py`
**Future Capabilities:**
- Central API integration
- Wireless profile automation
- Switch provisioning templates

---

## 11. AWS Modules

### File: `aws/vpc_api.py`
**Future Capabilities:**
- VPC creation workflows
- Route table and subnet auto-builders

### File: `aws/tgw_api.py`
**Future Capabilities:**
- TGW route propagation
- Multi-VPC topology generator

### File: `aws/sg_api.py`
**Current and Future Capabilities:**
- Automated compliance engine
- Cross-environment rule comparison
- Unused rule detection
- Flow Log integration (future)

### File: `aws/route_table_api.py`
**Future Capabilities:**
- Route validation
- Auto-route injection

### File: `aws/igw_api.py`
**Future Capabilities:**
- Automated IGW provisioning
- Auto-routing post-attachment

### File: `aws/nat_api.py`
**Future Capabilities:**
- Multi-AZ auto failover
- Resilient NAT autoscaling

### File: `aws/eip_api.py`
**Future Capabilities:**
- Auto-association with instances
- EIP lifecycle management

### File: `aws/elb_api.py`
**Future Capabilities:**
- Listener/Rule automation
- Target group health audits

### File: `aws/peering_api.py`
**Future Capabilities:**
- Automated route propagation checks
- Cross-account peering workflows

### File: `aws/monitoring_api.py`
**Future Capabilities:**
- Multi-metric dashboards
- CloudWatch alarm automation

---

## This file will be updated as new vendors and modules are added.


---

## 12. Azure Modules

### File: `azure/vnet_api.py`
**Future Capabilities:**
- VNet creation workflows
- Subnet provisioning
- NSG creation/attachment
- Route table automation
- Cross-region VNet peering
- Private Link and service endpoints automation


### File: `azure/nsg_api.py`
**Future Capabilities:**
- NSG creation and deletion
- Automated security rule provisioning
- Cross-region NSG comparison
- Compliance checks (zero trust policies)
- Detection of shadowed or redundant rules
- Auto-removal of unused rules


### File: `azure/lb_api.py`
**Future Capabilities:**
- Public/Private LB creation
- Backend pool management
- Dynamic backend pool membership (scale sets)
- Health probe integration
- HTTP/HTTPS rule automation
- Cross-zone load balancing
- High availability configuration


### File: `azure/vwan_api.py`
**Future Capabilities:**
- Virtual WAN provisioning
- Virtual Hub creation and routing configuration
- VPN / ExpressRoute / SD-WAN gateway integration
- Hub-to-hub global transit automation
- Automated spoke onboarding into vWAN
- Traffic inspection & firewall policy integration


### File: `azure/private_link_api.py`
**Future Capabilities:**
- Private Endpoint creation
- Automatic subnet + NIC provisioning
- Private DNS zone linking
- Private Link Service creation (custom services)
- Full end-to-end service publishing workflows
- Traffic inspection integration with Azure Firewall or NVAs


---

## 13. GCP Modules

### File: `gcp/gcp_vpc_api.py`
**Future Capabilities:**
- VPC network creation
- Subnet creation with regional selection
- Global dynamic routing configuration
- Firewall rules automation
- VPC peering workflows
- Shared VPC (Host/Service project automation)
- Private Service Connect integration


### File: `gcp/gcp_firewall_api.py`
**Future Capabilities:**
- Firewall rule creation and update
- Automated compliance engine (like AWS SG)
- Rule comparison across environments
- Shadowed rule detection
- Risky rule identification (0.0.0.0/0)
- Bulk rule import/export for migrations


### File: `gcp/gcp_lb_api.py`
**Future Capabilities:**
- Full HTTP(S) global load balancer creation
- Backend service provisioning (instance groups, NEG)
- Health check automation
- Forwarding rules and listener automation
- Multi-region routing and failover
- LB → Cloud Armor → CDN pipeline automation


### File: `gcp/gcp_router_api.py`
**Future Capabilities:**
- Cloud Router creation workflows
- Automated BGP peer provisioning
- Route policy automation
- VPN / Interconnect hybrid routing orchestration
- Dynamic routing diagrams and topology inference
- Cross-region routing consistency checks


### File: `gcp/gcp_nat_api.py`
**Future Capabilities:**
- NAT gateway creation workflows
- Automatic NAT IP assignment and scaling
- Cloud Router NAT attachment automation
- Advanced NAT policies (drain mode, failover)
- Global multi-region NAT strategy builder
- Integrate NAT logs into compliance engine


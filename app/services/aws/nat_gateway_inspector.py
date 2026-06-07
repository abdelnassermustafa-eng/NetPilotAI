from __future__ import annotations

import boto3


class NatGatewayInspector:
    """
    Read-only inspector for NAT Gateways within a VPC.
    Produces a summary + details payload suitable for validation UI.
    """

    def __init__(self):
        self.ec2 = boto3.client("ec2")

    @staticmethod
    def _extract_default_routes_to_nat(route_tables: list[dict]) -> dict[str, list[dict]]:
        """
        Build a mapping:
          nat_gateway_id -> [{route_table_id, destination}, ...]
        We only include routes where destination == 0.0.0.0/0 and target is NatGatewayId.
        """
        mapping: dict[str, list[dict]] = {}
        for rt in route_tables:
            rt_id = rt.get("RouteTableId")
            for route in rt.get("Routes", []):
                if route.get("DestinationCidrBlock") == "0.0.0.0/0" and route.get("NatGatewayId"):
                    nat_id = route["NatGatewayId"]
                    mapping.setdefault(nat_id, []).append(
                        {"route_table_id": rt_id, "destination": "0.0.0.0/0"}
                    )
        return mapping

    @staticmethod
    def _count_by_state(nats: list[dict]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for nat in nats:
            st = nat.get("State", "unknown")
            counts[st] = counts.get(st, 0) + 1
        return counts

    def inspect_vpc_nat_gateways(self, vpc_id: str) -> dict:
        # --------------------------------------------------
        # 1) NAT Gateways in this VPC
        # --------------------------------------------------
        nats_resp = self.ec2.describe_nat_gateways(
            Filter=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        nat_gateways = nats_resp.get("NatGateways", [])

        # --------------------------------------------------
        # 2) Route tables in this VPC (to detect NAT references)
        # --------------------------------------------------
        rts_resp = self.ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        route_tables = rts_resp.get("RouteTables", [])
        nat_references = self._extract_default_routes_to_nat(route_tables)

        # --------------------------------------------------
        # 3) Subnet -> AZ mapping (for NAT placement)
        # --------------------------------------------------
        subnets_resp = self.ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        subnet_az: dict[str, str] = {
            s["SubnetId"]: s.get("AvailabilityZone", "unknown")
            for s in subnets_resp.get("Subnets", [])
        }

        # --------------------------------------------------
        # 4) ENIs in this VPC (to map NAT ENIs)
        #    NAT creates ENIs; we map ENI -> NAT by Description "Interface for NAT Gateway ..."
        # --------------------------------------------------
        enis_resp = self.ec2.describe_network_interfaces(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        enis = enis_resp.get("NetworkInterfaces", [])

        nat_enis: dict[str, list[dict]] = {}
        for eni in enis:
            desc = eni.get("Description", "") or ""
            # Common format: "Interface for NAT Gateway nat-xxxxxxxx"
            if "NAT Gateway" in desc and "nat-" in desc:
                # Extract nat- id
                # Best-effort parse: take last token containing nat-
                nat_id = None
                for token in desc.split():
                    if token.startswith("nat-"):
                        nat_id = token
                if nat_id:
                    nat_enis.setdefault(nat_id, []).append(
                        {
                            "eni_id": eni["NetworkInterfaceId"],
                            "status": eni.get("Status", "unknown"),
                        }
                    )

        # --------------------------------------------------
        # Build details objects
        # --------------------------------------------------
        details: list[dict] = []
        unique_subnets = set()
        eip_count = 0
        rtb_referencing_nat = set()

        for nat in nat_gateways:
            nat_id = nat["NatGatewayId"]
            state = nat.get("State", "unknown")
            subnet_id = nat.get("SubnetId")
            az = subnet_az.get(subnet_id, "unknown")

            unique_subnets.add(subnet_id)

            # Elastic IPs
            elastic_ips: list[dict] = []
            for addr in nat.get("NatGatewayAddresses", []):
                alloc_id = addr.get("AllocationId")
                pub_ip = addr.get("PublicIp")
                if alloc_id or pub_ip:
                    elastic_ips.append(
                        {"allocation_id": alloc_id, "public_ip": pub_ip}
                    )

            eip_count += len(elastic_ips)

            # Route table references (default routes)
            referenced_by = nat_references.get(nat_id, [])
            for ref in referenced_by:
                if ref.get("route_table_id"):
                    rtb_referencing_nat.add(ref["route_table_id"])

            # ENIs
            nat_eni_list = nat_enis.get(nat_id, [])

            # State reason (if available)
            state_reason = None
            failure_message = nat.get("FailureMessage")
            if failure_message:
                state_reason = failure_message

            details.append(
                {
                    "nat_gateway_id": nat_id,
                    "state": state,
                    "subnet": {
                        "subnet_id": subnet_id,
                        "availability_zone": az,
                    },
                    "elastic_ips": elastic_ips,
                    "network_interfaces": nat_eni_list,
                    "referenced_by_route_tables": referenced_by,
                    "state_reason": state_reason,
                }
            )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------
        state_counts = self._count_by_state(nat_gateways)

        summary = {
            "total_nat_gateways": len(details),
            "available_nat_gateways": state_counts.get("available", 0),
            "pending_nat_gateways": state_counts.get("pending", 0),
            "failed_nat_gateways": state_counts.get("failed", 0),
            "subnets_with_nat": len(unique_subnets) if details else 0,
            "route_tables_referencing_nat": len(rtb_referencing_nat),
            "elastic_ips_attached": eip_count,
        }

        return {
            "vpc_id": vpc_id,
            "summary": summary,
            "details": details,
        }


from __future__ import annotations

import boto3


class VPCInspector:
    def __init__(self):
        self.ec2 = boto3.client("ec2")

    def inspect(self, vpc_id: str) -> dict:
        summary = {
            "subnets": 0,
            "internet_gateways": 0,
            "nat_gateways": 0,
            "route_tables": 0,
            "security_groups": 0,
            "network_interfaces": 0,
        }

        details = {
            "subnets": [],
            "internet_gateways": [],
            "nat_gateways": [],
            "route_tables": [],
            "network_interfaces": [],
        }

        # --------------------------------------------------
        # Subnets
        # --------------------------------------------------
        subnets_resp = self.ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        for s in subnets_resp.get("Subnets", []):
            details["subnets"].append(
                {
                    "subnet_id": s["SubnetId"],
                    "cidr": s["CidrBlock"],
                    "availability_zone": s["AvailabilityZone"],
                }
            )

        summary["subnets"] = len(details["subnets"])

        # --------------------------------------------------
        # Internet Gateways
        # --------------------------------------------------
        igws_resp = self.ec2.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )
        for igw in igws_resp.get("InternetGateways", []):
            details["internet_gateways"].append(
                {
                    "internet_gateway_id": igw["InternetGatewayId"],
                    "attached": True,
                }
            )

        summary["internet_gateways"] = len(details["internet_gateways"])

        # --------------------------------------------------
        # NAT Gateways
        # --------------------------------------------------
        nats_resp = self.ec2.describe_nat_gateways(
            Filter=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        for nat in nats_resp.get("NatGateways", []):
            allocation_id = None
            if nat.get("NatGatewayAddresses"):
                allocation_id = nat["NatGatewayAddresses"][0].get("AllocationId")

            details["nat_gateways"].append(
                {
                    "nat_gateway_id": nat["NatGatewayId"],
                    "subnet_id": nat["SubnetId"],
                    "elastic_ip_allocation_id": allocation_id,
                    "state": nat["State"],
                }
            )

        summary["nat_gateways"] = len(details["nat_gateways"])

        # --------------------------------------------------
        # Route Tables
        # --------------------------------------------------
        rts_resp = self.ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        for rt in rts_resp.get("RouteTables", []):
            associations = rt.get("Associations", [])
            is_main = any(a.get("Main") for a in associations)

            details["route_tables"].append(
                {
                    "route_table_id": rt["RouteTableId"],
                    "is_main": is_main,
                    "association_count": len(associations),
                }
            )

        summary["route_tables"] = len(details["route_tables"])

        # --------------------------------------------------
        # Network Interfaces (ENIs)
        # --------------------------------------------------
        enis_resp = self.ec2.describe_network_interfaces(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        for eni in enis_resp.get("NetworkInterfaces", []):
            details["network_interfaces"].append(
                {
                    "network_interface_id": eni["NetworkInterfaceId"],
                    "subnet_id": eni["SubnetId"],
                    "status": eni["Status"],
                }
            )

        summary["network_interfaces"] = len(details["network_interfaces"])

        # --------------------------------------------------
        # Final Evaluation
        # --------------------------------------------------
        deletable = all(count == 0 for count in summary.values())

        return {
            "vpc_id": vpc_id,
            "deletable": deletable,
            "summary": summary,
            "details": details,
        }

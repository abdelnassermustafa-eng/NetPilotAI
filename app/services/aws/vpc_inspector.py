from __future__ import annotations

import boto3


class VPCInspector:
    def __init__(self):
        self.ec2 = boto3.client("ec2")

    def inspect(self, vpc_id: str) -> dict:
        deps = {
            "subnets": 0,
            "internet_gateways": 0,
            "nat_gateways": 0,
            "route_tables": 0,
            "security_groups": 0,
            "network_interfaces": 0,
        }

        # Subnets
        subnets = self.ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        deps["subnets"] = len(subnets.get("Subnets", []))

        # Internet Gateways
        igws = self.ec2.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )
        deps["internet_gateways"] = len(igws.get("InternetGateways", []))

        # NAT Gateways
        nats = self.ec2.describe_nat_gateways(
            Filter=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        deps["nat_gateways"] = len(nats.get("NatGateways", []))

        # Route Tables
        rts = self.ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        deps["route_tables"] = len(rts.get("RouteTables", []))

        # Security Groups (exclude default)
        sgs = self.ec2.describe_security_groups(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        deps["security_groups"] = len(
            [sg for sg in sgs.get("SecurityGroups", []) if sg["GroupName"] != "default"]
        )

        # Network Interfaces
        enis = self.ec2.describe_network_interfaces(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        deps["network_interfaces"] = len(enis.get("NetworkInterfaces", []))

        deletable = all(count == 0 for count in deps.values())

        return {
            "vpc_id": vpc_id,
            "deletable": deletable,
            "dependencies": deps,
        }

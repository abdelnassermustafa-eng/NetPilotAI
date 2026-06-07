from __future__ import annotations

import boto3


class InternetGatewayInspector:
    """
    Read-only inspector for Internet Gateways within a VPC.
    Produces a summary + details payload suitable for validation UI.
    """

    def __init__(self):
        self.ec2 = boto3.client("ec2")

    def inspect_vpc_internet_gateways(self, vpc_id: str) -> dict:
        # --------------------------------------------------
        # 1) Discover IGWs attached to this VPC
        # --------------------------------------------------
        igws_resp = self.ec2.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )
        igws = igws_resp.get("InternetGateways", [])

        # --------------------------------------------------
        # 2) Discover route tables (to find IGW references)
        # --------------------------------------------------
        rts_resp = self.ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        route_tables = rts_resp.get("RouteTables", [])

        details: list[dict] = []
        route_tables_referencing_igw = set()
        default_routes_to_igw = 0

        for igw in igws:
            igw_id = igw["InternetGatewayId"]

            # Attachment info
            attachments = igw.get("Attachments", [])
            attached_vpc_id = None
            attachment_state = "detached"

            for att in attachments:
                if att.get("VpcId") == vpc_id:
                    attached_vpc_id = vpc_id
                    attachment_state = "attached"

            referenced_by: list[dict] = []

            # Scan route tables for IGW usage
            for rt in route_tables:
                for route in rt.get("Routes", []):
                    if route.get("GatewayId") == igw_id:
                        destination = (
                            route.get("DestinationCidrBlock")
                            or route.get("DestinationIpv6CidrBlock")
                            or route.get("DestinationPrefixListId")
                            or "unknown"
                        )

                        referenced_by.append(
                            {
                                "route_table_id": rt["RouteTableId"],
                                "destination": destination,
                            }
                        )

                        route_tables_referencing_igw.add(rt["RouteTableId"])

                        if destination == "0.0.0.0/0":
                            default_routes_to_igw += 1

            # Derive state
            if referenced_by:
                state = "in-use"
            elif attachment_state == "attached":
                state = "attached"
            else:
                state = "detached"

            details.append(
                {
                    "internet_gateway_id": igw_id,
                    "attachment_state": attachment_state,
                    "attached_vpc_id": attached_vpc_id,
                    "referenced_by_route_tables": referenced_by,
                    "state": state,
                }
            )

        summary = {
            "total_igws": len(details),
            "attached_igws": len([d for d in details if d["attachment_state"] == "attached"]),
            "detached_igws": len([d for d in details if d["attachment_state"] != "attached"]),
            "route_tables_referencing_igw": len(route_tables_referencing_igw),
            "default_routes_to_igw": default_routes_to_igw,
        }

        return {
            "vpc_id": vpc_id,
            "summary": summary,
            "details": details,
        }

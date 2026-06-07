from __future__ import annotations

import boto3


class RouteTableInspector:
    """
    Read-only inspector for route tables within a VPC.
    Produces a UI-friendly summary + details payload.
    """

    def __init__(self):
        self.ec2 = boto3.client("ec2")

    @staticmethod
    def _simplify_route(route: dict) -> dict:
        # Destination: prefer IPv4, else IPv6, else prefix list
        destination = (
            route.get("DestinationCidrBlock")
            or route.get("DestinationIpv6CidrBlock")
            or route.get("DestinationPrefixListId")
            or "unknown"
        )

        # Target detection (one of these may exist)
        if route.get("GatewayId"):
            target_id = route["GatewayId"]
            target_type = "internet_gateway" if target_id.startswith("igw-") else "gateway"
        elif route.get("NatGatewayId"):
            target_id = route["NatGatewayId"]
            target_type = "nat_gateway"
        elif route.get("TransitGatewayId"):
            target_id = route["TransitGatewayId"]
            target_type = "transit_gateway"
        elif route.get("VpcPeeringConnectionId"):
            target_id = route["VpcPeeringConnectionId"]
            target_type = "vpc_peering"
        elif route.get("VpcEndpointId"):
            target_id = route["VpcEndpointId"]
            target_type = "vpc_endpoint"
        elif route.get("NetworkInterfaceId"):
            target_id = route["NetworkInterfaceId"]
            target_type = "network_interface"
        elif route.get("InstanceId"):
            target_id = route["InstanceId"]
            target_type = "instance"
        else:
            # local routes have GatewayId == 'local' normally, but fallback anyway
            target_id = route.get("GatewayId") or "local"
            target_type = "local" if target_id == "local" else "unknown"

        return {
            "destination": destination,
            "target_type": target_type,
            "target_id": target_id,
            "state": route.get("State", "unknown"),
            "origin": route.get("Origin", "unknown"),
        }

    @staticmethod
    def _simplify_association(assoc: dict) -> dict:
        if assoc.get("SubnetId"):
            return {"type": "subnet", "subnet_id": assoc["SubnetId"], "main": bool(assoc.get("Main", False))}
        # Main association may have no SubnetId
        return {"type": "main", "subnet_id": None, "main": bool(assoc.get("Main", False))}

    @staticmethod
    def _derive_state(is_main: bool, assoc_count: int) -> str:
        if is_main:
            return "main"
        if assoc_count == 0:
            return "orphaned"
        return "in-use"

    def inspect_vpc_route_tables(self, vpc_id: str) -> dict:
        rts_resp = self.ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        route_tables = rts_resp.get("RouteTables", [])

        details: list[dict] = []

        for rt in route_tables:
            associations = rt.get("Associations", [])
            is_main = any(a.get("Main") for a in associations)

            simplified_assocs = [self._simplify_association(a) for a in associations]
            simplified_routes = [self._simplify_route(r) for r in rt.get("Routes", [])]

            assoc_count = len([a for a in simplified_assocs if a.get("type") == "subnet"])
            state = self._derive_state(is_main=is_main, assoc_count=assoc_count)

            # Count default route presence (IPv4)
            has_default_route = any(r.get("destination") == "0.0.0.0/0" for r in simplified_routes)

            details.append(
                {
                    "route_table_id": rt["RouteTableId"],
                    "is_main": is_main,
                    "associations": simplified_assocs,
                    "association_count": assoc_count,
                    "routes": simplified_routes,
                    "route_count": len(simplified_routes),
                    "has_default_route": has_default_route,
                    "state": state,
                }
            )

        total = len(details)
        main_count = len([d for d in details if d["is_main"]])
        non_main = total - main_count
        orphaned = len([d for d in details if d["state"] == "orphaned"])
        with_default = len([d for d in details if d["has_default_route"]])

        summary = {
            "total_route_tables": total,
            "main_route_tables": main_count,
            "non_main_route_tables": non_main,
            "orphaned_route_tables": orphaned,
            "route_tables_with_default_route": with_default,
        }

        return {
            "vpc_id": vpc_id,
            "summary": summary,
            "details": details,
        }


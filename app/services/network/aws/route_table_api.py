import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.exceptions import ClientError


class AWSRouteTableManager:
    def __init__(self, region: str = "us-east-1"):
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
            self.ec2_resource = session.resource("ec2", region_name=region)
        except Exception:
            self.ec2 = None
            self.ec2_resource = None

    def disassociate(self, association_id: str):
        """
        Disassociate a subnet from a route table.
        """
        try:
            self.ec2.disassociate_route_table(AssociationId=association_id)

            return {"status": "success", "association_id": association_id}

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # ---------------------------------------------------------
    # ASSOCIATE / REPLACE ROUTE TABLE (AWS-SAFE)
    # ---------------------------------------------------------
    def associate_route_table(self, rtb_id: str, subnet_id: str):
        try:
            # Step 1: Check existing association for this subnet
            response = self.ec2.describe_route_tables(
                Filters=[
                    {
                        "Name": "association.subnet-id",
                        "Values": [subnet_id],
                    }
                ]
            )

            associations = []
            for rt in response.get("RouteTables", []):
                for assoc in rt.get("Associations", []):
                    if assoc.get("SubnetId") == subnet_id:
                        associations.append(assoc)

            # Step 2: Replace association if one exists (MOST COMMON CASE)
            if associations:
                association_id = associations[0]["RouteTableAssociationId"]

                self.ec2.replace_route_table_association(
                    AssociationId=association_id,
                    RouteTableId=rtb_id,
                )

                return {
                    "status": "success",
                    "action": "replaced",
                    "route_table_id": rtb_id,
                    "subnet_id": subnet_id,
                    "association_id": association_id,
                }

            # Step 3: Otherwise associate normally (RARE CASE)
            result = self.ec2.associate_route_table(
                RouteTableId=rtb_id,
                SubnetId=subnet_id,
            )

            return {
                "status": "success",
                "action": "associated",
                "route_table_id": rtb_id,
                "subnet_id": subnet_id,
                "association_id": result["AssociationId"],
            }

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
            }

    # ---------------------------------------------------------
    # CREATE ROUTE TABLE
    # ---------------------------------------------------------
    def create_route_table(self, vpc_id: str, name: str, description: str):
        try:
            response = self.ec2.create_route_table(VpcId=vpc_id)
            rtb_id = response["RouteTable"]["RouteTableId"]

            # Tags
            tags = [{"Key": "Name", "Value": name}]
            if description:
                tags.append({"Key": "Description", "Value": description})

            self.ec2.create_tags(Resources=[rtb_id], Tags=tags)

            return {"status": "success", "route_table_id": rtb_id, "vpc_id": vpc_id}

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # DELETE ROUTE TABLE
    # ---------------------------------------------------------
    def delete_route_table(self, rtb_id: str):
        try:
            self.ec2.delete_route_table(RouteTableId=rtb_id)
            return {"status": "success", "route_table_id": rtb_id}
        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

            # ---------------------------------------------------------
            # LIST ROUTE TABLES
            # ---------------------------------------------------------
            return {"status": "failed", "route_tables": []}

    # ---------------------------------------------------------
    # ASSOCIATE SUBNET
    # ---------------------------------------------------------
    def associate_subnet(self, rtb_id: str, subnet_id: str):
        try:
            response = self.ec2.associate_route_table(
                RouteTableId=rtb_id, SubnetId=subnet_id
            )

            return {"status": "success", "association_id": response["AssociationId"]}

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # CREATE ROUTE
    # ---------------------------------------------------------
    def create_route(
        self,
        route_table_id: str,
        destination_cidr: str,
        target_type: str,
        target_id: str,
    ):
        """
        target_type: 'igw', 'nat', 'instance', 'tgw', 'vpc_peering'
        destination_cidr: IPv4 or IPv6 CIDR
        """
        if not route_table_id or not destination_cidr or not target_type:
            return {
                "status": "failed",
                "error": "route_table_id, destination_cidr, and target_type are required.",
            }

        params = {
            "RouteTableId": route_table_id,
        }

        # IPv4 vs IPv6
        if ":" in destination_cidr:
            params["DestinationIpv6CidrBlock"] = destination_cidr
        else:
            params["DestinationCidrBlock"] = destination_cidr

        # Target mapping
        if target_type == "igw":
            params["GatewayId"] = target_id
        elif target_type == "nat":
            params["NatGatewayId"] = target_id
        elif target_type == "instance":
            params["InstanceId"] = target_id
        elif target_type == "tgw":
            params["TransitGatewayId"] = target_id
        elif target_type == "vpc_peering":
            params["VpcPeeringConnectionId"] = target_id
        else:
            return {
                "status": "failed",
                "error": f"Unsupported target_type: {target_type}",
            }

        try:
            self.ec2.create_route(**params)
            return {
                "status": "success",
                "route_table_id": route_table_id,
                "destination_cidr": destination_cidr,
                "target_type": target_type,
                "target_id": target_id,
            }
        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # DELETE ROUTE
    # ---------------------------------------------------------
    def delete_route(self, route_table_id: str, destination_cidr: str):
        """
        Delete a route by its destination CIDR (IPv4 or IPv6).
        """
        if not route_table_id or not destination_cidr:
            return {
                "status": "failed",
                "error": "route_table_id and destination_cidr are required.",
            }

        params = {"RouteTableId": route_table_id}

        if ":" in destination_cidr:
            params["DestinationIpv6CidrBlock"] = destination_cidr
        else:
            params["DestinationCidrBlock"] = destination_cidr

        try:
            self.ec2.delete_route(**params)
            return {
                "status": "success",
                "route_table_id": route_table_id,
                "destination_cidr": destination_cidr,
            }
        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # LIST ROUTE TABLES
    # ---------------------------------------------------------
    def list_route_tables(self):
        try:
            response = self.ec2.describe_route_tables()
            route_tables = []

            for rt in response["RouteTables"]:
                associations = []
                associations_details = []
                is_main = False

                for assoc in rt.get("Associations", []):
                    if assoc.get("Main"):
                        is_main = True

                    associations_details.append(
                        {
                            "association_id": assoc.get("RouteTableAssociationId"),
                            "subnet_id": assoc.get("SubnetId"),
                            "main": assoc.get("Main", False),
                        }
                    )

                    if assoc.get("SubnetId"):
                        associations.append(assoc["SubnetId"])

                routes = []
                for r in rt.get("Routes", []):
                    cidr = r.get("DestinationCidrBlock") or r.get(
                        "DestinationIpv6CidrBlock"
                    )

                    target = (
                        r.get("GatewayId")
                        or r.get("NatGatewayId")
                        or r.get("TransitGatewayId")
                        or r.get("InstanceId")
                        or r.get("VpcPeeringConnectionId")
                        or "local"
                    )

                    if cidr:
                        routes.append({"cidr": cidr, "target": target})

                route_tables.append(
                    {
                        "route_table_id": rt["RouteTableId"],
                        "vpc_id": rt["VpcId"],
                        "is_main": is_main,
                        "associations": associations,
                        "associations_details": associations_details,
                        "routes": routes,
                    }
                )

            return {"status": "success", "route_tables": route_tables}

        except (ClientError, NoCredentialsError) as e:
            return {"status": "failed", "error": str(e), "route_tables": []}

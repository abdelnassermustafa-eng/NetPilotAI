import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSVPCManager:
    def __init__(self, region: str = "us-east-1"):
        """
        Simple wrapper around EC2 / VPC functionality.

        If session or client creation fails (e.g., missing credentials),
        we set clients to None. The list_* methods will then return
        placeholders instead of crashing.
        """
        try:
            self.session = boto3.session.Session()
            self.ec2 = self.session.client("ec2", region_name=region)
            self.ec2_resource = self.session.resource("ec2", region_name=region)
        except Exception:
            # Fallbacks so the app can still render UI without hard failure.
            self.ec2 = None
            self.ec2_resource = None

    # =====================================================================
    # VPC OPERATIONS
    # =====================================================================

    # -------------------------------------------------------
    # CREATE VPC
    # -------------------------------------------------------
    def create_vpc(self, cidr: str = "10.0.0.0/16"):
        """Create a new VPC with a friendly tag."""
        if not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 client not initialized (check AWS credentials / config).",
            }

        try:
            response = self.ec2.create_vpc(CidrBlock=cidr)
            vpc_id = response["Vpc"]["VpcId"]

            # Tag for readability in console
            self.ec2.create_tags(
                Resources=[vpc_id], Tags=[{"Key": "Name", "Value": "NetPilot-VPC"}]
            )

            return {"status": "created", "vpc_id": vpc_id, "cidr": cidr}

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for VPC creation."
            )
            return {"status": "failed", "error": message}

    # -------------------------------------------------------
    # SIMPLE DELETE (NO DEPENDENCY REMOVAL)
    # -------------------------------------------------------
    def delete_vpc_simple(self, vpc_id: str):
        """
        Delete a VPC directly.
        Fails if dependencies exist (subnets, IGWs, etc.).
        """
        if not self.ec2:
            return {
                "status": "failed",
                "vpc_id": vpc_id,
                "error": "EC2 client not initialized (check AWS credentials / config).",
            }

        try:
            self.ec2.delete_vpc(VpcId=vpc_id)
            return {"status": "deleted", "vpc_id": vpc_id}
        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for VPC deletion."
            )
            return {
                "status": "failed",
                "vpc_id": vpc_id,
                "error": message,
            }

    # -------------------------------------------------------
    # SAFE DELETE (REMOVE DEPENDENCIES FIRST)
    # -------------------------------------------------------
    def delete_vpc_safe(self, vpc_id: str):
        """
        Safely delete a VPC and its dependent resources.
        """
        if not self.ec2_resource or not self.ec2:
            return {
                "status": "failed",
                "vpc_id": vpc_id,
                "error": "EC2 resource/client not initialized (check AWS credentials).",
            }

        logs = []

        try:
            vpc = self.ec2_resource.Vpc(vpc_id)
        except Exception as e:
            return {
                "status": "failed",
                "vpc_id": vpc_id,
                "error": f"Unable to load VPC resource: {e}",
                "steps": logs,
            }

        try:
            # ---- Delete Internet Gateways ----
            for igw in vpc.internet_gateways.all():
                igw.detach_from_vpc(VpcId=vpc_id)
                logs.append(f"Detached {igw.id} from VPC")
                igw.delete()
                logs.append(f"Deleted Internet Gateway {igw.id}")

            # ---- Delete Subnets ----
            for subnet in vpc.subnets.all():
                subnet.delete()
                logs.append(f"Deleted Subnet {subnet.id}")

            # ---- Delete Route Tables ----
            for rtb in vpc.route_tables.all():
                # keep main route table
                if not any(assoc.main for assoc in rtb.associations):
                    rtb.delete()
                    logs.append(f"Deleted Route Table {rtb.id}")

            # ---- Delete Security Groups ----
            for sg in vpc.security_groups.all():
                if sg.group_name != "default":
                    sg.delete()
                    logs.append(f"Deleted Security Group {sg.id}")

            # ---- Delete Network ACLs ----
            for acl in vpc.network_acls.all():
                if not acl.is_default:
                    acl.delete()
                    logs.append(f"Deleted Network ACL {acl.id}")

            # ---- Delete VPC Endpoints ----
            endpoints = self.ec2.describe_vpc_endpoints(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            ).get("VpcEndpoints", [])

            for ep in endpoints:
                self.ec2.delete_vpc_endpoints(VpcEndpointIds=[ep["VpcEndpointId"]])
                logs.append(f"Deleted VPC Endpoint {ep['VpcEndpointId']}")

            # ---- Finally delete the VPC ----
            vpc.delete()
            logs.append(f"Deleted VPC {vpc_id}")
            return {"status": "success", "vpc_id": vpc_id, "steps": logs}

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for safe VPC deletion."
            )
            return {
                "status": "failed",
                "vpc_id": vpc_id,
                "error": message,
                "steps": logs,
            }

    # -------------------------------------------------------
    # LIST VPCS
    # -------------------------------------------------------
    def list_vpcs(self):
        """Return all VPCs in the region."""
        if not self.ec2:
            # Offline / no-credentials friendly placeholder
            return {
                "count": 1,
                "vpcs": [
                    {
                        "vpc_id": "vpc-placeholder",
                        "cidr": "10.0.0.0/16",
                        "state": "available",
                        "is_default": False,
                        "tags": [{"Key": "Name", "Value": "Demo-VPC"}],
                    }
                ],
            }

        try:
            response = self.ec2.describe_vpcs()
            vpcs = [
                {
                    "vpc_id": v.get("VpcId"),
                    "cidr": v.get("CidrBlock"),
                    "state": v.get("State"),
                    "is_default": v.get("IsDefault"),
                    "tags": v.get("Tags", []),
                }
                for v in response.get("Vpcs", [])
            ]

            return {"count": len(vpcs), "vpcs": vpcs}

        except (ClientError, NoCredentialsError):
            # Fall back to a placeholder so UI still renders
            return {
                "count": 1,
                "vpcs": [
                    {
                        "vpc_id": "vpc-placeholder",
                        "cidr": "10.0.0.0/16",
                        "state": "unknown",
                        "is_default": False,
                        "tags": [],
                    }
                ],
            }

    # =====================================================================
    # SUBNET OPERATIONS (SUBNET PHASE — A)
    # =====================================================================

    # -------------------------------------------------------
    # LIST SUBNETS (OPTIONAL FILTER BY VPC)
    # -------------------------------------------------------
    def list_subnets(self, vpc_id: str | None = None):
        """
        Return all subnets, optionally filtered by VPC.

        :param vpc_id: if provided, only subnets in this VPC are returned.
        """
        if not self.ec2:
            return {
                "count": 1,
                "subnets": [
                    {
                        "subnet_id": "subnet-placeholder",
                        "vpc_id": "vpc-placeholder",
                        "cidr": "10.0.1.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "available",
                        "tags": [{"Key": "Name", "Value": "Demo-Subnet"}],
                    }
                ],
            }

        try:
            params = {}
            if vpc_id:
                params["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]

            response = self.ec2.describe_subnets(**params)
            subnets = [
                {
                    "subnet_id": s.get("SubnetId"),
                    "vpc_id": s.get("VpcId"),
                    "cidr": s.get("CidrBlock"),
                    "availability_zone": s.get("AvailabilityZone"),
                    "state": s.get("State"),
                    "tags": s.get("Tags", []),
                }
                for s in response.get("Subnets", [])
            ]

            return {"count": len(subnets), "subnets": subnets}

        except (ClientError, NoCredentialsError):
            return {
                "count": 1,
                "subnets": [
                    {
                        "subnet_id": "subnet-placeholder",
                        "vpc_id": vpc_id or "vpc-placeholder",
                        "cidr": "10.0.1.0/24",
                        "availability_zone": "us-east-1a",
                        "state": "unknown",
                        "tags": [],
                    }
                ],
            }

    # -------------------------------------------------------
    # CREATE SUBNET
    # -------------------------------------------------------
    def create_subnet(
        self,
        vpc_id: str,
        cidr: str,
        availability_zone: str | None = None,
        name: str | None = "NetPilot-Subnet",
    ):
        """
        Create a subnet in a given VPC.

        :param vpc_id: target VPC ID
        :param cidr: subnet CIDR, e.g. 10.0.1.0/24
        :param availability_zone: optional AZ (e.g. us-east-1a)
        :param name: optional Name tag
        """
        if not self.ec2_resource or not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 resource/client not initialized (check AWS credentials).",
            }

        try:
            create_args = {"VpcId": vpc_id, "CidrBlock": cidr}
            if availability_zone:
                create_args["AvailabilityZone"] = availability_zone

            subnet = self.ec2_resource.create_subnet(**create_args)

            if name:
                self.ec2.create_tags(
                    Resources=[subnet.id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            # Refresh attributes
            subnet.load()

            return {
                "status": "created",
                "subnet_id": subnet.id,
                "vpc_id": subnet.vpc_id,
                "cidr": subnet.cidr_block,
                "availability_zone": subnet.availability_zone,
            }

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for subnet creation."
            )
            return {
                "status": "failed",
                "error": message,
                "vpc_id": vpc_id,
                "cidr": cidr,
            }

    # -------------------------------------------------------
    # DELETE SUBNET
    # -------------------------------------------------------
    def delete_subnet(self, subnet_id: str):
        """
        Delete a subnet by ID.
        """
        if not self.ec2_resource:
            return {
                "status": "failed",
                "subnet_id": subnet_id,
                "error": "EC2 resource not initialized (check AWS credentials).",
            }

        try:
            subnet = self.ec2_resource.Subnet(subnet_id)
            vpc_id = subnet.vpc_id
            subnet.delete()

            return {
                "status": "deleted",
                "subnet_id": subnet_id,
                "vpc_id": vpc_id,
            }

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for subnet deletion."
            )
            return {
                "status": "failed",
                "subnet_id": subnet_id,
                "error": message,
            }

    # =====================================================================
    # ROUTE Availability Zones
    # =====================================================================
    def list_availability_zones(self):
        try:
            response = self.ec2.describe_availability_zones(
                Filters=[{"Name": "state", "Values": ["available"]}]
            )
            zones = [z["ZoneName"] for z in response["AvailabilityZones"]]
            return {"availability_zones": zones}
        except Exception as e:
            return {"availability_zones": [], "error": str(e)}

    # -------------------------------------------------------
    # LIST ROUTE TABLES (OPTIONAL FILTER BY VPC)
    # -------------------------------------------------------
    def list_route_tables(self, vpc_id: str | None = None):
        """
        List route tables, optionally filtered by VPC.
        """
        if not self.ec2:
            return {
                "count": 1,
                "route_tables": [
                    {
                        "route_table_id": "rtb-placeholder",
                        "vpc_id": "vpc-placeholder",
                        "is_main": True,
                        "associations": [],
                        "routes": [
                            {"cidr": "10.0.0.0/16", "target": "local"},
                        ],
                        "tags": [],
                    }
                ],
            }

        try:
            params = {}
            if vpc_id:
                params["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]

            response = self.ec2.describe_route_tables(**params)
            rts = []

            for rt in response.get("RouteTables", []):
                rtb_id = rt.get("RouteTableId")
                r_vpc_id = rt.get("VpcId")
                associations = rt.get("Associations", [])
                routes = rt.get("Routes", [])
                tags = rt.get("Tags", [])

                is_main = any(a.get("Main") for a in associations)

                assoc_subnets = [
                    a.get("SubnetId") for a in associations if a.get("SubnetId")
                ]

                simplified_routes = []
                for r in routes:
                    cidr = (
                        r.get("DestinationCidrBlock")
                        or r.get("DestinationIpv6CidrBlock")
                        or "unknown"
                    )
                    target = (
                        r.get("GatewayId")
                        or r.get("NatGatewayId")
                        or r.get("TransitGatewayId")
                        or r.get("InstanceId")
                        or r.get("NetworkInterfaceId")
                        or (
                            "local"
                            if r.get("GatewayId") is None
                            and r.get("NatGatewayId") is None
                            else "unknown"
                        )
                    )
                    simplified_routes.append({"cidr": cidr, "target": target})

                rts.append(
                    {
                        "route_table_id": rtb_id,
                        "vpc_id": r_vpc_id,
                        "is_main": is_main,
                        "associations": assoc_subnets,
                        "routes": simplified_routes,
                        "tags": tags,
                    }
                )

            return {"count": len(rts), "route_tables": rts}

        except (ClientError, NoCredentialsError):
            return {
                "count": 1,
                "route_tables": [
                    {
                        "route_table_id": "rtb-placeholder",
                        "vpc_id": vpc_id or "vpc-placeholder",
                        "is_main": True,
                        "associations": [],
                        "routes": [
                            {"cidr": "10.0.0.0/16", "target": "local"},
                        ],
                        "tags": [],
                    }
                ],
            }

    # -------------------------------------------------------
    # CREATE ROUTE TABLE
    # -------------------------------------------------------
    def create_route_table(self, vpc_id: str, name: str | None = "NetPilot-RTB"):
        """
        Create a non-main route table in the given VPC.
        """
        if not self.ec2_resource or not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 resource/client not initialized (check AWS credentials).",
            }

        try:
            vpc = self.ec2_resource.Vpc(vpc_id)
            rt = vpc.create_route_table()

            if name:
                self.ec2.create_tags(
                    Resources=[rt.id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            rt.load()

            return {
                "status": "created",
                "route_table_id": rt.id,
                "vpc_id": vpc_id,
            }

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for route table creation."
            )
            return {
                "status": "failed",
                "error": message,
                "vpc_id": vpc_id,
            }

    # -------------------------------------------------------
    # DELETE ROUTE TABLE
    # -------------------------------------------------------
    def delete_route_table(self, route_table_id: str):
        """
        Delete a route table.
        Cannot delete main route table.
        """
        if not self.ec2_resource:
            return {
                "status": "failed",
                "route_table_id": route_table_id,
                "error": "EC2 resource not initialized (check AWS credentials).",
            }

        try:
            rt = self.ec2_resource.RouteTable(route_table_id)
            rt.load()

            # Check if main
            for assoc in rt.associations:
                if assoc.main:
                    return {
                        "status": "failed",
                        "route_table_id": route_table_id,
                        "error": "Cannot delete main route table.",
                    }

            # Ensure there are no associations left
            for assoc in rt.associations:
                if assoc.subnet_id:
                    assoc.delete()

            rt.delete()
            return {
                "status": "deleted",
                "route_table_id": route_table_id,
            }

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for route table deletion."
            )
            return {
                "status": "failed",
                "route_table_id": route_table_id,
                "error": message,
            }

    # -------------------------------------------------------
    # ASSOCIATE ROUTE TABLE WITH SUBNET
    # -------------------------------------------------------
    def associate_route_table(self, route_table_id: str, subnet_id: str):
        """
        Associate a route table with a given subnet.
        """
        if not self.ec2:
            return {
                "status": "failed",
                "route_table_id": route_table_id,
                "subnet_id": subnet_id,
                "error": "EC2 client not initialized.",
            }

        try:
            resp = self.ec2.associate_route_table(
                RouteTableId=route_table_id,
                SubnetId=subnet_id,
            )
            assoc_id = resp.get("AssociationId")

            return {
                "status": "associated",
                "route_table_id": route_table_id,
                "subnet_id": subnet_id,
                "association_id": assoc_id,
            }

        except (ClientError, NoCredentialsError) as e:
            message = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else "No AWS credentials found for route table association."
            )
            return {
                "status": "failed",
                "route_table_id": route_table_id,
                "subnet_id": subnet_id,
                "error": message,
            }

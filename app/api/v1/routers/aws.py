from fastapi import APIRouter
from pydantic import BaseModel
import boto3


from app.models.base_model import VPCDeleteRequest

from app.services.network.aws.vpc_api import AWSVPCManager
from app.services.network.aws.ec2_api import AWSEC2Manager
from app.services.network.aws.sg_api import SecurityGroupManager
from app.services.network.aws.route_table_api import AWSRouteTableManager
from app.services.network.aws.nat_gateway_api import AWSNatGatewayManager
from app.services.network.aws.internet_gateway_api import AWSInternetGatewayManager

from app.services.aws.vpc_inspector import VPCInspector
from app.services.aws.route_table_inspector import RouteTableInspector
from app.services.aws.nat_gateway_inspector import NatGatewayInspector
from app.services.aws.internet_gateway_inspector import InternetGatewayInspector




router = APIRouter(tags=["AWS"])


# ============================================================
# 🟦 VPC ROUTES
# ============================================================
@router.get("/vpcs")
def list_vpcs():
    return AWSVPCManager().list_vpcs()

@router.get("/vpcs/{vpc_id}/inspect")
def inspect_vpc_dependencies(vpc_id: str):
    inspector = VPCInspector()
    return inspector.inspect(vpc_id)

@router.get("/route-tables/inspect")
async def inspect_route_tables(vpc_id: str):
    inspector = RouteTableInspector()
    return inspector.inspect_vpc_route_tables(vpc_id)

@router.get("/nat-gateways/inspect")
async def inspect_nat_gateways(vpc_id: str):
    inspector = NatGatewayInspector()
    return inspector.inspect_vpc_nat_gateways(vpc_id)

@router.get("/internet-gateways/inspect")
async def inspect_internet_gateways(vpc_id: str):
    inspector = InternetGatewayInspector()
    return inspector.inspect_vpc_internet_gateways(vpc_id)

    resp = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )

    return {
        "count": len(resp.get("Subnets", [])),
        "subnets": [
            {
                "subnet_id": s["SubnetId"],
                "cidr": s["CidrBlock"],
                "availability_zone": s["AvailabilityZone"],
                "state": s["State"],
            }
            for s in resp.get("Subnets", [])
        ],
    }


@router.post("/vpcs")
def create_vpc(cidr: str = "10.0.0.0/16"):
    return AWSVPCManager().create_vpc(cidr)


@router.post("/vpc/delete-body")
def delete_vpc_body(request: VPCDeleteRequest):
    return AWSVPCManager().delete_vpc_simple(request.vpc_id)


@router.post("/vpc/safe-delete-body")
def delete_vpc_safe_body(request: VPCDeleteRequest):
    return AWSVPCManager().delete_vpc_safe(request.vpc_id)


@router.delete("/vpc/{vpc_id}/delete")
def delete_vpc_simple(vpc_id: str):
    return AWSVPCManager().delete_vpc_simple(vpc_id)


@router.delete("/vpc/{vpc_id}/safe-delete")
def delete_vpc_safe(vpc_id: str):
    return AWSVPCManager().delete_vpc_safe(vpc_id)


# ============================================================
# 🟦 SUBNET ROUTES
@router.get("/subnets")
def list_subnets(vpc_id: str | None = None):
    ec2 = boto3.client("ec2")

    if vpc_id:
        resp = ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
    else:
        resp = ec2.describe_subnets()

    return [
        {
            "subnet_id": s["SubnetId"],
            "vpc_id": s["VpcId"],
            "cidr": s["CidrBlock"],
            "availability_zone": s["AvailabilityZone"],
            "state": s["State"],
        }
        for s in resp.get("Subnets", [])
    ]

# ============================================================


@router.post("/subnets")
def create_subnet(
    vpc_id: str,
    cidr: str,
    availability_zone: str,
    name: str | None = None,
):
    return AWSVPCManager().create_subnet(
        vpc_id=vpc_id,
        cidr=cidr,
        availability_zone=availability_zone,
        name=name,
    )


@router.delete("/subnets/{subnet_id}")
def delete_subnet(subnet_id: str):
    return AWSVPCManager().delete_subnet(subnet_id)


# ============================================================
# 🟦 AVAILABILITY ZONES
# ============================================================
@router.get("/availability-zones")
def list_availability_zones():
    return AWSVPCManager().list_availability_zones()


# ============================================================
# 🟦 ROUTE TABLE MODELS
# ============================================================
class RouteTableCreate(BaseModel):
    vpc_id: str
    name: str
    description: str | None = None


class RouteCreate(BaseModel):
    destination_cidr: str
    target_type: str
    target_id: str


# ============================================================
# 🟦 ROUTE TABLE ROUTES
# ============================================================
@router.get("/route-tables")
def list_route_tables():
    return AWSRouteTableManager().list_route_tables()


@router.post("/route-tables")
def create_route_table(payload: RouteTableCreate):
    return AWSRouteTableManager().create_route_table(
        vpc_id=payload.vpc_id,
        name=payload.name,
        description=payload.description,
    )


@router.post("/route-tables/{rtb_id}/associate")
def associate_route_table(rtb_id: str, subnet_id: str):
    return AWSRouteTableManager().associate_route_table(
        rtb_id=rtb_id,
        subnet_id=subnet_id,
    )


@router.post("/route-tables/{rtb_id}/routes")
def create_route(rtb_id: str, payload: RouteCreate):
    return AWSRouteTableManager().create_route(
        route_table_id=rtb_id,
        destination_cidr=payload.destination_cidr,
        target_type=payload.target_type,
        target_id=payload.target_id,
    )


@router.post("/route-tables/{association_id}/disassociate")
def disassociate_route_table(association_id: str):
    return AWSRouteTableManager().disassociate(association_id)


# ============================================================
# 🟦 INTERNET GATEWAYS (AUTHORITATIVE)
# ============================================================
@router.get("/internet-gateways")
def list_internet_gateways():
    return AWSInternetGatewayManager().list_igws()


@router.post("/internet-gateways")
def create_internet_gateway(name: str | None = None):
    return AWSInternetGatewayManager().create_igw(name=name)


@router.post("/internet-gateways/{igw_id}/attach")
def attach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSInternetGatewayManager().attach_igw(igw_id, vpc_id)


@router.post("/internet-gateways/{igw_id}/detach")
def detach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSInternetGatewayManager().detach_igw(igw_id, vpc_id)


@router.delete("/internet-gateways/{igw_id}")
def delete_internet_gateway(igw_id: str):
    return AWSInternetGatewayManager().delete_igw(igw_id)


# ============================================================
# 🟦 NAT GATEWAYS (LOCKED)
# ============================================================
@router.get("/nat-gateways")
def list_nat_gateways():
    return AWSNatGatewayManager().list_nat_gateways()


@router.post("/nat-gateways")
def create_nat_gateway(
    subnet_id: str,
    name: str | None = None,
    allocation_id: str | None = None,
):
    return AWSNatGatewayManager().create_nat_gateway(
        subnet_id=subnet_id,
        allocation_id=allocation_id,
        name=name,
    )


@router.delete("/nat-gateways/{nat_gateway_id}")
def delete_nat_gateway(nat_gateway_id: str):
    return AWSNatGatewayManager().delete_nat_gateway(
        nat_gateway_id=nat_gateway_id
    )


# ============================================================
# 🟦 EC2
# ============================================================
@router.get("/instances")
def list_instances():
    return AWSEC2Manager().list_instances()


# ============================================================
# 🟦 SECURITY GROUPS
# ============================================================
@router.get("/security-groups")
def list_security_groups():
    return SecurityGroupManager().list_security_groups()

@router.get("/vpcs/{vpc_id}/inspect")
async def inspect_vpc(vpc_id: str):
    """
    Read-only inspection explaining why a VPC cannot be deleted.
    """
    api = VpcApi()
    return api.inspect_vpc_dependencies(vpc_id)

@router.get("/vpcs/{vpc_id}/subnets/inspection")
async def inspect_subnets(vpc_id: str):
    """
    Read-only inspection of subnets within a VPC.
    (Step 5: include ENI, NAT, and explicit route table associations)
    """
    import boto3
    from collections import defaultdict

    ec2 = boto3.client("ec2")

    # 1) Subnets in VPC
    resp = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    subnets = resp.get("Subnets", [])

    # 2) ENIs in VPC → group by subnet
    eni_resp = ec2.describe_network_interfaces(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    eni_counts = defaultdict(int)
    for eni in eni_resp.get("NetworkInterfaces", []):
        subnet_id = eni.get("SubnetId")
        if subnet_id:
            eni_counts[subnet_id] += 1

    # 3) NAT Gateways in VPC → group by subnet
    nat_resp = ec2.describe_nat_gateways(
        Filter=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    nat_counts = defaultdict(int)
    for nat in nat_resp.get("NatGateways", []):
        subnet_id = nat.get("SubnetId")
        if subnet_id:
            nat_counts[subnet_id] += 1

    # 4) Route table explicit associations → set of subnet IDs
    rt_resp = ec2.describe_route_tables(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    rt_associated_subnets = set()
    for rt in rt_resp.get("RouteTables", []):
        for assoc in rt.get("Associations", []):
            subnet_id = assoc.get("SubnetId")
            if subnet_id:
                rt_associated_subnets.add(subnet_id)

    # 5) Build details
    details = []
    subnets_with_enis = 0
    subnets_with_nat = 0
    subnets_with_rt_assoc = 0

    for sn in subnets:
        subnet_id = sn.get("SubnetId")
        eni_count = eni_counts.get(subnet_id, 0)
        nat_count = nat_counts.get(subnet_id, 0)
        rt_assoc = subnet_id in rt_associated_subnets

        if eni_count > 0:
            subnets_with_enis += 1
        if nat_count > 0:
            subnets_with_nat += 1
        if rt_assoc:
            subnets_with_rt_assoc += 1

        can_delete = (eni_count == 0 and nat_count == 0)

        details.append({
            "subnet_id": subnet_id,
            "cidr": sn.get("CidrBlock"),
            "availability_zone": sn.get("AvailabilityZone"),
            "state": sn.get("State"),
            "eni_count": eni_count,
            "nat_gateway_count": nat_count,
            "route_table_associated": rt_assoc,
            "can_delete": can_delete
        })

    return {
        "summary": {
            "total_subnets": len(subnets),
            "subnets_with_enis": subnets_with_enis,
            "subnets_with_nat": subnets_with_nat,
            "subnets_with_route_table_associations": subnets_with_rt_assoc
        },
        "details": details
    }

# ============================================================
# 🟦 NETWORK INTERFACES (ENIs) — INVENTORY
# ============================================================
@router.get("/network-interfaces")
def list_network_interfaces(vpc_id: str):
    import boto3

    ec2 = boto3.client("ec2")

    resp = ec2.describe_network_interfaces(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )

    interfaces = []
    for eni in resp.get("NetworkInterfaces", []):
        interfaces.append({
            "eni_id": eni.get("NetworkInterfaceId"),
            "subnet_id": eni.get("SubnetId"),
            "status": eni.get("Status"),
            "private_ip": eni.get("PrivateIpAddress"),
            "interface_type": eni.get("InterfaceType"),
            "attachment": eni.get("Attachment", {}).get("InstanceId")
        })

    return {
        "network_interfaces": interfaces
    }

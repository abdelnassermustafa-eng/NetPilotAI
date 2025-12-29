from fastapi import APIRouter
from pydantic import BaseModel

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
# ============================================================
@router.get("/subnets")
def list_subnets():
    return AWSVPCManager().list_subnets()


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


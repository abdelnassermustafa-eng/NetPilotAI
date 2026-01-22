from fastapi import APIRouter
from app.services.network.aws.vpc_api import AWSVPCManager
from app.services.network.aws.ec2_api import AWSEC2Manager
from app.services.network.aws.sg_api import SecurityGroupManager
from app.services.network.aws.route_table_api import AWSRouteTableManager
from app.services.network.aws.nat_gateway_api import AWSNatGatewayManager
from app.models.base_model import VPCDeleteRequest
from pydantic import BaseModel


router = APIRouter(tags=["AWS"])



# ============================================================
# 🟦 VPC ROUTES
# ============================================================
@router.get("/vpcs")
async def list_vpcs():
    return AWSVPCManager().list_vpcs()


@router.post("/vpcs")
async def create_vpc(cidr: str = "10.0.0.0/16"):
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
async def list_subnets():
    return AWSVPCManager().list_subnets()


@router.post("/subnets")
async def create_subnet(
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
async def delete_subnet(subnet_id: str):
    return AWSVPCManager().delete_subnet(subnet_id)


# ============================================================
# 🟦 AVAILABILITY ZONES
# ============================================================
@router.get("/availability-zones")
async def list_availability_zones():
    return AWSVPCManager().list_availability_zones()

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
async def list_route_tables():
    return AWSRouteTableManager().list_route_tables()


@router.post("/route-tables")
async def create_route_table(payload: RouteTableCreate):
    return AWSRouteTableManager().create_route_table(
        vpc_id=payload.vpc_id,
        name=payload.name,
        description=payload.description,
    )


@router.post("/route-tables/{rtb_id}/associate")
async def associate_route_table(rtb_id: str, subnet_id: str):
    return AWSRouteTableManager().associate_route_table(rtb_id, subnet_id)

@router.post("/route-tables/{rtb_id}/routes")
async def create_route(
    rtb_id: str,
    payload: RouteCreate,
):
    return AWSRouteTableManager().create_route(
        route_table_id=rtb_id,
        destination_cidr=payload.destination_cidr,
        target_type=payload.target_type,
        target_id=payload.target_id,
    )



@router.post("/route-tables/{association_id}/disassociate")
async def disassociate_route_table(association_id: str):
    return AWSRouteTableManager().disassociate(association_id)


# ============================================================
# 🟦 INTERNET GATEWAYS (FIXED & STABLE)
# ============================================================
@router.get("/internet-gateways")
async def list_internet_gateways():
    return AWSEC2Manager().list_internet_gateways()


@router.post("/internet-gateways")
async def create_internet_gateway(name: str | None = None):
    return AWSEC2Manager().create_internet_gateway(name=name)


@router.post("/internet-gateways/{igw_id}/attach")
async def attach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSEC2Manager().attach_internet_gateway(igw_id, vpc_id)


@router.post("/internet-gateways/{igw_id}/detach")
async def detach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSEC2Manager().detach_internet_gateway(igw_id, vpc_id)


@router.delete("/internet-gateways/{igw_id}")
async def delete_internet_gateway(igw_id: str):
    return AWSEC2Manager().delete_internet_gateway(igw_id)


# ============================================================
# 🟦 NAT GATEWAYS (UNCHANGED — NEXT PROBLEM)
# ============================================================
@router.get("/nat-gateways")
async def list_nat_gateways():
    return AWSNatGatewayManager().list_nat_gateways()


@router.post("/nat-gateways")
async def create_nat_gateway(
    subnet_id: str,
    name: str | None = None,
    allocation_id: str | None = None,
):
    return AWSNatGatewayManager().create_nat_gateway(
        subnet_id=subnet_id,
        name=name,
        allocation_id=allocation_id,
    )


@router.delete("/nat-gateways/{nat_gateway_id}")
async def delete_nat_gateway(
    nat_gateway_id: str,
    release_eip: bool = True,
):
    return AWSNatGatewayManager().delete_nat_gateway(
        nat_gateway_id=nat_gateway_id,
        release_eip=release_eip,
    )


# ============================================================
# 🟦 EC2
# ============================================================
@router.get("/instances")
async def list_instances():
    return AWSEC2Manager().list_instances()


# ============================================================
# 🟦 SECURITY GROUPS
# ============================================================
@router.get("/security-groups")
async def list_security_groups():
    return SecurityGroupManager().list_security_groups()

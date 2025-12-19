from fastapi import APIRouter
from app.services.network.aws.vpc_api import AWSVPCManager
from app.services.network.aws.ec2_api import AWSEC2Manager
from app.services.network.aws.sg_api import SecurityGroupManager
from app.services.network.aws.route_table_api import AWSRouteTableManager
from app.services.network.aws.igw_api import AWSInternetGatewayManager
from app.services.network.aws.nat_api import AWSNatGatewayManager
from app.services.network.aws.nat_gateway_api import AWSNatGatewayManager
from app.services.network.aws.internet_gateway_api import AWSInternetGatewayManager
from app.models.base_model import VPCDeleteRequest


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


# ============================================================
# 🟥 DEASSOCIATE SUBNET FROM ROUTE TABLE
# ============================================================
# @router.post("/route-tables/{assoc_id}/disassociate")
# async def disassociate_subnet(assoc_id: str):
#    return RouteTableManager().disassociate(assoc_id)


@router.post("/route-tables/{association_id}/disassociate")
async def disassociate_route_table(association_id: str):
    return AWSRouteTableManager().disassociate(association_id)


# ============================================================
# 🟦 ROUTE TABLE ROUTES
# ============================================================
@router.get("/route-tables")
async def list_route_tables():
    return AWSRouteTableManager().list_route_tables()


@router.post("/route-tables")
async def create_route_table(vpc_id: str, name: str | None = None):
    return AWSRouteTableManager().create_route_table(vpc_id=vpc_id, name=name)


@router.post("/route-tables/{rtb_id}/associate")
async def associate_route_table(rtb_id: str, subnet_id: str):
    return AWSRouteTableManager().associate_route_table(rtb_id, subnet_id)


@router.post("/route-tables/{rtb_id}/routes")
async def create_route(
    rtb_id: str,
    destination_cidr: str,
    target_type: str,
    target_id: str,
):
    return AWSRouteTableManager().create_route(
        route_table_id=rtb_id,
        destination_cidr=destination_cidr,
        target_type=target_type,
        target_id=target_id,
    )


# ============================================================
# 🟦 INTERNET GATEWAY ROUTES (NEW — Phase 4)
# ============================================================


@router.get("/internet-gateways")
async def list_internet_gateways():
    return AWSInternetGatewayManager().list_internet_gateways()


@router.post("/internet-gateways")
async def create_internet_gateway(name: str | None = None, vpc_id: str | None = None):
    """
    Create an IGW with:
      - optional Name tag
      - optional immediate attachment
    """
    return AWSInternetGatewayManager().create_internet_gateway(name=name, vpc_id=vpc_id)


@router.post("/internet-gateways/{igw_id}/attach")
async def attach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSInternetGatewayManager().attach_internet_gateway(igw_id, vpc_id)


@router.post("/internet-gateways/{igw_id}/detach")
async def detach_internet_gateway(igw_id: str, vpc_id: str):
    return AWSInternetGatewayManager().detach_internet_gateway(igw_id, vpc_id)


@router.delete("/internet-gateways/{igw_id}")
async def delete_internet_gateway(igw_id: str):
    return AWSInternetGatewayManager().delete_internet_gateway(igw_id)


# @router.post("/route-tables/disassociate")
# async def disassociate_route_table(association_id: str):
#    return AWSRouteTableManager().disassociate(association_id)


# ============================================================
# 🟦 NAT GATEWAY ROUTES (Phase 4 — Full UI)
# ============================================================


@router.get("/nat-gateways")
async def list_nat_gateways():
    """
    List all NAT Gateways with useful details for the UI.
    """
    return AWSNatGatewayManager().list_nat_gateways()


@router.post("/nat-gateways")
async def create_nat_gateway(
    subnet_id: str,
    name: str | None = None,
    allocation_id: str | None = None,
):
    """
    Create a NAT Gateway in the given subnet.

    - If allocation_id is not provided, an Elastic IP will be auto-allocated.
    - Optional 'name' will be applied as a Name tag on the NAT Gateway.
    """
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
    """
    Delete a NAT Gateway and, optionally, release its EIP.
    """
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


# =========================================================
# NAT GATEWAY ROUTES
# =========================================================

nat_manager = AWSNatGatewayManager()


# ---------------------------------------------------------
# ALLOCATE ELASTIC IP
# ---------------------------------------------------------
@router.post("/nat/eip")
def allocate_nat_eip(name: str = None):
    """
    Allocate an Elastic IP for NAT Gateway use.
    """
    return nat_manager.allocate_eip(name=name)


# ---------------------------------------------------------
# RELEASE ELASTIC IP
# ---------------------------------------------------------
@router.delete("/nat/eip/{allocation_id}")
def release_nat_eip(allocation_id: str):
    """
    Release an Elastic IP.
    """
    return nat_manager.release_eip(allocation_id)


# ---------------------------------------------------------
# CREATE NAT GATEWAY
# ---------------------------------------------------------
@router.post("/nat")
def create_nat_gateway(
    subnet_id: str,
    allocation_id: str,
    name: str = None,
):
    """
    Create a NAT Gateway in a public subnet.
    """
    return nat_manager.create_nat_gateway(
        subnet_id=subnet_id,
        allocation_id=allocation_id,
        name=name,
    )


# ---------------------------------------------------------
# DELETE NAT GATEWAY
# ---------------------------------------------------------
@router.delete("/nat/{nat_gateway_id}")
def delete_nat_gateway(nat_gateway_id: str):
    """
    Delete a NAT Gateway.
    """
    return nat_manager.delete_nat_gateway(nat_gateway_id)


# ---------------------------------------------------------
# LIST NAT GATEWAYS
# ---------------------------------------------------------
@router.get("/nat")
def list_nat_gateways():
    """
    List all NAT Gateways.
    """
    return nat_manager.list_nat_gateways()


# =========================================================
# INTERNET GATEWAY ROUTES
# =========================================================

igw_manager = AWSInternetGatewayManager()


# ---------------------------------------------------------
# CREATE INTERNET GATEWAY
# ---------------------------------------------------------
@router.post("/igw")
def create_internet_gateway(name: str = None):
    """
    Create an Internet Gateway (unattached).
    """
    return igw_manager.create_igw(name=name)


# ---------------------------------------------------------
# ATTACH INTERNET GATEWAY TO VPC
# ---------------------------------------------------------
@router.post("/igw/attach")
def attach_internet_gateway(
    internet_gateway_id: str,
    vpc_id: str,
):
    """
    Attach an Internet Gateway to a VPC.
    """
    return igw_manager.attach_igw(
        igw_id=internet_gateway_id,
        vpc_id=vpc_id,
    )


# ---------------------------------------------------------
# DETACH INTERNET GATEWAY FROM VPC
# ---------------------------------------------------------
@router.post("/igw/detach")
def detach_internet_gateway(
    internet_gateway_id: str,
    vpc_id: str,
):
    """
    Detach an Internet Gateway from a VPC.
    """
    return igw_manager.detach_igw(
        igw_id=internet_gateway_id,
        vpc_id=vpc_id,
    )


# ---------------------------------------------------------
# DELETE INTERNET GATEWAY
# ---------------------------------------------------------
@router.delete("/igw/{internet_gateway_id}")
def delete_internet_gateway(internet_gateway_id: str):
    """
    Delete an Internet Gateway (must be detached first).
    """
    return igw_manager.delete_igw(igw_id=internet_gateway_id)


# ---------------------------------------------------------
# LIST INTERNET GATEWAYS
# ---------------------------------------------------------
@router.get("/igw")
def list_internet_gateways():
    """
    List all Internet Gateways.
    """
    return igw_manager.list_igws()

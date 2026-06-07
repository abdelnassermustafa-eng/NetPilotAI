from fastapi import APIRouter, Query
import boto3

router = APIRouter(prefix="/aws", tags=["AWS"])

@router.get("/network-interfaces")
def list_network_interfaces(vpc_id: str = Query(...)):
    ec2 = boto3.client("ec2")

    resp = ec2.describe_network_interfaces(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]}
        ]
    )

    enis = []
    for eni in resp.get("NetworkInterfaces", []):
        enis.append({
            "network_interface_id": eni.get("NetworkInterfaceId"),
            "subnet_id": eni.get("SubnetId"),
            "status": eni.get("Status"),
            "private_ip": eni.get("PrivateIpAddress"),
            "description": eni.get("Description"),
        })

    return {
        "status": "ok",
        "items": enis
    }

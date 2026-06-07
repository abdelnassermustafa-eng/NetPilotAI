from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# ------------------------------
# HTML Dashboard Page
# ------------------------------
@router.get("/", tags=["dashboard"])
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ------------------------------
# JSON Summary Endpoint
# ------------------------------
@router.get("/summary", tags=["dashboard"])
def dashboard_summary():
    """
    Returns a JSON summary of NetPilot AI system capabilities.
    """

    cloud_providers = ["AWS", "Azure", "GCP"]
    vendor_modules = [
        "Cisco",
        "Juniper",
        "Arista",
        "Fortinet",
        "Palo Alto",
        "Check Point",
        "VMware",
    ]

    return {
        "status": "ok",
        "backend_version": "1.0.0",
        "cloud_providers": cloud_providers,
        "vendor_modules": vendor_modules,
        "cloud_count": len(cloud_providers),
        "vendor_count": len(vendor_modules),
        "message": "Dashboard summary loaded successfully.",
    }

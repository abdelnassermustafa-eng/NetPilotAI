from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.routers.dashboard import router as dashboard_router
from app.api.v1.routers.aws import router as aws_router
from app.api.v1.routers.health import router as health_router

from app.db.init_db import init_db

app = FastAPI(
    title="NetPilot AI Backend",
    description="Multi-cloud & Network Automation Platform",
    version="1.0.0",
)

# ----------------------------
# Static & Templates
# ----------------------------
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ----------------------------
# Routers
# ----------------------------
app.include_router(health_router, prefix="/api/v1")
app.include_router(aws_router, prefix="/api/v1/aws")
app.include_router(dashboard_router, prefix="/api/v1/dashboard")


# ----------------------------
# Dashboard (Root UI)
# ----------------------------
@app.get("/", tags=["dashboard"])
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ----------------------------
# Startup event
# ----------------------------app.include_router(dashboard_router, prefix="/dashboard")


@app.on_event("startup")
def startup_event():
    init_db()
    print("NetPilot AI backend started successfully.")

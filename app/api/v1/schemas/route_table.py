from pydantic import BaseModel
from typing import Optional

class RouteTableCreate(BaseModel):
    vpc_id: str
    name: Optional[str] = None
    description: Optional[str] = None

class RouteTableAssociate(BaseModel):
    subnet_id: str

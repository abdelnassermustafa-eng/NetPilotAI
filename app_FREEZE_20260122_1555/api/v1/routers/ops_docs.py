from fastapi import APIRouter

router = APIRouter()

@router.get("/about")
def ops_about():
    """
    Operational & Validation documentation endpoint.
    Read-only. No cloud mutations.
    """
    return {
        "module": "Validation & Operations",
        "purpose": "Read-only inspection, dependency analysis, and CLI mirroring",
        "guarantees": [
            "No resource modification",
            "No delete/create actions",
            "Safe for production accounts"
        ],
        "planned_features": [
            "VPC dependency inspection",
            "Why-blocked explanations",
            "CLI equivalents for UI actions",
            "Cross-resource validation"
        ]
    }

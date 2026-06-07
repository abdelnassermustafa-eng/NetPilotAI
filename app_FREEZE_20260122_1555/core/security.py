"""
Security utilities for NetPilot AI.

Future Enhancements:
- JWT authentication
- Role-based access control (RBAC)
- API key authentication
- OAuth2 support
"""

from fastapi import HTTPException, status

def not_implemented(feature: str):
    """
    Temporary placeholder for security functions not yet implemented.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Security feature '{feature}' is not implemented yet in NetPilot AI."
    )

from fastapi import HTTPException, status, Depends
from typing import Optional, Callable

from app.licensing.models import LicenseStatus, Entitlements
from app.licensing.client_manager import ClientLicenseManager

# Global client license manager instance
default_client_manager = ClientLicenseManager()

def get_client_license_manager() -> ClientLicenseManager:
    return default_client_manager

def verify_active_license(
    client_manager: ClientLicenseManager = Depends(get_client_license_manager)
) -> Entitlements:
    lic_status, entitlements, message = client_manager.evaluate_license()
    if lic_status != LicenseStatus.ACTIVE or not entitlements:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "LICENSE_RESTRICTED",
                "license_status": lic_status.value,
                "message": message
            }
        )
    return entitlements

def require_entitlement(feature_attr: str):
    def entitlement_checker(entitlements: Entitlements = Depends(verify_active_license)):
        if not getattr(entitlements, feature_attr, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "ENTITLEMENT_RESTRICTED",
                    "plan": entitlements.plan.value,
                    "message": f"Feature '{feature_attr}' is not available on your {entitlements.plan.value} plan."
                }
            )
        return entitlements
    return entitlement_checker

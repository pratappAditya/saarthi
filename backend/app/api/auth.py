from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.db.auth import AuthRepository
from app.security.quota import QuotaManager

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str
    device_id: Optional[str] = "desktop_device_1"
    device_name: Optional[str] = "Windows Workstation"

class ResetPasswordRequest(BaseModel):
    email: str

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.replace("Bearer ", "").strip()
    session = AuthRepository.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    return session

@router.post("/register")
def register(req: RegisterRequest):
    try:
        user = AuthRepository.create_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name
        )
        session = AuthRepository.create_session(user["user_id"])
        return {
            "status": "success",
            "message": "Account created successfully. Please verify your email.",
            "user": user,
            "session": session
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
def login(req: LoginRequest):
    user = AuthRepository.authenticate(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    session = AuthRepository.create_session(
        user_id=user["user_id"],
        device_id=req.device_id or "desktop_device_1",
        device_name=req.device_name or "Windows Workstation"
    )
    return {
        "status": "success",
        "user": user,
        "session": session
    }

@router.post("/logout")
def logout(user: Dict[str, Any] = Depends(get_current_user)):
    AuthRepository.revoke_session(user["session_token"])
    return {"status": "success", "message": "Logged out successfully."}

@router.get("/me")
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    quota = QuotaManager.get_quota_status(user["user_id"], user["subscription_plan"])
    return {
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_verified": bool(user["is_verified"]),
            "role": user["role"],
            "subscription_plan": user["subscription_plan"]
        },
        "quota": quota
    }

class VerifyEmailRequest(BaseModel):
    token: str

class RequestResetRequest(BaseModel):
    email: str

class PerformResetRequest(BaseModel):
    token: str
    new_password: str

class RevokeDeviceRequest(BaseModel):
    device_id: str

from app.services.identity_service import IdentityService

class Verify2FARequest(BaseModel):
    code: str

@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest):
    IdentityService.verify_email(req.token)
    return {"status": "success", "message": "Email verified successfully."}

@router.post("/request-password-reset")
def request_password_reset(req: RequestResetRequest):
    return IdentityService.request_password_reset(req.email)

@router.post("/reset-password")
def reset_password(req: PerformResetRequest):
    IdentityService.confirm_password_reset(req.token, req.new_password)
    return {"status": "success", "message": "Password reset successfully. Please log in with your new password."}

@router.get("/sessions")
def list_sessions(user: Dict[str, Any] = Depends(get_current_user)):
    sessions = IdentityService.inspect_sessions(user["user_id"])
    return {"sessions": sessions}

@router.delete("/sessions/{session_id}")
def revoke_session_by_id(session_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    IdentityService.revoke_session_by_id(user["user_id"], session_id)
    return {"status": "success", "message": "Session revoked successfully."}

@router.get("/devices")
def list_devices(user: Dict[str, Any] = Depends(get_current_user)):
    devices = AuthRepository.list_user_devices(user["user_id"])
    return {"devices": devices}

@router.post("/devices/revoke")
def revoke_device(req: RevokeDeviceRequest, user: Dict[str, Any] = Depends(get_current_user)):
    AuthRepository.revoke_device(user["user_id"], req.device_id)
    return {"status": "success", "message": f"Device {req.device_id} revoked."}

@router.post("/logout-all")
def logout_all(user: Dict[str, Any] = Depends(get_current_user)):
    count = IdentityService.logout_all_sessions(user["user_id"])
    return {"status": "success", "message": f"Logged out from all {count} sessions."}

@router.post("/2fa/setup")
def setup_2fa(user: Dict[str, Any] = Depends(get_current_user)):
    return IdentityService.setup_2fa(user["user_id"])

@router.post("/2fa/verify")
def verify_2fa(req: Verify2FARequest, user: Dict[str, Any] = Depends(get_current_user)):
    IdentityService.verify_and_enable_2fa(user["user_id"], req.code)
    return {"status": "success", "message": "2FA verified and enabled successfully."}

@router.post("/delete-account")
def delete_account(user: Dict[str, Any] = Depends(get_current_user)):
    AuthRepository.delete_account(user["user_id"])
    return {"status": "success", "message": "Account deleted successfully."}

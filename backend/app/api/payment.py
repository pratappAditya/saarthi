import json
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.api.auth import get_current_user
from app.services.billing_service import BillingService

router = APIRouter(prefix="/payment", tags=["Payment & Billing"])

class CheckoutRequest(BaseModel):
    plan_name: str
    provider: Optional[str] = "RAZORPAY"
    currency: Optional[str] = "INR"
    seats: Optional[int] = 1
    org_id: Optional[str] = None

class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    plan_name: Optional[str] = None
    provider: Optional[str] = "RAZORPAY"

class CancelSubscriptionRequest(BaseModel):
    subscription_id: str
    policy: Optional[str] = "immediate"

class UpgradeDowngradeRequest(BaseModel):
    subscription_id: str
    new_plan_name: str
    seats: Optional[int] = 1

@router.get("/plans")
def get_plans():
    return BillingService.get_plan_catalog()

@router.post("/checkout")
def create_checkout_session(req: CheckoutRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return BillingService.create_checkout_order(
        user_id=user["user_id"],
        plan_name=req.plan_name,
        provider=req.provider or "RAZORPAY",
        currency=req.currency or "INR",
        seats=req.seats or 1,
        org_id=req.org_id
    )

@router.post("/verify")
def verify_payment(req: VerifyPaymentRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return BillingService.verify_payment_and_activate_subscription(
        order_id=req.order_id,
        payment_id=req.payment_id,
        signature=req.signature,
        plan_name=req.plan_name,
        provider=req.provider or "RAZORPAY"
    )

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, x_razorpay_signature: Optional[str] = Header(None)):
    payload = await request.body()
    res = BillingService.process_webhook(payload, x_razorpay_signature or "", provider="RAZORPAY")
    if res.get("verified") is False or res.get("status") == "error":
        raise HTTPException(status_code=400, detail="Invalid payment webhook signature.")
    return res

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    payload = await request.body()
    res = BillingService.process_webhook(payload, stripe_signature or "", provider="STRIPE")
    if res.get("verified") is False or res.get("status") == "error":
        raise HTTPException(status_code=400, detail="Invalid payment webhook signature.")
    return res

@router.post("/payments/webhook")
async def generic_webhook(request: Request):
    payload = await request.body()
    res = BillingService.process_webhook(payload, "", provider="RAZORPAY")
    if res.get("verified") is False or res.get("status") == "error":
        raise HTTPException(status_code=400, detail="Invalid payment webhook signature.")
    return res

@router.get("/subscriptions")
def get_user_subscriptions(user: Dict[str, Any] = Depends(get_current_user)):
    subs = BillingService.get_user_subscriptions(user["user_id"])
    return {"subscriptions": subs}

@router.get("/invoices")
def get_user_invoices(user: Dict[str, Any] = Depends(get_current_user)):
    invs = BillingService.get_user_invoices(user["user_id"])
    return {"invoices": invs}

@router.post("/cancel")
def cancel_subscription(req: CancelSubscriptionRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return BillingService.cancel_subscription(req.subscription_id, user["user_id"], policy=req.policy or "immediate")

@router.post("/upgrade-downgrade")
def upgrade_downgrade_subscription(req: UpgradeDowngradeRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return BillingService.upgrade_or_downgrade(
        subscription_id=req.subscription_id,
        user_id=user["user_id"],
        new_plan_name=req.new_plan_name,
        new_seats=req.seats or 1
    )

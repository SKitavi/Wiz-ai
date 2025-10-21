# app/routers/plans.py

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()

class PlanRequest(BaseModel):
    user_id: str
    date: date

class PlanResponse(BaseModel):
    user_id: str
    date: date
    plan: str

# Optional: Auth dependency (if you want to enforce token checking)
def verify_token(authorization: str = Header(...)):
    # Example: Check against a static token or from settings
    expected = "Bearer YOUR_SECRET_TOKEN"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):  # Add 'Depends(verify_token)' if needed
    if not request.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required and cannot be empty")

    plan_date = request.date or date.today()

    # Replace this with your actual logic
    generated_plan = f"Generated schedule for user {request.user_id} on {plan_date}"

    return PlanResponse(
        user_id=request.user_id,
        date=plan_date,
        plan=generated_plan
    )

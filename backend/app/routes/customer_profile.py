from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user
from app.db.models import User
from app.models.schema import CustomerProfileResponse

router = APIRouter(prefix="/customer_profile", tags=["customer_profile"])


@router.get("/", response_model=CustomerProfileResponse, status_code=200)
async def get_customer_profile(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user

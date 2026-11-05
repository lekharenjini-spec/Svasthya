import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

from ..database import get_db
from ..models import User, PatientProfile
from ..security import get_current_user, require_role

# Configure audit logging for healthcare privacy tracking
logger = logging.getLogger("security_audit")

router = APIRouter(prefix="/profiles", tags=["Patient Profiles"])

# --- Pydantic Schemas ---
class ProfileCreate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")  # Standard Indian 6-digit PIN validation
    emergency_contact: Optional[str] = Field(None, pattern=r"^\d{10}$")


class ProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")
    emergency_contact: Optional[str] = Field(None, pattern=r"^\d{10}$")


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone_number: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    emergency_contact: Optional[str] = None

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Patient: Create profile if it does not already exist."""
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can create patient profiles.")

    existing_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Patient profile already exists for this user.")

    new_profile = PatientProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    logger.info(f"Patient [ID: {current_user.id}] created their profile.")
    
    return {
        "id": new_profile.id,
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "age": new_profile.age,
        "address": new_profile.address,
        "city": new_profile.city,
        "pincode": new_profile.pincode,
        "emergency_contact": new_profile.emergency_contact
    }


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Patient: Get logged-in patient's profile."""
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access restricted to patient accounts.")

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        # Fallback safeguard: auto-generate profile if missing
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": profile.id,
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "age": profile.age,
        "address": profile.address,
        "city": profile.city,
        "pincode": profile.pincode,
        "emergency_contact": profile.emergency_contact
    }


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    update_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Patient: Update logged-in patient's own profile fields."""
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access restricted to patient accounts.")

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    logger.info(f"Patient [ID: {current_user.id}] updated their profile securely.")

    return {
        "id": profile.id,
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "age": profile.age,
        "address": profile.address,
        "city": profile.city,
        "pincode": profile.pincode,
        "emergency_contact": profile.emergency_contact
    }


@router.get("/{user_id}", response_model=ProfileResponse)
def get_patient_profile_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Authorized Doctor or Admin: Access a patient's profile under strict permissions."""
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized role access to patient clinical profiles.")

    target_user = db.query(User).filter(User.id == user_id, User.role == "patient").first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Patient user record not found.")

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile details not found.")

    logger.info(f"User [ID: {current_user.id}, Role: {current_user.role}] accessed sensitive patient profile [ID: {user_id}]")

    return {
        "id": profile.id,
        "user_id": target_user.id,
        "full_name": target_user.full_name,
        "email": target_user.email,
        "phone_number": target_user.phone_number,
        "age": profile.age,
        "address": profile.address,
        "city": profile.city,
        "pincode": profile.pincode,
        "emergency_contact": profile.emergency_contact
  }
  

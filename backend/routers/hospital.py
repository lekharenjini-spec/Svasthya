import csv
import io
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..database import get_db
from ..models import Hospital, User
from ..security import get_current_user, require_role

# Configure audit logging
logger = logging.getLogger("security_audit")

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

# --- Pydantic Schemas ---
class HospitalCreate(BaseModel):
    hospital_name: str = Field(..., min_length=2, max_length=150)
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_services: Optional[str] = None


class HospitalUpdate(BaseModel):
    hospital_name: Optional[str] = Field(None, min_length=2, max_length=150)
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_services: Optional[str] = None
    is_active: Optional[bool] = None


class HospitalResponse(BaseModel):
    id: int
    hospital_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_services: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Admin only: Add a new hospital."""
    existing = db.query(Hospital).filter(
        Hospital.hospital_name == hospital_data.hospital_name, 
        Hospital.city == hospital_data.city
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A hospital with this name and city already exists.")

    new_hospital = Hospital(**hospital_data.model_dump(), is_active=True)
    db.add(new_hospital)
    db.commit()
    db.refresh(new_hospital)

    logger.info(f"Admin [ID: {current_user.id}] created hospital: {new_hospital.hospital_name}")
    return new_hospital


@router.get("/", response_model=List[HospitalResponse])
def list_hospitals(
    search: Optional[str] = Query(None, description="Search by hospital name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
    service: Optional[str] = Query(None, description="Filter by available service keyword"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Public/Authenticated view: Search and filter hospitals with pagination."""
    query = db.query(Hospital)

    if not current_user or current_user.role == "patient":
        query = query.filter(Hospital.is_active == True)

    if search:
        query = query.filter(Hospital.hospital_name.ilike(f"%{search}%"))
    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))
    if pincode:
        query = query.filter(Hospital.pincode == pincode)
    if service:
        query = query.filter(Hospital.available_services.ilike(f"%{service}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital_details(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get hospital details by ID."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found.")

    if not hospital.is_active and (not current_user or current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Hospital not found.")

    return hospital


@router.put("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    update_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Admin only: Update hospital info."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found.")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(hospital, key, value)

    db.commit()
    db.refresh(hospital)

    logger.info(f"Admin [ID: {current_user.id}] updated hospital ID: {hospital_id}")
    return hospital


@router.delete("/{hospital_id}", status_code=status.HTTP_200_OK)
def deactivate_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Admin only: Safely deactivate a hospital."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found.")

    hospital.is_active = False
    db.commit()

    logger.info(f"Admin [ID: {current_user.id}] deactivated hospital ID: {hospital_id}")
    return {"message": f"Hospital '{hospital.hospital_name}' has been deactivated successfully."}


@router.post("/load-csv", status_code=status.HTTP_200_OK)
async def load_hospitals_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Admin only: Bulk import hospitals via CSV format."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are accepted.")

    contents = await file.read()
    decoded_file = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_file))

    required_columns = {"hospital_name", "city", "pincode"}
    if not csv_reader.fieldnames or not required_columns.issubset(set(csv_reader.fieldnames)):
        raise HTTPException(status_code=400, detail=f"Missing required CSV columns. Expected at least: {required_columns}")

    success_count = 0
    invalid_rows = []

    for row_idx, row in enumerate(csv_reader, start=1):
        try:
            name = row.get("hospital_name", "").strip()
            city = row.get("city", "").strip()
            if not name or not city:
                invalid_rows.append({"row": row_idx, "reason": "Missing hospital_name or city"})
                continue

            existing = db.query(Hospital).filter(Hospital.hospital_name == name, Hospital.city == city).first()
            if existing:
                invalid_rows.append({"row": row_idx, "reason": f"Duplicate hospital '{name}' in '{city}'"})
                continue

            new_hosp = Hospital(
                hospital_name=name,
                address=row.get("address"),
                city=city,
                pincode=row.get("pincode"),
                phone_number=row.get("phone_number"),
                email=row.get("email"),
                latitude=float(row["latitude"]) if row.get("latitude") else None,
                longitude=float(row["longitude"]) if row.get("longitude") else None,
                available_services=row.get("available_services"),
                is_active=True
            )
            db.add(new_hosp)
            db.commit()
            success_count += 1
        except Exception as e:
            db.rollback()
            invalid_rows.append({"row": row_idx, "reason": str(e)})

    logger.info(f"Admin [ID: {current_user.id}] imported CSV: {success_count} added, {len(invalid_rows)} failed.")
    return {
        "message": "CSV import processed",
        "successfully_imported": success_count,
        "failed_rows_count": len(invalid_rows),
        "invalid_rows": invalid_rows
    }
    

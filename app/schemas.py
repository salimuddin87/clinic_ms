# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Reusable base model that enables from_orm() in pydantic v2
class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Patients
class PatientCreate(OrmBaseModel):
    first_name: str
    last_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None


class PatientOut(PatientCreate):
    id: int
    # model_config inherited from OrmBaseModel -> from_attributes=True


# Appointments
class AppointmentCreate(OrmBaseModel):
    patient_id: int
    scheduled_at: datetime
    reason: Optional[str] = None


class AppointmentOut(OrmBaseModel):
    id: int
    patient_id: int
    scheduled_at: datetime
    reason: Optional[str]
    status: str
    created_at: datetime


# Medicines
class MedicineCreate(OrmBaseModel):
    name: str
    manufacturer: Optional[str] = None
    quantity: int = 0
    description: Optional[str] = None
    reorder_threshold: int = 5


class MedicineOut(MedicineCreate):
    id: int


# Users & auth
class UserCreate(OrmBaseModel):
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "staff"
    password: str


class Token(OrmBaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(OrmBaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

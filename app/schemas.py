# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Patients
class PatientCreate(BaseModel):
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

    class Config:
        orm_mode = True


# Appointments
class AppointmentCreate(BaseModel):
    patient_id: int
    scheduled_at: datetime
    reason: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    scheduled_at: datetime
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# Medicines
class MedicineCreate(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    quantity: int = 0
    description: Optional[str] = None
    reorder_threshold: int = 5


class MedicineOut(MedicineCreate):
    id: int
    class Config:
        orm_mode = True


# Users & auth
class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "staff"
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

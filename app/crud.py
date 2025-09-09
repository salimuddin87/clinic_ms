# app/crud.py
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, schemas
from .logger_config import get_logger
from . import auth

logger = get_logger("clinic.crud")


# -------------------------
# Patients
# -------------------------
def create_patient(db: Session, payload: schemas.PatientCreate) -> models.Patient:
    """
    Creates and returns a new Patient record.
    """
    p = models.Patient(**payload.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    logger.info("Created patient id=%s name=%s %s", p.id, p.first_name, p.last_name)
    return p


def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    """
    Fetch patient by id.
    """
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def list_patients(db: Session, skip: int = 0, limit: int = 10, q: Optional[str] = None) -> List[models.Patient]:
    """
    List patients with optional search query (searches first_name, last_name, phone) and pagination.
    """
    qs = db.query(models.Patient)
    if q:
        like = f"%{q}%"
        qs = qs.filter(
            (models.Patient.first_name.like(like)) |
            (models.Patient.last_name.like(like)) |
            (models.Patient.phone.like(like))
        )
    results = qs.order_by(models.Patient.id).offset(skip).limit(limit).all()
    logger.info("Listed patients skip=%s limit=%s q=%s returned=%s", skip, limit, q, len(results))
    return results


# -------------------------
# Appointments
# -------------------------
def create_appointment(db: Session, payload: schemas.AppointmentCreate) -> models.Appointment:
    """
    Create appointment for an existing patient. Raises ValueError if patient not found.
    """
    patient = get_patient(db, payload.patient_id)
    if not patient:
        logger.warning("Attempt to create appointment for non-existent patient id=%s", payload.patient_id)
        raise ValueError("Patient not found")
    appt = models.Appointment(
        patient_id=payload.patient_id,
        scheduled_at=payload.scheduled_at,
        reason=payload.reason
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    logger.info("Created appointment id=%s patient=%s at=%s", appt.id, appt.patient_id, appt.scheduled_at)
    return appt


def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def list_appointments(db: Session, skip: int = 0, limit: int = 10, status: Optional[str] = None) -> List[models.Appointment]:
    qs = db.query(models.Appointment)
    if status:
        qs = qs.filter(models.Appointment.status == status)
    results = qs.order_by(models.Appointment.scheduled_at).offset(skip).limit(limit).all()
    logger.info("Listed appointments skip=%s limit=%s status=%s returned=%s", skip, limit, status, len(results))
    return results


def reschedule_appointment(db: Session, appointment_id: int, new_time: datetime) -> Optional[models.Appointment]:
    appt = get_appointment(db, appointment_id)
    if not appt:
        logger.warning("Reschedule failed: appointment not found id=%s", appointment_id)
        return None
    appt.scheduled_at = new_time
    db.commit()
    db.refresh(appt)
    logger.info("Rescheduled appointment id=%s to %s", appointment_id, new_time)
    return appt


def update_appointment_status(db: Session, appointment_id: int, status: str) -> Optional[models.Appointment]:
    appt = get_appointment(db, appointment_id)
    if not appt:
        logger.warning("Update status failed: appointment not found id=%s", appointment_id)
        return None
    appt.status = status
    db.commit()
    db.refresh(appt)
    logger.info("Updated appointment id=%s status=%s", appointment_id, status)
    return appt


# -------------------------
# Medicines
# -------------------------
def create_medicine(db: Session, payload: schemas.MedicineCreate) -> models.Medicine:
    m = models.Medicine(**payload.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    logger.info("Created medicine id=%s name=%s qty=%s", m.id, m.name, m.quantity)
    return m


def get_medicine(db: Session, medicine_id: int) -> Optional[models.Medicine]:
    return db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()


def search_medicines(db: Session, q: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[models.Medicine]:
    qs = db.query(models.Medicine)
    if q:
        like = f"%{q}%"
        qs = qs.filter(models.Medicine.name.like(like))
    results = qs.order_by(models.Medicine.name).offset(skip).limit(limit).all()
    logger.info("Searched medicines q=%s skip=%s limit=%s returned=%s", q, skip, limit, len(results))
    return results


def adjust_medicine_stock(db: Session, medicine_id: int, delta: int) -> Optional[models.Medicine]:
    m = get_medicine(db, medicine_id)
    if not m:
        logger.warning("Adjust stock failed: medicine not found id=%s", medicine_id)
        return None
    m.quantity = max(0, m.quantity + delta)
    db.commit()
    db.refresh(m)
    logger.info("Adjusted medicine id=%s delta=%s new_qty=%s", m.id, delta, m.quantity)
    return m


# -------------------------
# Users / Auth
# -------------------------
def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    """
    Creates user with hashed password. If username already exists, returns None.
    """
    existing = get_user_by_username(db, payload.username)
    if existing:
        logger.warning("Create user failed: username exists %s", payload.username)
        return None
    hashed = auth.get_password_hash(payload.password)
    u = models.User(username=payload.username, full_name=payload.full_name, role=payload.role, hashed_password=hashed)
    db.add(u)
    db.commit()
    db.refresh(u)
    logger.info("Created user id=%s username=%s role=%s", u.id, u.username, u.role)
    return u


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    u = get_user_by_username(db, username)
    if not u:
        logger.info("Authentication failed: username not found %s", username)
        return None
    if not auth.verify_password(password, u.hashed_password):
        logger.info("Authentication failed: invalid password for %s", username)
        return None
    logger.info("Authenticated user %s", username)
    return u

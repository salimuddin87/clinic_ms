# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.appointment_service import AppointmentService
from ..schemas import AppointmentCreate, AppointmentOut
from ..auth import require_roles
from typing import List
from datetime import datetime

router = APIRouter(prefix="/appointments", tags=["appointments"])


def send_reminder_stub(patient_phone: str, when: datetime):
    # stub: integrate with SMS/email provider (Twilio/SendGrid)
    print(f"Reminder would be sent to {patient_phone} about appointment at {when}")


@router.post("", response_model=AppointmentOut, status_code=201, dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def create_appointment(payload: AppointmentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    svc = AppointmentService(db)
    try:
        appt = svc.create(payload)
    except ValueError:
        raise HTTPException(status_code=404, detail="Patient not found")
    # schedule reminder as background task (example: send 24 hours before)
    # In real app you'd calculate when and use a scheduler (Celery/Redis/APS)
    # Here we just schedule a simple background task run immediately for demo
    background_tasks.add_task(send_reminder_stub, "patient-phone-placeholder", appt.scheduled_at)
    return appt


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentOut, dependencies=[Depends(require_roles("doctor","admin"))])
def reschedule(appointment_id: int, new_time: datetime, db: Session = Depends(get_db)):
    svc = AppointmentService(db)
    appt = svc.reschedule(appointment_id, new_time)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut, dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def cancel(appointment_id: int, db: Session = Depends(get_db)):
    svc = AppointmentService(db)
    appt = svc.cancel(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.get("", response_model=List[AppointmentOut], dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def list_appointments(page: int = Query(1, ge=1), status: str | None = None, db: Session = Depends(get_db)):
    per_page = 10
    skip = (page-1)*per_page
    svc = AppointmentService(db)
    return svc.list(skip=skip, limit=per_page, status=status)

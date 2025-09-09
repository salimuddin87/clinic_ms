# app/services/appointment_service.py
from .base_service import BaseService
from ..models import Appointment, Patient
from ..schemas import AppointmentCreate
from typing import List, Optional
from datetime import datetime


class AppointmentService(BaseService):
    def create(self, payload: AppointmentCreate) -> Appointment:
        # ensure patient exists
        patient = self.db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if not patient:
            raise ValueError("Patient not found")
        a = Appointment(patient_id=payload.patient_id, scheduled_at=payload.scheduled_at, reason=payload.reason)
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        self.logger.info("Created appointment id=%s", a.id)
        return a

    def get(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def list(self, skip: int = 0, limit: int = 10, status: Optional[str] = None) -> List[Appointment]:
        qs = self.db.query(Appointment)
        if status:
            qs = qs.filter(Appointment.status == status)
        return qs.order_by(Appointment.scheduled_at).offset(skip).limit(limit).all()

    def reschedule(self, appointment_id: int, new_time: datetime) -> Optional[Appointment]:
        a = self.get(appointment_id)
        if not a:
            return None
        a.scheduled_at = new_time
        self.db.commit()
        self.db.refresh(a)
        self.logger.info("Rescheduled appointment %s -> %s", appointment_id, new_time)
        return a

    def cancel(self, appointment_id: int) -> Optional[Appointment]:
        a = self.get(appointment_id)
        if not a:
            return None
        a.status = "canceled"
        self.db.commit()
        self.db.refresh(a)
        self.logger.info("Canceled appointment %s", appointment_id)
        return a

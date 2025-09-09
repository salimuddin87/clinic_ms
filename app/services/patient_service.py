# app/services/patient_service.py
from .base_service import BaseService
from ..models import Patient
from ..schemas import PatientCreate
from typing import List, Optional


class PatientService(BaseService):
    def create(self, payload: PatientCreate) -> Patient:
        p = Patient(**payload.dict())
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        self.logger.info("Created patient id=%s", p.id)
        return p

    def get(self, patient_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def list(self, skip: int = 0, limit: int = 10, q: Optional[str] = None) -> List[Patient]:
        qs = self.db.query(Patient)
        if q:
            like = f"%{q}%"
            qs = qs.filter((Patient.first_name.like(like)) | (Patient.last_name.like(like)) | (Patient.phone.like(like)))
        return qs.order_by(Patient.id).offset(skip).limit(limit).all()

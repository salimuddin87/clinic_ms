# app/services/medicine_service.py
from .base_service import BaseService
from ..models import Medicine
from ..schemas import MedicineCreate
from typing import List, Optional


class MedicineService(BaseService):
    def create(self, payload: MedicineCreate) -> Medicine:
        m = Medicine(**payload.dict())
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        self.logger.info("Created medicine id=%s", m.id)
        return m

    def get(self, medicine_id: int) -> Optional[Medicine]:
        return self.db.query(Medicine).filter(Medicine.id == medicine_id).first()

    def search(self, q: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[Medicine]:
        qs = self.db.query(Medicine)
        if q:
            like = f"%{q}%"
            qs = qs.filter(Medicine.name.like(like))
        return qs.order_by(Medicine.name).offset(skip).limit(limit).all()

    def adjust(self, medicine_id: int, delta: int) -> Optional[Medicine]:
        m = self.get(medicine_id)
        if not m:
            return None
        m.quantity = max(0, m.quantity + delta)
        self.db.commit()
        self.db.refresh(m)
        self.logger.info("Adjusted medicine %s by %s -> now %s", m.id, delta, m.quantity)
        return m

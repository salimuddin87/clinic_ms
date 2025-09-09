# app/routers/reports.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import require_roles
from app.models import Patient, Appointment, Medicine
from app.logger_config import get_logger
from datetime import datetime

logger = get_logger("clinic.reports")
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overview", dependencies=[Depends(require_roles("admin","doctor"))])
def overview(db: Session = Depends(get_db)):
    total_patients = db.query(Patient).count()
    upcoming = db.query(Appointment).filter(Appointment.scheduled_at >= datetime.utcnow(), Appointment.status == "scheduled").count()
    low_stock = db.query(Medicine).filter(Medicine.quantity <= Medicine.reorder_threshold).count()
    logger.info("Report overview requested")
    return {"total_patients": total_patients, "upcoming_appointments": upcoming, "low_stock_medicines": low_stock}

# app/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.patient_service import PatientService
from app.schemas import PatientCreate, PatientOut
from app.auth import require_roles, get_current_user
from app.cache import cache
from typing import List
import json

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=201, dependencies=[Depends(require_roles("doctor","nurse","admin"))])
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    svc = PatientService(db)
    p = svc.create(payload)
    # invalidate general patient list cache
    cache.set("patients:invalidate", "1", ttl=1)
    return p


@router.get("/{patient_id}", response_model=PatientOut, dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    cache_key = f"patient:{patient_id}"
    cached = cache.get(cache_key)
    if cached:
        # cached is JSON string
        return json.loads(cached)
    svc = PatientService(db)
    p = svc.get(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    out = PatientOut.from_orm(p).dict()
    cache.set(cache_key, out)
    return out


@router.get("", response_model=List[PatientOut], dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def list_patients(page: int = Query(1, ge=1), q: str | None = None, db: Session = Depends(get_db)):
    per_page = 10
    skip = (page-1)*per_page
    svc = PatientService(db)
    results = svc.list(skip=skip, limit=per_page, q=q)
    return results

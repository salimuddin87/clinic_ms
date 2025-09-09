# app/routers/medicines.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.medicine_service import MedicineService
from app.schemas import MedicineCreate, MedicineOut
from app.auth import require_roles
from app.cache import cache
import json

router = APIRouter(prefix="/medicines", tags=["medicines"])


@router.post("", response_model=MedicineOut, status_code=201, dependencies=[Depends(require_roles("admin","staff"))])
def add_medicine(payload: MedicineCreate, db: Session = Depends(get_db)):
    svc = MedicineService(db)
    m = svc.create(payload)
    cache.set("medicines:invalidate", "1", ttl=1)
    return m


@router.get("/{medicine_id}", response_model=MedicineOut, dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    svc = MedicineService(db)
    m = svc.get(medicine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return m


@router.get("", response_model=List[MedicineOut], dependencies=[Depends(require_roles("doctor","nurse","admin","staff"))])
def search_medicines(q: str | None = None, page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    per_page = 10
    skip = (page-1)*per_page
    cache_key = f"medicines:search:{q or ''}:page:{page}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    svc = MedicineService(db)
    res = svc.search(q=q, skip=skip, limit=per_page)
    out = [MedicineOut.from_orm(r).dict() for r in res]
    cache.set(cache_key, out)
    # log low stock
    for r in res:
        if r.quantity <= r.reorder_threshold:
            # simple log; you can trigger notifications
            pass
    return out


@router.patch("/{medicine_id}/adjust", response_model=MedicineOut, dependencies=[Depends(require_roles("admin","staff"))])
def adjust_medicine(medicine_id: int, delta: int = 0, db: Session = Depends(get_db)):
    svc = MedicineService(db)
    m = svc.adjust(medicine_id, delta)
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return m

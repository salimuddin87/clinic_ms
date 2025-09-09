# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.logger_config import get_logger
from app.routers import users, patients, appointments, medicines, reports
# from app.cache import redis_client

logger = get_logger("clinic.main")

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic Management System")

# include routers
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(medicines.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}

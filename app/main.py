# app/main.py
from fastapi import FastAPI
from .database import engine, Base
from .logger_config import get_logger
from .routers import users, patients, appointments, medicines, reports
# from .cache import redis_client

logger = get_logger("clinic.main")

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic OOP Management System")

# include routers
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(medicines.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}

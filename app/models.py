# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    dob = Column(String)  # simple ISO date string
    gender = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    medical_history = Column(Text)

    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    reason = Column(String)
    status = Column(String, default="scheduled")  # scheduled/completed/canceled
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")


class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    manufacturer = Column(String)
    quantity = Column(Integer, default=0)
    description = Column(Text)
    reorder_threshold = Column(Integer, default=5)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    role = Column(String, default="staff")  # admin, doctor, nurse, staff
    hashed_password = Column(String, nullable=False)

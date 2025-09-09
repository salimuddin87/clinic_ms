# app/services/base_service.py
from sqlalchemy.orm import Session
from app.logger_config import get_logger

logger = get_logger("clinic.base_service")


class BaseService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger

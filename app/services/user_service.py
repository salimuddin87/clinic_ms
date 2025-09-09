# app/services/user_service.py
from app.services.base_service import BaseService
from app.models import User
from app.schemas import UserCreate
from app.auth import get_password_hash, verify_password
from typing import Optional


class UserService(BaseService):
    def create(self, payload: UserCreate) -> User:
        hashed = get_password_hash(payload.password)
        u = User(username=payload.username, full_name=payload.full_name, role=payload.role, hashed_password=hashed)
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        self.logger.info("Created user %s role=%s", u.username, u.role)
        return u

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        u = self.get_by_username(username)
        if not u:
            return None
        if not verify_password(password, u.hashed_password):
            return None
        return u

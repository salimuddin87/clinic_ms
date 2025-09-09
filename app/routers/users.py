# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import UserService
from app.schemas import UserCreate, Token
from app.auth import create_access_token, get_db as auth_db_getter
from app.logger_config import get_logger

logger = get_logger("clinic.routes.users")
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    svc = UserService(db)
    if svc.get_by_username(payload.username):
        raise HTTPException(status_code=400, detail="Username exists")
    user = svc.create(payload)
    return {"id": user.id, "username": user.username, "role": user.role}


@router.post("/token", response_model=Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    logger.info("User %s logged in", user.username)
    return {"access_token": access_token, "token_type": "bearer"}

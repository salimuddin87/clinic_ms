from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    available: Optional[bool] = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    available: Optional[bool] = None


class ItemOut(ItemBase):
    id: int

    class Config:
        orm_mode = True

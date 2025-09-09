from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    available = Column(Boolean, default=True)

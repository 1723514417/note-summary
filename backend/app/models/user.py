from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime
import pytz


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")),
    )

    notes = relationship("Note", back_populates="owner")
    categories = relationship("Category", back_populates="owner")

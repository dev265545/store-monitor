from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    timestamp_utc = Column(DateTime)
    status = Column(String)

    store = relationship("Store", back_populates="status_records")

class BusinessHours(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    day_of_week = Column(Integer)
    start_time_local = Column(String)
    end_time_local = Column(String)

    store = relationship("Store", back_populates="business_hours")

class Store(Base):
    __tablename__ = "store"

    id = Column(Integer, primary_key=True, index=True)
    timezone_str = Column(String)

    status_records = relationship("StoreStatus", back_populates="store")
    business_hours = relationship("BusinessHours", back_populates="store")

class Report(Base):
    __tablename__ = "report"

    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    created_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
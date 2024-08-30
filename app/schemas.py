from pydantic import BaseModel
from datetime import datetime

class StoreStatusBase(BaseModel):
    store_id: int
    timestamp_utc: datetime
    status: str

class StoreStatusCreate(StoreStatusBase):
    pass

class StoreStatus(StoreStatusBase):
    id: int

    class Config:
        orm_mode = True

class BusinessHoursBase(BaseModel):
    store_id: int
    day_of_week: int
    start_time_local: str
    end_time_local: str

class BusinessHoursCreate(BusinessHoursBase):
    pass

class BusinessHours(BusinessHoursBase):
    id: int

    class Config:
        orm_mode = True

class StoreBase(BaseModel):
    id: int
    timezone_str: str

class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    status_records: list[StoreStatus] = []
    business_hours: list[BusinessHours] = []

    class Config:
        orm_mode = True

class ReportBase(BaseModel):
    id: str
    status: str
    created_at: datetime

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    completed_at: datetime | None = None

    class Config:
        orm_mode = True

class ReportResponse(BaseModel):
    report_id: str

class ReportStatus(BaseModel):
    status: str
    report_url: str | None = None
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid
from app.shared_lib import utils
from datetime import date

class DeliverAddress(BaseModel):
    province_id: str
    district_id: str

class CourierBase(BaseModel):
    courier_id: str = None
    name: constr(min_length=3)
    age: int
    email: EmailStr
    phone: constr(pattern=r'^\d{10}$')
    date_of_birth: date
    deliver_address: DeliverAddress
    created_at: datetime = None
    updated_at: datetime = None
    def __init__(self, **data):
        super().__init__(**data)
        self.courier_id = str(uuid.uuid4()).replace('-', '')
        self.created_at = utils._get_current_datetime()
        self.updated_at = self.created_at
        self.date_of_birth = self.date_of_birth.isoformat() if isinstance(self.date_of_birth, date) else self.date_of_birth

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid
from app.shared_lib import utils

class CustomerBase(BaseModel):
    customer_id: str = None
    name: str
    age: int
    email: EmailStr
    phone: str
    date_of_birth: str
    created_at: datetime = None
    updated_at: datetime = None
    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = utils._get_current_datetime()
        self.customer_id = str(uuid.uuid4()).replace('-', '')
        self.updated_at = self.created_at

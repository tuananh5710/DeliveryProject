from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
from app.shared_lib import utils

class Priority(str, Enum):
    IMMEDIATE = "immediate" # Hàng giao ngay ( độ ưu tiên 1 )
    PRIORITY = "priority" # Hàng ưu tiên ( độ ưu tiên 2 )
    STANDARD = "standard" # Hàng phổ thông ( độ ưu tiên 3 )

class StatusOrder(str, Enum):
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETE = "complete"
    CANCELLED = "cancelled"

class ProductType(str, Enum):
    PERISHABLE = "perishable"
    NON_PERISHABLE = "non_perishable"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FURNITURE = "furniture"

class DeliveryType(str, Enum):
    NORMAL = "normal"
    SCHEDULE = "schedule"

class Address(BaseModel):
    receiver_phone: constr(pattern=r'^\d{10}$')
    receiver_name: str
    province_id: str
    district_id: str
    ward_id: str
    street: str

class OrderBase(BaseModel):
    order_id: str = None
    customer_id: str
    priority_level: Priority
    created_at: datetime = None
    updated_at: datetime = None
    delivery_schedule: str = None
    delivery_type: DeliveryType
    address_delivery: Address
    product_type: ProductType
    status: str = None
    def __init__(self, **data):
        super().__init__(**data)
        self.order_id = str(uuid.uuid4())
        self.created_at = utils._get_current_datetime()
        self.updated_at = self.created_at
        self.status = StatusOrder.PROCESSING.value

class FilterParamsRequest(BaseModel):
    courier_id: str
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    priority_level: Optional[Priority] = None
    product_type: Optional[ProductType] = None
    status: Optional[StatusOrder] = None

class UpdateOffersRequest(BaseModel):
    courier_id: str
    list_offers: List[str]
    current_status: StatusOrder

class CompleteOfferRequest(BaseModel):
    courier_id: str
    offer_id: str
    image: str
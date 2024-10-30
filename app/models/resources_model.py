from pydantic import BaseModel
from enum import Enum

class AddressTypeResouces(str, Enum):
    PROVINCE = "province"
    DISTRICT = "district"
    WARD = "ward"

class AddressTypeMapping(str, Enum):
    PROVINCE = "address_province"
    DISTRICT = "address_district"
    WARD = "address_ward"

class AddressResources(BaseModel):
    address_id: str = None
    address_type: AddressTypeResouces

def map_address_type(address_type: AddressTypeResouces) -> AddressTypeMapping:
    mapping = {
        AddressTypeResouces.PROVINCE: AddressTypeMapping.PROVINCE,
        AddressTypeResouces.DISTRICT: AddressTypeMapping.DISTRICT,
        AddressTypeResouces.WARD: AddressTypeMapping.WARD,
    }
    return mapping.get(address_type)
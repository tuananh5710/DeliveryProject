from fastapi import APIRouter
from typing import List, Optional
# from core.helpers.cache import Cache
from app.logic.resources_logic import _get_resources
from app.models.resources_model import AddressResources

resources_router = APIRouter(prefix='/resources')

@resources_router.post("/")
async def get_resources(address_resources: AddressResources):
    return await _get_resources(address_resources)
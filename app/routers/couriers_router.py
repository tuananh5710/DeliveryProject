from fastapi import APIRouter
from typing import List, Optional
from app.models.couriers_model import CourierBase
from app.models.orders_model import UpdateOffersRequest, CompleteOfferRequest
from app.logic.couriers_logic import _create_couriers, _couriers_fetch_offer, _couriers_update_offers, _couriers_complete_offer

couriers_router = APIRouter(prefix='/couriers')

@couriers_router.post("/create")
def create_couriers(courier: CourierBase):
    return _create_couriers(courier)

@couriers_router.get("/fetch-offer")
def couriers_fetch_offer( courier_id: str ,page_number: int):
    return _couriers_fetch_offer(courier_id, page_number)

@couriers_router.post("/update-offers")
def couriers_update_offers(update_offers: UpdateOffersRequest):
    return _couriers_update_offers(update_offers)

@couriers_router.post("/complete-offer")
def couriers_complete_offer(complete_offer: CompleteOfferRequest):
    return _couriers_complete_offer(complete_offer)
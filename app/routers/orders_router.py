from fastapi import APIRouter
from typing import List, Optional
from app.models.orders_model import OrderBase, Priority, ProductType, StatusOrder
from app.logic.orders_logic import _create_orders, _filter_orders

order_router = APIRouter(prefix='/orders')


@order_router.post("/create")
def create_order(order: OrderBase):
    return _create_orders(order)

@order_router.get("/filter")
def filter_by_customer_id(
    customer_id: Optional[str] = None,
    courier_id: Optional[str] = None,
    order_id: Optional[str] = None,
    priority_level: Optional[Priority] = None,
    product_type: Optional[ProductType] = None,
    status: Optional[StatusOrder] = None):

    return _filter_orders(customer_id, courier_id, order_id, priority_level, product_type, status)
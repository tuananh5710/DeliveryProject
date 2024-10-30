from fastapi import APIRouter
from typing import List, Optional
from app.models.customers_model import CustomerBase
from app.logic.customers_logic import _create_users

users_router = APIRouter(prefix='/customers')

@users_router.post("/create")
def create_users(user: CustomerBase):
    return _create_users(user)

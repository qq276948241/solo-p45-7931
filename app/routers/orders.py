from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OrderStatus, CageType
from app.schemas import (
    OrderCreate, OrderUpdate, OrderOut,
    WaitlistCreate, WaitlistOut, WaitlistPosition, OrderCreateResult,
)
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["寄养订单"])


@router.post("/", response_model=OrderCreateResult, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db, data)


@router.get("/", response_model=List[OrderOut])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    pet_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return order_service.list_orders(db, status, pet_id, skip, limit)


@router.get("/staying", response_model=List[OrderOut])
def list_staying_pets(
    date: date = Query(..., description="查询日期"),
    db: Session = Depends(get_db),
):
    return order_service.list_staying_orders(db, date)


@router.post("/waitlist", response_model=WaitlistOut, status_code=201)
def add_waitlist(data: WaitlistCreate, db: Session = Depends(get_db)):
    return order_service.add_to_waitlist(db, data)


@router.get("/waitlist", response_model=List[WaitlistOut])
def list_waitlist(
    cage_type: Optional[CageType] = None,
    db: Session = Depends(get_db),
):
    return order_service.list_waitlist(db, cage_type)


@router.get("/waitlist/{waitlist_id}/position", response_model=WaitlistPosition)
def get_waitlist_position(waitlist_id: int, db: Session = Depends(get_db)):
    return order_service.get_waitlist_position(db, waitlist_id)


@router.delete("/waitlist/{waitlist_id}", status_code=204)
def remove_waitlist(waitlist_id: int, db: Session = Depends(get_db)):
    order_service.remove_from_waitlist(db, waitlist_id)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_order(db, order_id)


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    return order_service.update_order(db, order_id, data)


@router.delete("/{order_id}", status_code=204)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order_service.cancel_order(db, order_id)

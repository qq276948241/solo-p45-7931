from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, Pet, OrderStatus, CageType, Billing
from app.schemas import OrderCreate, OrderUpdate, OrderOut
from app.pricing import calculate_fee

router = APIRouter(prefix="/orders", tags=["寄养订单"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    order = Order(**data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    if data.status == OrderStatus.checked_out and data.check_out:
        days = max(1, (data.check_out - data.check_in).days)
        fee = calculate_fee(data.cage_type.value, days)
        billing = Billing(order_id=order.id, days=days, total_amount=fee, is_paid=False)
        db.add(billing)
        db.commit()
    return order


@router.get("/", response_model=List[OrderOut])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    pet_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if status is not None:
        query = query.filter(Order.status == status)
    if pet_id is not None:
        query = query.filter(Order.pet_id == pet_id)
    return query.offset(skip).limit(limit).all()


@router.get("/staying", response_model=List[OrderOut])
def list_staying_pets(
    date: date = Query(..., description="查询日期"),
    db: Session = Depends(get_db),
):
    target_start = datetime.combine(date, datetime.min.time())
    target_end = datetime.combine(date, datetime.max.time())
    orders = (
        db.query(Order)
        .filter(
            Order.status == OrderStatus.checked_in,
            Order.check_in <= target_end,
        )
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    update_data = data.model_dump(exclude_unset=True)
    old_status = order.status
    for key, value in update_data.items():
        setattr(order, key, value)
    if order.status == OrderStatus.checked_out and order.check_out and not order.billing:
        days = max(1, (order.check_out - order.check_in).days)
        fee = calculate_fee(order.cage_type.value, days)
        billing = Billing(order_id=order.id, days=days, total_amount=fee, is_paid=False)
        db.add(billing)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    db.delete(order)
    db.commit()

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Order, Pet, OrderStatus, CageType, Billing, Waitlist
from app.schemas import OrderCreate, OrderUpdate, WaitlistCreate, OrderCreateResult
from app.pricing import calculate_fee, get_cage_capacity


def _count_overlapping_orders(db: Session, cage_type: CageType, check_in: datetime, check_out: datetime, exclude_order_id: Optional[int] = None) -> int:
    query = db.query(Order).filter(
        Order.cage_type == cage_type,
        Order.status != OrderStatus.checked_out,
        Order.check_in < check_out,
        (Order.check_out == None) | (Order.check_out > check_in),
    )
    if exclude_order_id is not None:
        query = query.filter(Order.id != exclude_order_id)
    return query.count()


def _create_billing_for_order(db: Session, order: Order) -> None:
    if order.status != OrderStatus.checked_out or not order.check_out:
        return
    if order.billing:
        return
    days = max(1, (order.check_out - order.check_in).days)
    fee = calculate_fee(order.cage_type.value, days)
    db.add(Billing(order_id=order.id, days=days, total_amount=fee, is_paid=False))
    db.commit()


def _promote_next_waitlist(db: Session, cage_type: CageType, check_in: datetime, check_out: Optional[datetime]) -> Optional[Order]:
    effective_check_out = check_out or check_in
    waitlist_entry = (
        db.query(Waitlist)
        .filter(
            Waitlist.cage_type == cage_type,
            Waitlist.check_in < effective_check_out,
            Waitlist.check_out > check_in,
        )
        .order_by(Waitlist.created_at.asc())
        .first()
    )
    if not waitlist_entry:
        return None
    order = Order(
        pet_id=waitlist_entry.pet_id,
        cage_type=waitlist_entry.cage_type,
        check_in=waitlist_entry.check_in,
        check_out=waitlist_entry.check_out,
        status=OrderStatus.reserved,
    )
    db.add(order)
    db.delete(waitlist_entry)
    db.commit()
    db.refresh(order)
    _create_billing_for_order(db, order)
    return order


def create_order(db: Session, data: OrderCreate) -> OrderCreateResult:
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if data.check_out and data.check_out <= data.check_in:
        raise HTTPException(status_code=400, detail="离店时间必须晚于入住时间")
    check_out = data.check_out
    effective_check_out = check_out or data.check_in
    capacity = get_cage_capacity(data.cage_type.value)
    occupied = _count_overlapping_orders(db, data.cage_type, data.check_in, effective_check_out)
    if occupied >= capacity:
        if not check_out:
            raise HTTPException(status_code=400, detail="笼位已满，加入候补需提供离店时间")
        waitlist_entry = Waitlist(
            pet_id=data.pet_id,
            cage_type=data.cage_type,
            check_in=data.check_in,
            check_out=check_out,
        )
        db.add(waitlist_entry)
        db.commit()
        db.refresh(waitlist_entry)
        return OrderCreateResult(
            order=None,
            waitlist=waitlist_entry,
            message="笼位已满，已加入候补队列",
        )
    order = Order(**data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    _create_billing_for_order(db, order)
    return OrderCreateResult(order=order, waitlist=None, message="订单创建成功")


def cancel_order(db: Session, order_id: int) -> Tuple[Order, Optional[Order]]:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    cage_type = order.cage_type
    check_in = order.check_in
    check_out = order.check_out
    db.delete(order)
    db.commit()
    promoted = _promote_next_waitlist(db, cage_type, check_in, check_out)
    return order, promoted


def update_order(db: Session, order_id: int, data: OrderUpdate) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    update_data = data.model_dump(exclude_unset=True)
    new_check_in = update_data.get("check_in", order.check_in)
    new_check_out = update_data.get("check_out", order.check_out)
    new_cage_type = update_data.get("cage_type", order.cage_type)
    if new_check_out and new_check_out <= new_check_in:
        raise HTTPException(status_code=400, detail="离店时间必须晚于入住时间")
    effective_check_out = new_check_out or new_check_in
    capacity = get_cage_capacity(new_cage_type.value)
    occupied = _count_overlapping_orders(db, new_cage_type, new_check_in, effective_check_out, exclude_order_id=order_id)
    if occupied >= capacity:
        raise HTTPException(status_code=400, detail="该时段所选笼位已满")
    for key, value in update_data.items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    _create_billing_for_order(db, order)
    return order


def add_to_waitlist(db: Session, data: WaitlistCreate) -> Waitlist:
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if data.check_out <= data.check_in:
        raise HTTPException(status_code=400, detail="离店时间必须晚于入住时间")
    waitlist_entry = Waitlist(**data.model_dump())
    db.add(waitlist_entry)
    db.commit()
    db.refresh(waitlist_entry)
    return waitlist_entry


def get_waitlist_position(db: Session, waitlist_id: int) -> dict:
    entry = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="候补记录不存在")
    position = (
        db.query(Waitlist)
        .filter(
            Waitlist.cage_type == entry.cage_type,
            Waitlist.check_in < entry.check_out,
            Waitlist.check_out > entry.check_in,
            Waitlist.created_at <= entry.created_at,
        )
        .count()
    )
    return {
        "waitlist_id": entry.id,
        "pet_id": entry.pet_id,
        "position": position,
        "cage_type": entry.cage_type,
        "check_in": entry.check_in,
        "check_out": entry.check_out,
    }


def remove_from_waitlist(db: Session, waitlist_id: int) -> None:
    entry = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="候补记录不存在")
    db.delete(entry)
    db.commit()


def list_waitlist(db: Session, cage_type: Optional[CageType] = None) -> list:
    query = db.query(Waitlist)
    if cage_type is not None:
        query = query.filter(Waitlist.cage_type == cage_type)
    return query.order_by(Waitlist.created_at.asc()).all()


def list_staying_orders(db: Session, target_date: datetime) -> list:
    target_start = datetime.combine(target_date, datetime.min.time())
    target_end = datetime.combine(target_date, datetime.max.time())
    return (
        db.query(Order)
        .filter(
            Order.status == OrderStatus.checked_in,
            Order.check_in <= target_end,
        )
        .all()
    )


def list_orders(db: Session, status: Optional[OrderStatus], pet_id: Optional[int], skip: int, limit: int) -> list:
    query = db.query(Order)
    if status is not None:
        query = query.filter(Order.status == status)
    if pet_id is not None:
        query = query.filter(Order.pet_id == pet_id)
    return query.offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, extract, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Billing, Order
from app.schemas import BillingOut, BillingUpdate, MonthlyRevenue

router = APIRouter(prefix="/billing", tags=["收费结算"])


@router.get("/", response_model=List[BillingOut])
def list_billings(skip: int = 0, limit: int = 100, is_paid: bool = None, db: Session = Depends(get_db)):
    query = db.query(Billing)
    if is_paid is not None:
        query = query.filter(Billing.is_paid == is_paid)
    return query.offset(skip).limit(limit).all()


@router.get("/monthly-summary", response_model=MonthlyRevenue)
def monthly_summary(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
):
    result = (
        db.query(
            func.coalesce(func.sum(Billing.total_amount), 0).label("total_amount"),
            func.coalesce(func.sum(case((Billing.is_paid == True, Billing.total_amount), else_=0)), 0).label("paid_amount"),
            func.coalesce(func.sum(case((Billing.is_paid == False, Billing.total_amount), else_=0)), 0).label("unpaid_amount"),
            func.count(Billing.id).label("order_count"),
        )
        .join(Order, Billing.order_id == Order.id)
        .filter(extract("year", Order.check_out) == year, extract("month", Order.check_out) == month)
        .first()
    )
    return MonthlyRevenue(
        year=year,
        month=month,
        total_amount=result.total_amount,
        paid_amount=result.paid_amount,
        unpaid_amount=result.unpaid_amount,
        order_count=result.order_count,
    )


@router.get("/order/{order_id}", response_model=BillingOut)
def get_billing_by_order(order_id: int, db: Session = Depends(get_db)):
    billing = db.query(Billing).filter(Billing.order_id == order_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="该订单暂无账单")
    return billing


@router.get("/{billing_id}", response_model=BillingOut)
def get_billing(billing_id: int, db: Session = Depends(get_db)):
    billing = db.query(Billing).filter(Billing.id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="账单不存在")
    return billing


@router.put("/{billing_id}", response_model=BillingOut)
def update_billing(billing_id: int, data: BillingUpdate, db: Session = Depends(get_db)):
    billing = db.query(Billing).filter(Billing.id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="账单不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(billing, key, value)
    db.commit()
    db.refresh(billing)
    return billing

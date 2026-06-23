from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut

router = APIRouter(prefix="/customers", tags=["客户管理"])


@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/", response_model=List[CustomerOut])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    update_data = data.model_dump(exclude_unset=True)
    if "phone" in update_data and update_data["phone"] != customer.phone:
        existing = db.query(Customer).filter(Customer.phone == update_data["phone"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="该手机号已注册")
    for key, value in update_data.items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    db.delete(customer)
    db.commit()

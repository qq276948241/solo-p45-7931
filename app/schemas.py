from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models import CageType, OrderStatus


class CustomerCreate(BaseModel):
    name: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=20)


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=20)


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    emergency_contact: Optional[str]

    model_config = {"from_attributes": True}


class PetCreate(BaseModel):
    name: str = Field(..., max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = None
    vaccination_status: Optional[str] = Field(None, max_length=200)
    allergies: Optional[str] = Field(None, max_length=200)
    owner_id: int


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = None
    vaccination_status: Optional[str] = Field(None, max_length=200)
    allergies: Optional[str] = Field(None, max_length=200)
    owner_id: Optional[int] = None


class PetOut(BaseModel):
    id: int
    name: str
    breed: Optional[str]
    weight: Optional[float]
    vaccination_status: Optional[str]
    allergies: Optional[str]
    owner_id: int

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    pet_id: int
    cage_type: CageType = CageType.standard
    check_in: datetime
    check_out: Optional[datetime] = None
    status: OrderStatus = OrderStatus.reserved


class OrderUpdate(BaseModel):
    cage_type: Optional[CageType] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[OrderStatus] = None


class OrderOut(BaseModel):
    id: int
    pet_id: int
    cage_type: CageType
    check_in: datetime
    check_out: Optional[datetime]
    status: OrderStatus

    model_config = {"from_attributes": True}


class BillingOut(BaseModel):
    id: int
    order_id: int
    days: int
    total_amount: float
    is_paid: bool

    model_config = {"from_attributes": True}


class BillingUpdate(BaseModel):
    is_paid: Optional[bool] = None


class MonthlyRevenue(BaseModel):
    year: int
    month: int
    total_amount: float
    paid_amount: float
    unpaid_amount: float
    order_count: int

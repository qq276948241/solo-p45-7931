import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CageType(str, enum.Enum):
    standard = "standard"
    luxury = "luxury"


class OrderStatus(str, enum.Enum):
    reserved = "reserved"
    checked_in = "checked_in"
    checked_out = "checked_out"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    emergency_contact = Column(String(20), nullable=True)

    pets = relationship("Pet", back_populates="owner")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)
    vaccination_status = Column(String(200), nullable=True)
    allergies = Column(String(200), nullable=True)
    owner_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    owner = relationship("Customer", back_populates="pets")
    orders = relationship("Order", back_populates="pet")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    cage_type = Column(Enum(CageType), nullable=False, default=CageType.standard)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.reserved)

    pet = relationship("Pet", back_populates="orders")
    billing = relationship("Billing", back_populates="order", uselist=False)


class Billing(Base):
    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    days = Column(Integer, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0.0)
    is_paid = Column(Boolean, nullable=False, default=False)

    order = relationship("Order", back_populates="billing")

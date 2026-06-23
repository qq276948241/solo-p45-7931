from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pet, Customer
from app.schemas import PetCreate, PetUpdate, PetOut

router = APIRouter(prefix="/pets", tags=["宠物档案"])


@router.post("/", response_model=PetOut, status_code=201)
def create_pet(data: PetCreate, db: Session = Depends(get_db)):
    owner = db.query(Customer).filter(Customer.id == data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="主人不存在")
    pet = Pet(**data.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("/", response_model=List[PetOut])
def list_pets(skip: int = 0, limit: int = 100, owner_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Pet)
    if owner_id is not None:
        query = query.filter(Pet.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    return pet


@router.put("/{pet_id}", response_model=PetOut)
def update_pet(pet_id: int, data: PetUpdate, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    update_data = data.model_dump(exclude_unset=True)
    if "owner_id" in update_data:
        owner = db.query(Customer).filter(Customer.id == update_data["owner_id"]).first()
        if not owner:
            raise HTTPException(status_code=404, detail="主人不存在")
    for key, value in update_data.items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/{pet_id}", status_code=204)
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    db.delete(pet)
    db.commit()

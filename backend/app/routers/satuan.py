from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.satuan import Satuan
from app.schemas.satuan import SatuanCreate, SatuanUpdate, SatuanOut

router = APIRouter(prefix="/satuan", tags=["Satuan"])


@router.get("/", response_model=list[SatuanOut])
def list_satuan(db: Session = Depends(get_db)):
    return db.query(Satuan).all()


@router.get("/{satuan_id}", response_model=SatuanOut)
def get_satuan(satuan_id: int, db: Session = Depends(get_db)):
    item = db.query(Satuan).filter(Satuan.id == satuan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Satuan not found")
    return item


@router.post("/", response_model=SatuanOut, status_code=201)
def create_satuan(payload: SatuanCreate, db: Session = Depends(get_db)):
    item = Satuan(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{satuan_id}", response_model=SatuanOut)
def update_satuan(satuan_id: int, payload: SatuanUpdate, db: Session = Depends(get_db)):
    item = db.query(Satuan).filter(Satuan.id == satuan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Satuan not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{satuan_id}", status_code=204)
def delete_satuan(satuan_id: int, db: Session = Depends(get_db)):
    item = db.query(Satuan).filter(Satuan.id == satuan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Satuan not found")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Satuan ini masih dipakai di Master Material, gak bisa dihapus")

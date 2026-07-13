from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.kategori import Kategori
from app.schemas.kategori import KategoriCreate, KategoriUpdate, KategoriOut

router = APIRouter(tags=["Kategori"])


@router.get("/", response_model=list[KategoriOut])
def list_kategori(db: Session = Depends(get_db)):
    return db.query(Kategori).all()


@router.get("/{kategori_id}", response_model=KategoriOut)
def get_kategori(kategori_id: int, db: Session = Depends(get_db)):
    item = db.query(Kategori).filter(Kategori.id == kategori_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kategori not found")
    return item


@router.post("/", response_model=KategoriOut, status_code=201)
def create_kategori(payload: KategoriCreate, db: Session = Depends(get_db)):
    item = Kategori(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{kategori_id}", response_model=KategoriOut)
def update_kategori(kategori_id: int, payload: KategoriUpdate, db: Session = Depends(get_db)):
    item = db.query(Kategori).filter(Kategori.id == kategori_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kategori not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{kategori_id}", status_code=204)
def delete_kategori(kategori_id: int, db: Session = Depends(get_db)):
    item = db.query(Kategori).filter(Kategori.id == kategori_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kategori not found")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Kategori ini masih dipakai di Master Material, gak bisa dihapus")

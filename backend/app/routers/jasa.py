from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.jasa import Jasa
from app.schemas.jasa import JasaCreate, JasaUpdate, JasaOut

router = APIRouter(tags=["Jasa"])


@router.get("/", response_model=list[JasaOut])
def list_jasa(db: Session = Depends(get_db)):
    # Default urut sesuai 'urutan' (posisi di Excel) — yang null ditaro paling belakang
    return db.query(Jasa).order_by(Jasa.urutan.asc().nullslast(), Jasa.id).all()


@router.get("/{jasa_id}", response_model=JasaOut)
def get_jasa(jasa_id: int, db: Session = Depends(get_db)):
    item = db.query(Jasa).filter(Jasa.id == jasa_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Jasa not found")
    return item


@router.post("/", response_model=JasaOut, status_code=201)
def create_jasa(payload: JasaCreate, db: Session = Depends(get_db)):
    item = Jasa(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Jenis pekerjaan ini sudah ada di master Jasa")
    db.refresh(item)
    return item


@router.put("/{jasa_id}", response_model=JasaOut)
def update_jasa(jasa_id: int, payload: JasaUpdate, db: Session = Depends(get_db)):
    item = db.query(Jasa).filter(Jasa.id == jasa_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Jasa not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Jenis pekerjaan ini sudah ada di master Jasa")
    db.refresh(item)
    return item


@router.delete("/{jasa_id}", status_code=204)
def delete_jasa(jasa_id: int, db: Session = Depends(get_db)):
    item = db.query(Jasa).filter(Jasa.id == jasa_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Jasa not found")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Jasa ini masih dipakai di Barang Jasa, gak bisa dihapus")

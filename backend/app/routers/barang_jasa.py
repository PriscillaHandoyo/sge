from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.barang_jasa import BarangJasa
from app.models.kode_barang_customer import KodeBarangCustomer
from app.models.jasa import Jasa
from app.schemas.barang_jasa import BarangJasaCreate, BarangJasaUpdate, BarangJasaOut

router = APIRouter(tags=["Barang Jasa"])


@router.get("/", response_model=list[BarangJasaOut])
def list_barang_jasa(db: Session = Depends(get_db)):
    return db.query(BarangJasa).all()


@router.get("/by-kode-barang/{kode_barang_customer_id}", response_model=list[BarangJasaOut])
def list_by_kode_barang(kode_barang_customer_id: int, db: Session = Depends(get_db)):
    """List semua jasa (sampai 25) untuk satu kode barang customer, urut sesuai 'urutan'."""
    return (
        db.query(BarangJasa)
        .filter(BarangJasa.kode_barang_customer_id == kode_barang_customer_id)
        .order_by(BarangJasa.urutan)
        .all()
    )


@router.post("/", response_model=BarangJasaOut, status_code=201)
def create_barang_jasa(payload: BarangJasaCreate, db: Session = Depends(get_db)):
    kbc = db.query(KodeBarangCustomer).filter(KodeBarangCustomer.id == payload.kode_barang_customer_id).first()
    if not kbc:
        raise HTTPException(status_code=400, detail="kode_barang_customer_id tidak ditemukan")

    jasa = db.query(Jasa).filter(Jasa.id == payload.jasa_id).first()
    if not jasa:
        raise HTTPException(status_code=400, detail="jasa_id tidak ditemukan")

    item = BarangJasa(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=BarangJasaOut)
def update_barang_jasa(item_id: int, payload: BarangJasaUpdate, db: Session = Depends(get_db)):
    item = db.query(BarangJasa).filter(BarangJasa.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Barang Jasa not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_barang_jasa(item_id: int, db: Session = Depends(get_db)):
    item = db.query(BarangJasa).filter(BarangJasa.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Barang Jasa not found")
    db.delete(item)
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from app.services.excel_import import parse_supplier_excel

router = APIRouter(prefix="/suppliers", tags=["Supplier"])


@router.post("/import/preview")
def preview_import_suppliers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()

    try:
        rows = parse_supplier_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_rows = []
    duplicate_rows = []

    for row in rows:
        existing = db.query(Supplier).filter(Supplier.kode_sup == row["kode_sup"]).first()
        if existing:
            duplicate_rows.append({
                "kode_sup": row["kode_sup"],
                "existing": {
                    "nama_sup": existing.nama_sup,
                    "tipe": existing.tipe,
                    "direktur": existing.direktur,
                    "alamat": existing.alamat,
                },
                "incoming": row,
            })
        else:
            new_rows.append(row)

    return {"new": new_rows, "duplicates": duplicate_rows}


@router.post("/import/confirm")
def confirm_import_suppliers(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_rows = payload.get("new", [])
    update_rows = payload.get("updates", [])

    inserted = []
    updated = []

    for row in new_rows:
        db.add(Supplier(**row))
        inserted.append(row["kode_sup"])

    for row in update_rows:
        existing = db.query(Supplier).filter(Supplier.kode_sup == row["kode_sup"]).first()
        if existing:
            for key, value in row.items():
                if key != "kode_sup":
                    setattr(existing, key, value)
            updated.append(row["kode_sup"])

    db.commit()

    return {"inserted": inserted, "updated": updated}


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierOut, status_code=201)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["tipe"] = data["tipe"].value if hasattr(data["tipe"], "value") else data["tipe"]

    supplier = Supplier(**data)
    db.add(supplier)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="kode_sup sudah dipakai")
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, payload: SupplierUpdate, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    data = payload.model_dump()
    data["tipe"] = data["tipe"].value if hasattr(data["tipe"], "value") else data["tipe"]

    for key, value in data.items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()

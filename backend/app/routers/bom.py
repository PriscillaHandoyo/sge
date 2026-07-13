from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.bom import Bom
from app.models.customer import Customer
from app.models.kode_barang_customer import KodeBarangCustomer
from app.models.material import Material
from app.schemas.bom import BomCreate, BomUpdate, BomOut
from app.services.excel_import import parse_bom_excel

router = APIRouter(tags=["BOM"])


@router.post("/import/preview")
def preview_import_bom(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parse 4 sheet BOM (kabel/housing/terminal/lainnya), BELUM nyimpen apapun.
    Butuh Kode Barang Customer dan Material yang udah ada duluan di database
    (dari import 'input pekerjaan' dan 'Supplier_dan_Part_nya' sebelumnya) —
    kalau belum ketemu, baris itu di-skip + dilaporin.
    """
    content = file.file.read()

    try:
        rows = parse_bom_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    customers_by_kode = {c.kode_cust: c for c in db.query(Customer).all()}
    materials_by_nama = {m.nama_material.strip().lower(): m for m in db.query(Material).all()}
    kbc_cache: dict[tuple, object] = {}

    new_rows = []
    duplicate_rows = []
    invalid_customer = []
    invalid_kbc = []
    invalid_material = []

    for row in rows:
        customer = customers_by_kode.get(row["kode_cust"])
        if not customer:
            invalid_customer.append(f"{row['kode_barang']} (kode_cust {row['kode_cust']} tidak ditemukan)")
            continue

        cache_key = (row["kode_barang"], customer.id)
        if cache_key not in kbc_cache:
            kbc_cache[cache_key] = (
                db.query(KodeBarangCustomer)
                .filter(
                    KodeBarangCustomer.kode_barang == row["kode_barang"],
                    KodeBarangCustomer.customer_id == customer.id,
                )
                .first()
            )
        kbc = kbc_cache[cache_key]
        if not kbc:
            invalid_kbc.append(f"{row['kode_barang']} ({row['kode_cust']}) belum ada di Kode Barang Customer")
            continue

        material = materials_by_nama.get(row["nama_material"].strip().lower())
        if not material:
            invalid_material.append(f"{row['nama_material']} (dipakai di {row['kode_barang']})")
            continue

        existing = (
            db.query(Bom)
            .filter(Bom.kode_barang_customer_id == kbc.id, Bom.material_id == material.id)
            .first()
        )

        incoming = {
            "kode_barang_customer_id": kbc.id,
            "material_id": material.id,
            "penggunaan": row["penggunaan"],
        }

        if existing:
            duplicate_rows.append({
                "bom_key": f"{row['kode_barang']} — {material.nama_material}",
                "existing": {"label": f"penggunaan lama: {existing.penggunaan}"},
                "incoming": incoming,
            })
        else:
            new_rows.append(incoming)

    return {
        "new": new_rows,
        "duplicates": duplicate_rows,
        "invalid_customer": invalid_customer,
        "invalid_kbc": invalid_kbc,
        "invalid_material": invalid_material,
    }


@router.post("/import/confirm")
def confirm_import_bom(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_rows = payload.get("new", [])
    update_rows = payload.get("updates", [])

    inserted = []
    updated = []

    for row in new_rows:
        db.add(Bom(**row))
        inserted.append(f"kbc#{row['kode_barang_customer_id']}-mat#{row['material_id']}")

    for row in update_rows:
        existing = (
            db.query(Bom)
            .filter(
                Bom.kode_barang_customer_id == row["kode_barang_customer_id"],
                Bom.material_id == row["material_id"],
            )
            .first()
        )
        if existing:
            existing.penggunaan = row["penggunaan"]
            updated.append(f"kbc#{row['kode_barang_customer_id']}-mat#{row['material_id']}")

    db.commit()

    return {"inserted": inserted, "updated": updated}


@router.get("/", response_model=list[BomOut])
def list_bom(db: Session = Depends(get_db)):
    return db.query(Bom).all()


@router.get("/{bom_id}", response_model=BomOut)
def get_bom(bom_id: int, db: Session = Depends(get_db)):
    item = db.query(Bom).filter(Bom.id == bom_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bom not found")
    return item


@router.post("/", response_model=BomOut, status_code=201)
def create_bom(payload: BomCreate, db: Session = Depends(get_db)):
    item = Bom(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{bom_id}", response_model=BomOut)
def update_bom(bom_id: int, payload: BomUpdate, db: Session = Depends(get_db)):
    item = db.query(Bom).filter(Bom.id == bom_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bom not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{bom_id}", status_code=204)
def delete_bom(bom_id: int, db: Session = Depends(get_db)):
    item = db.query(Bom).filter(Bom.id == bom_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bom not found")
    db.delete(item)
    db.commit()

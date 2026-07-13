from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.material import Material
from app.models.supplier import Supplier
from app.models.kategori import Kategori
from app.models.satuan import Satuan
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
from app.services.excel_import import parse_material_excel

router = APIRouter(tags=["Material"])


@router.post("/import/preview")
def preview_import_materials(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parse sheet 'master part number per supp', BELUM nyimpen apapun.
    Kategori & satuan dari Excel di-lookup ke master Kategori/Satuan
    (by nama) — kalau gak ketemu (jarang kejadian kecuali master-nya
    diubah manual), baris itu di-skip + dilaporin di 'unmatched_master'.
    """
    content = file.file.read()

    try:
        rows = parse_material_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    suppliers_by_kode = {s.kode_sup: s for s in db.query(Supplier).all()}
    kategori_by_nama = {k.nama_kategori.lower(): k for k in db.query(Kategori).all()}
    satuan_by_nama = {s.nama_satuan.lower(): s for s in db.query(Satuan).all()}

    new_rows = []
    duplicate_rows = []
    invalid_supplier = []
    unmatched_master = []

    for row in rows:
        supplier = suppliers_by_kode.get(row["kode_sup"])
        if not supplier:
            invalid_supplier.append(f"{row['nama_material']} (supplier code {row['kode_sup']} tidak ditemukan)")
            continue

        kategori = kategori_by_nama.get(row["kategori"].lower())
        satuan = satuan_by_nama.get(row["satuan_terkecil"].lower())
        if not kategori or not satuan:
            unmatched_master.append(
                f"{row['nama_material']} (kategori '{row['kategori']}' atau satuan '{row['satuan_terkecil']}' tidak ditemukan di master)"
            )
            continue

        existing = (
            db.query(Material)
            .filter(Material.nama_material == row["nama_material"], Material.supplier_id == supplier.id)
            .first()
        )

        incoming = {
            "nama_material": row["nama_material"],
            "supplier_id": supplier.id,
            "satuan_id": satuan.id,
            "kategori_id": kategori.id,
        }

        if existing:
            duplicate_rows.append({
                "nama_material": row["nama_material"],
                "existing": {"label": f"{supplier.nama_sup} — kategori {existing.kategori_ref.nama_kategori}"},
                "incoming": incoming,
            })
        else:
            new_rows.append(incoming)

    return {
        "new": new_rows,
        "duplicates": duplicate_rows,
        "invalid_supplier": invalid_supplier,
        "unmatched_master": unmatched_master,
    }


@router.post("/import/confirm")
def confirm_import_materials(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_rows = payload.get("new", [])
    update_rows = payload.get("updates", [])

    inserted = []
    updated = []

    for row in new_rows:
        db.add(Material(**row))
        inserted.append(row["nama_material"])

    for row in update_rows:
        existing = (
            db.query(Material)
            .filter(Material.nama_material == row["nama_material"], Material.supplier_id == row["supplier_id"])
            .first()
        )
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
            updated.append(row["nama_material"])

    db.commit()

    return {"inserted": inserted, "updated": updated}


@router.get("/", response_model=list[MaterialOut])
def list_materials(db: Session = Depends(get_db)):
    return db.query(Material).all()


@router.get("/{material_id}", response_model=MaterialOut)
def get_material(material_id: int, db: Session = Depends(get_db)):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Material not found")
    return item


@router.post("/", response_model=MaterialOut, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == payload.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="supplier_id tidak ditemukan")

    kategori = db.query(Kategori).filter(Kategori.id == payload.kategori_id).first()
    if not kategori:
        raise HTTPException(status_code=400, detail="kategori_id tidak ditemukan")

    satuan = db.query(Satuan).filter(Satuan.id == payload.satuan_id).first()
    if not satuan:
        raise HTTPException(status_code=400, detail="satuan_id tidak ditemukan")

    item = Material(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{material_id}", response_model=MaterialOut)
def update_material(material_id: int, payload: MaterialUpdate, db: Session = Depends(get_db)):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Material not found")

    supplier = db.query(Supplier).filter(Supplier.id == payload.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="supplier_id tidak ditemukan")

    kategori = db.query(Kategori).filter(Kategori.id == payload.kategori_id).first()
    if not kategori:
        raise HTTPException(status_code=400, detail="kategori_id tidak ditemukan")

    satuan = db.query(Satuan).filter(Satuan.id == payload.satuan_id).first()
    if not satuan:
        raise HTTPException(status_code=400, detail="satuan_id tidak ditemukan")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: int, db: Session = Depends(get_db)):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(item)
    db.commit()

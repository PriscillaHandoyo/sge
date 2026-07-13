from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.kode_barang_customer import KodeBarangCustomer
from app.models.customer import Customer
from app.models.jasa import Jasa
from app.models.barang_jasa import BarangJasa
from app.schemas.kode_barang_customer import (
    KodeBarangCustomerCreate,
    KodeBarangCustomerUpdate,
    KodeBarangCustomerOut,
)
from app.services.excel_import import parse_pekerjaan_excel

router = APIRouter(tags=["Kode Barang Customer"])


@router.post("/import/preview")
def preview_import_pekerjaan(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()

    try:
        parsed = parse_pekerjaan_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    rows = parsed["rows"]
    job_order = parsed["job_order"]

    customers_by_kode = {c.kode_cust: c for c in db.query(Customer).all()}
    jasa_by_nama = {j.jenis_pekerjaan.strip().lower(): j for j in db.query(Jasa).all()}

    # new_jasa dihitung dari SEMUA 23 nama di header Excel, bukan cuma yang
    # kepake di baris manapun — biar master Jasa lengkap sesuai template,
    # termasuk jenis pekerjaan yang belum pernah dipilih di P/N manapun.
    new_jasa_names = {name for name in job_order if name.strip().lower() not in jasa_by_nama}

    new_rows = []
    duplicate_rows = []
    invalid_customer = []

    for row in rows:
        customer = customers_by_kode.get(row["kode_cust"])
        if not customer:
            invalid_customer.append(f"{row['kode_barang']} (kode_cust {row['kode_cust']} tidak ditemukan)")
            continue

        jasa_assignments = []
        for entry in row["jasa_entries"]:
            nama = entry["jenis_pekerjaan"]
            jasa = jasa_by_nama.get(nama.strip().lower())
            if jasa:
                jasa_assignments.append({
                    "jasa_id": jasa.id,
                    "jenis_pekerjaan": jasa.jenis_pekerjaan,
                    "urutan": entry["urutan"],
                })
            else:
                jasa_assignments.append({
                    "jasa_id": None,
                    "jenis_pekerjaan": nama,
                    "urutan": entry["urutan"],
                })

        existing_kbc = (
            db.query(KodeBarangCustomer)
            .filter(
                KodeBarangCustomer.kode_barang == row["kode_barang"],
                KodeBarangCustomer.customer_id == customer.id,
            )
            .first()
        )

        incoming = {
            "kode_barang": row["kode_barang"],
            "customer_id": customer.id,
            "jasa_assignments": jasa_assignments,
        }

        if existing_kbc:
            existing_jasa_count = (
                db.query(BarangJasa)
                .filter(BarangJasa.kode_barang_customer_id == existing_kbc.id)
                .count()
            )
            duplicate_rows.append({
                "kode_barang": row["kode_barang"],
                "existing": {
                    "label": f"{customer.nama_cust} — {existing_jasa_count} pekerjaan tersimpan",
                },
                "incoming": incoming,
            })
        else:
            new_rows.append(incoming)

    return {
        "new": new_rows,
        "duplicates": duplicate_rows,
        "invalid_customer": invalid_customer,
        "new_jasa": sorted(new_jasa_names),
        "job_order": parsed["job_order"],
    }


def _get_or_create_jasa(db: Session, name: str, job_order: list) -> int:
    """
    Cari Jasa by nama; kalau belum ada, bikin baru dengan urutan sesuai
    posisi kolomnya di Excel. Pakai try/except buat jaga-jaga race condition
    (2 request bersamaan) — unique constraint di DB bakal nolak yang ke-2,
    di sini kita tangkep dan pakai yang udah ke-insert duluan.
    """
    existing = db.query(Jasa).filter(Jasa.jenis_pekerjaan == name).first()
    if existing:
        return existing.id

    urutan = job_order.index(name) + 1 if name in job_order else None
    new_jasa = Jasa(jenis_pekerjaan=name, urutan=urutan)
    db.add(new_jasa)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.query(Jasa).filter(Jasa.jenis_pekerjaan == name).first()
        if existing:
            return existing.id
        raise
    return new_jasa.id


def _resolve_jasa_assignments(db: Session, assignments: list, name_to_id: dict) -> list:
    resolved = []
    for a in assignments:
        jasa_id = a["jasa_id"] if a["jasa_id"] is not None else name_to_id[a["jenis_pekerjaan"]]
        resolved.append({"jasa_id": jasa_id, "urutan": a["urutan"]})
    return resolved


@router.post("/import/confirm")
def confirm_import_pekerjaan(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_rows = payload.get("new", [])
    update_rows = payload.get("updates", [])
    job_order = payload.get("job_order", [])

    # Pastiin SEMUA jenis pekerjaan yang ada di header Excel (job_order)
    # tercatat di master Jasa — termasuk yang gak kepake di baris manapun.
    name_to_id = {name: _get_or_create_jasa(db, name, job_order) for name in job_order}

    # Jaga-jaga: kalau ada nama di jasa_assignments yang gak masuk job_order
    # (seharusnya gak kejadian, tapi defensif aja)
    for row in new_rows + update_rows:
        for assign in row["jasa_assignments"]:
            if assign["jasa_id"] is None and assign["jenis_pekerjaan"] not in name_to_id:
                name_to_id[assign["jenis_pekerjaan"]] = _get_or_create_jasa(
                    db, assign["jenis_pekerjaan"], job_order
                )

    inserted = []
    updated = []

    for row in new_rows:
        kbc = KodeBarangCustomer(kode_barang=row["kode_barang"], customer_id=row["customer_id"])
        db.add(kbc)
        db.flush()
        for assign in _resolve_jasa_assignments(db, row["jasa_assignments"], name_to_id):
            db.add(BarangJasa(
                kode_barang_customer_id=kbc.id,
                jasa_id=assign["jasa_id"],
                urutan=assign["urutan"],
            ))
        inserted.append(row["kode_barang"])

    for row in update_rows:
        kbc = (
            db.query(KodeBarangCustomer)
            .filter(
                KodeBarangCustomer.kode_barang == row["kode_barang"],
                KodeBarangCustomer.customer_id == row["customer_id"],
            )
            .first()
        )
        if not kbc:
            continue

        db.query(BarangJasa).filter(BarangJasa.kode_barang_customer_id == kbc.id).delete()
        for assign in _resolve_jasa_assignments(db, row["jasa_assignments"], name_to_id):
            db.add(BarangJasa(
                kode_barang_customer_id=kbc.id,
                jasa_id=assign["jasa_id"],
                urutan=assign["urutan"],
            ))
        updated.append(row["kode_barang"])

    db.commit()

    return {"inserted": inserted, "updated": updated}


@router.get("/", response_model=list[KodeBarangCustomerOut])
def list_kode_barang(db: Session = Depends(get_db)):
    return db.query(KodeBarangCustomer).all()


@router.get("/{item_id}", response_model=KodeBarangCustomerOut)
def get_kode_barang(item_id: int, db: Session = Depends(get_db)):
    item = db.query(KodeBarangCustomer).filter(KodeBarangCustomer.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kode barang customer not found")
    return item


@router.get("/by-customer/{customer_id}", response_model=list[KodeBarangCustomerOut])
def list_kode_barang_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return db.query(KodeBarangCustomer).filter(KodeBarangCustomer.customer_id == customer_id).all()


@router.post("/", response_model=KodeBarangCustomerOut, status_code=201)
def create_kode_barang(payload: KodeBarangCustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id tidak ditemukan")

    item = KodeBarangCustomer(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=KodeBarangCustomerOut)
def update_kode_barang(item_id: int, payload: KodeBarangCustomerUpdate, db: Session = Depends(get_db)):
    item = db.query(KodeBarangCustomer).filter(KodeBarangCustomer.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kode barang customer not found")

    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id tidak ditemukan")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_kode_barang(item_id: int, db: Session = Depends(get_db)):
    item = db.query(KodeBarangCustomer).filter(KodeBarangCustomer.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kode barang customer not found")
    db.delete(item)
    db.commit()

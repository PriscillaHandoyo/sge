from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.services.excel_import import parse_customer_excel

router = APIRouter(prefix="/customers", tags=["Customer"])


@router.post("/import/preview")
def preview_import_customers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parse file Excel, BELUM nyimpen apapun ke database.
    Balikin data yang baru (siap insert langsung) dan data yang
    kode_cust-nya udah ada (perlu keputusan user: update atau skip).
    """
    content = file.file.read()

    try:
        rows = parse_customer_excel(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_rows = []
    duplicate_rows = []

    for row in rows:
        existing = db.query(Customer).filter(Customer.kode_cust == row["kode_cust"]).first()
        if existing:
            duplicate_rows.append({
                "kode_cust": row["kode_cust"],
                "existing": {
                    "nama_cust": existing.nama_cust,
                    "contact_person_1": existing.contact_person_1,
                    "no_telp_1": existing.no_telp_1,
                    "alamat": existing.alamat,
                },
                "incoming": row,
            })
        else:
            new_rows.append(row)

    return {"new": new_rows, "duplicates": duplicate_rows}


@router.post("/import/confirm")
def confirm_import_customers(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Beneran nyimpen ke database. Payload isinya:
    { "new": [...], "updates": [...] }
    'new' selalu di-insert. 'updates' cuma yang user pilih "Update" di frontend
    (yang dipilih "Skip" gak dikirim sama sekali di sini).
    """
    new_rows = payload.get("new", [])
    update_rows = payload.get("updates", [])

    inserted = []
    updated = []

    for row in new_rows:
        db.add(Customer(**row))
        inserted.append(row["kode_cust"])

    for row in update_rows:
        existing = db.query(Customer).filter(Customer.kode_cust == row["kode_cust"]).first()
        if existing:
            for key, value in row.items():
                if key != "kode_cust":
                    setattr(existing, key, value)
            updated.append(row["kode_cust"])

    db.commit()

    return {"inserted": inserted, "updated": updated}


@router.get("/", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="kode_cust sudah dipakai")
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in payload.model_dump().items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()

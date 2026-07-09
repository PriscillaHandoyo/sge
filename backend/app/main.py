from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

app = FastAPI(title="SGE API")

@app.get("/")
def read_root():
    return {"message": "SGE API is running. Go to /docs for documentation."}

from app.routers import user, auth, customer, supplier, jasa, material, kode_barang_customer, bom, barang_jasa, kategori, satuan 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # development aja, nanti di production dipersempit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(supplier.router)
app.include_router(jasa.router)
app.include_router(material.router)
app.include_router(kode_barang_customer.router)
app.include_router(bom.router)
app.include_router(barang_jasa.router)
app.include_router(kategori.router)
app.include_router(satuan.router)

#@app.get("/health")
#def health(db: Session = Depends(get_db)):
#    db.execute(text("SELECT 1"))
#    return {"status": "ok", "db": "connected"}

@app.get("/health")
def health():
    return {"status": "ok"}

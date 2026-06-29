from typing import Optional
from pydantic import BaseModel, ConfigDict


class KodeBarangCustomerBase(BaseModel):
    kode_barang: str
    customer_id: int


class KodeBarangCustomerCreate(KodeBarangCustomerBase):
    pass


class KodeBarangCustomerUpdate(KodeBarangCustomerBase):
    pass


class KodeBarangCustomerOut(KodeBarangCustomerBase):
    id: int
    nama_cust: Optional[str] = None  # read-only, otomatis dari relasi customer

    model_config = ConfigDict(from_attributes=True)

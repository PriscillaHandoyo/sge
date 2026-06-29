from typing import Optional
from pydantic import BaseModel, ConfigDict


class BarangJasaBase(BaseModel):
    kode_barang_customer_id: int
    jasa_id: int
    urutan: Optional[int] = None


class BarangJasaCreate(BarangJasaBase):
    pass


class BarangJasaUpdate(BarangJasaBase):
    pass


class BarangJasaOut(BarangJasaBase):
    id: int
    jenis_pekerjaan: Optional[str] = None
    kode_barang: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

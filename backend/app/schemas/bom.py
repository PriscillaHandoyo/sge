from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class BomBase(BaseModel):
    kode_barang_customer_id: int
    material_id: int
    penggunaan: Decimal


class BomCreate(BomBase):
    pass


class BomUpdate(BomBase):
    pass


class BomOut(BomBase):
    id: int
    nama_material: Optional[str] = None
    satuan_terkecil: Optional[str] = None
    kode_barang: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

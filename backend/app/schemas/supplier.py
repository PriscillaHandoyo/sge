from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field


class TipeSupplier(str, Enum):
    import_ = "import"
    lokal = "lokal"


class SupplierBase(BaseModel):
    kode_sup: str
    nama_sup: str
    tipe: TipeSupplier
    direktur: Optional[str] = None
    contact_person_1: Optional[str] = None
    contact_person_2: Optional[str] = None
    alamat: Optional[str] = None
    no_telp_1: Optional[str] = None
    no_telp_2: Optional[str] = None
    no_hp_1: Optional[str] = None
    no_hp_2: Optional[str] = None
    material_dapat_disupply: Optional[str] = None
    lead_time_delivery: Optional[int] = None
    lead_time_produksi: Optional[int] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int
    kategori: list[str] = []  # read-only, otomatis dari Material — gak dibatasi enum lagi

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def total_lead_time(self) -> Optional[int]:
        if self.lead_time_delivery is None or self.lead_time_produksi is None:
            return None
        return self.lead_time_delivery + self.lead_time_produksi

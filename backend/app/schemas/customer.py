from pydantic import BaseModel, ConfigDict
from typing import Optional


class CustomerBase(BaseModel):
    kode_cust: str
    nama_cust: str
    contact_person_1: Optional[str] = None
    contact_person_2: Optional[str] = None
    alamat: Optional[str] = None
    no_telp_1: Optional[str] = None
    no_telp_2: Optional[str] = None
    no_hp_1: Optional[str] = None
    no_hp_2: Optional[str] = None
    email_1: Optional[str] = None
    email_2: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

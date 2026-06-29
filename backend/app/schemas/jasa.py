from typing import Optional
from pydantic import BaseModel, ConfigDict


class JasaBase(BaseModel):
    jenis_pekerjaan: str
    urutan: Optional[int] = None


class JasaCreate(JasaBase):
    pass


class JasaUpdate(JasaBase):
    pass


class JasaOut(JasaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

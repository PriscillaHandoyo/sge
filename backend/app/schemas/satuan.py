from pydantic import BaseModel, ConfigDict


class SatuanBase(BaseModel):
    nama_satuan: str


class SatuanCreate(SatuanBase):
    pass


class SatuanUpdate(SatuanBase):
    pass


class SatuanOut(SatuanBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict


class KategoriBase(BaseModel):
    nama_kategori: str


class KategoriCreate(KategoriBase):
    pass


class KategoriUpdate(KategoriBase):
    pass


class KategoriOut(KategoriBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

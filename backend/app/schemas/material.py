from pydantic import BaseModel, ConfigDict


class MaterialBase(BaseModel):
    nama_material: str
    supplier_id: int
    satuan_id: int
    kategori_id: int


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    pass


class MaterialOut(MaterialBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

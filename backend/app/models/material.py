from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Material(Base):
    __tablename__ = "material"

    id = Column(Integer, primary_key=True, index=True)
    nama_material = Column(String(255), nullable=False)
    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False)
    satuan_id = Column(Integer, ForeignKey("satuan.id"), nullable=False)
    kategori_id = Column(Integer, ForeignKey("kategori.id"), nullable=False)

    supplier = relationship("Supplier", lazy="joined")
    satuan = relationship("Satuan", lazy="joined")
    kategori_ref = relationship("Kategori", lazy="joined")

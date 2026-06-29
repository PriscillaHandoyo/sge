from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Bom(Base):
    __tablename__ = "bom"

    id = Column(Integer, primary_key=True, index=True)
    kode_barang_customer_id = Column(Integer, ForeignKey("kode_barang_customer.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("material.id"), nullable=False)
    penggunaan = Column(Numeric(10, 3), nullable=False)

    kode_barang_customer = relationship("KodeBarangCustomer", lazy="joined")
    material = relationship("Material", lazy="joined")

    @property
    def nama_material(self):
        return self.material.nama_material if self.material else None

    @property
    def satuan_terkecil(self):
        # Material.satuan_terkecil udah gak ada lagi (sekarang FK ke tabel Satuan),
        # jadi harus lewat relationship material.satuan.nama_satuan
        if self.material and self.material.satuan:
            return self.material.satuan.nama_satuan
        return None

    @property
    def kode_barang(self):
        return self.kode_barang_customer.kode_barang if self.kode_barang_customer else None

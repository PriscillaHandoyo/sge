from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class BarangJasa(Base):
    __tablename__ = "barang_jasa"

    id = Column(Integer, primary_key=True, index=True)
    kode_barang_customer_id = Column(Integer, ForeignKey("kode_barang_customer.id"), nullable=False)
    jasa_id = Column(Integer, ForeignKey("jasa.id"), nullable=False)
    urutan = Column(Integer, nullable=True)

    kode_barang_customer = relationship("KodeBarangCustomer", lazy="joined")
    jasa = relationship("Jasa", lazy="joined")

    @property
    def jenis_pekerjaan(self):
        return self.jasa.jenis_pekerjaan if self.jasa else None

    @property
    def kode_barang(self):
        return self.kode_barang_customer.kode_barang if self.kode_barang_customer else None

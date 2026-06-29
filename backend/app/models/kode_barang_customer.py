from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class KodeBarangCustomer(Base):
    __tablename__ = "kode_barang_customer"

    id = Column(Integer, primary_key=True, index=True)
    kode_barang = Column(String(100), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)

    customer = relationship("Customer", lazy="joined")

    @property
    def nama_cust(self):
        return self.customer.nama_cust if self.customer else None

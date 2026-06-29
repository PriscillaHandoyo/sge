from sqlalchemy import Column, Integer, String, Text

from app.db.session import Base


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    kode_cust = Column(String(50), unique=True, nullable=False, index=True)
    nama_cust = Column(String(255), nullable=False)
    contact_person_1 = Column(String(100), nullable=True)
    contact_person_2 = Column(String(100), nullable=True)
    alamat = Column(Text, nullable=True)
    no_telp_1 = Column(String(100), nullable=True)
    no_telp_2 = Column(String(100), nullable=True)
    no_hp_1 = Column(String(100), nullable=True)
    no_hp_2 = Column(String(100), nullable=True)
    email_1 = Column(String(100), nullable=True)
    email_2 = Column(String(100), nullable=True)

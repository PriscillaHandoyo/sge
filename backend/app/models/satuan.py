from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Satuan(Base):
    __tablename__ = "satuan"

    id = Column(Integer, primary_key=True, index=True)
    nama_satuan = Column(String(20), unique=True, nullable=False)

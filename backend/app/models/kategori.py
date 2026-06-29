from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Kategori(Base):
    __tablename__ = "kategori"

    id = Column(Integer, primary_key=True, index=True)
    nama_kategori = Column(String(50), unique=True, nullable=False)

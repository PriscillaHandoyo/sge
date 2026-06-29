from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Jasa(Base):
    __tablename__ = "jasa"

    id = Column(Integer, primary_key=True, index=True)
    jenis_pekerjaan = Column(String(100), nullable=False, unique=True)
    urutan = Column(Integer, nullable=True)

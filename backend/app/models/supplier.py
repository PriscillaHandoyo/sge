from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import object_session

from app.db.session import Base


class Supplier(Base):
    __tablename__ = "supplier"

    id = Column(Integer, primary_key=True, index=True)
    kode_sup = Column(String(50), unique=True, nullable=False, index=True)
    nama_sup = Column(String(255), nullable=False)
    tipe = Column(String(10), nullable=False)  # 'import' / 'lokal', divalidasi di schema
    direktur = Column(String(100), nullable=True)
    contact_person_1 = Column(String(100), nullable=True)
    contact_person_2 = Column(String(100), nullable=True)
    alamat = Column(Text, nullable=True)
    no_telp_1 = Column(String(100), nullable=True)
    no_telp_2 = Column(String(100), nullable=True)
    no_hp_1 = Column(String(100), nullable=True)
    no_hp_2 = Column(String(100), nullable=True)
    material_dapat_disupply = Column(Text, nullable=True)
    lead_time_delivery = Column(Integer, nullable=True)  # dalam hari
    lead_time_produksi = Column(Integer, nullable=True)  # dalam hari

    @property
    def kategori(self):
        """
        Kategori supplier ini otomatis dihitung dari kategori Material-material
        yang punya supplier_id ini. Sekarang kategori Material sendiri adalah
        FK ke tabel Kategori (bukan string bebas lagi), jadi join lewat itu.
        """
        from app.models.material import Material  # import lokal, hindari circular import
        from app.models.kategori import Kategori

        session = object_session(self)
        if session is None:
            return []

        rows = (
            session.query(Kategori.nama_kategori)
            .join(Material, Material.kategori_id == Kategori.id)
            .filter(Material.supplier_id == self.id)
            .distinct()
            .all()
        )
        return [r[0] for r in rows]

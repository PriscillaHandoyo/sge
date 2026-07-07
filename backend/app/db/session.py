from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# JANGAN impor settings dari app.core.config lagi
# Ambil langsung dari environment variable yang disediakan Docker
db_url = os.getenv("DATABASE_URL", "postgresql://sge:sge@postgres:5432/sge")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

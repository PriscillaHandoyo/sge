import bcrypt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://sge:sge@sge-postgres:5432/sge"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String) # Sesuaikan dengan nama kolom!
    role = Column(String)          # Wajib diisi karena Nullable = not null

def create_user(username, password, role="admin"):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    db = SessionLocal()
    # Gunakan nama kolom yang tepat: password_hash
    new_user = User(
        username=username, 
        password_hash=hashed.decode('utf-8'),
        role=role
    )
    
    try:
        db.add(new_user)
        db.commit()
        print(f"User '{username}' dengan role '{role}' berhasil dibuat!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_user("admin", "admin123", "admin")

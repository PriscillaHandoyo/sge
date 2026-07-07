from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import sys
import os

# Menambahkan path agar bisa mengimpor model
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --- FORCE DATABASE URL CONFIGURATION ---
# Kita ambil langsung dari environment variable sistem (Docker)
# Ini memotong ketergantungan pada file settings.py
db_url = os.environ.get("DATABASE_URL", "postgresql://sge:sge@postgres:5432/sge")

# Akses objek konfigurasi Alembic
config = context.config
config.set_main_option('sqlalchemy.url', db_url)

# Setup Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Impor Base dan Model agar Alembic bisa mendeteksi perubahan tabel
from app.db.session import Base
from app.models import customer, supplier, jasa, material, kode_barang_customer, bom, barang_jasa, user, kategori, satuan

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Membuat engine langsung tanpa mengandalkan settings.py
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

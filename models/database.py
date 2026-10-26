import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(override=True)

password_cleaned = quote_plus(os.getenv("DATABASE_PASS", ""))
database_user = os.getenv("DATABASE_USER", "")
database_ip = os.getenv("DATABASE_IP", "")
database_port = os.getenv("PORT", "3306")
selected_db = os.getenv("SELECTED_DB", "")

database_url = (
    f"mysql+pymysql://{database_user}:{password_cleaned}"
    f"@{database_ip}:{database_port}/{selected_db}"
)

engine = create_engine(
    database_url,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=1800,
)

session_maker = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session():
    """FastAPI dependency that yields a database session and safely closes it."""
    session = session_maker()
    try:
        yield session
    finally:
        session.close()

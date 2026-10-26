"""Convenience alias for models.database."""
from models.database import engine, session_maker, get_db_session

__all__ = ["engine", "session_maker", "get_db_session"]

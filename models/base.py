"""
Database Base Configuration
===========================

SQLAlchemy engine, session, and base class setup.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    scoped_session,
)
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    """Base class for all models with common fields."""
    
    # Common timestamp columns for all models
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DatabaseManager:
    """
    Database connection manager.
    
    Usage:
        db = DatabaseManager()
        db.init_app('sqlite:///jiyo100saal.db')
        
        with db.session() as session:
            patient = Patient(...)
            session.add(patient)
            session.commit()
    """
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self._scoped_session = None
    
    def init_app(self, database_url: str, echo: bool = False):
        """
        Initialize database connection.
        
        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite:///jiyo100saal.db')
            echo: If True, log all SQL statements
        """
        self.engine = create_engine(
            database_url,
            echo=echo,
            # SQLite-specific: enable foreign key support
            connect_args={"check_same_thread": False} if 'sqlite' in database_url else {},
        )
        
        # Enable foreign keys for SQLite
        if 'sqlite' in database_url:
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        self.Session = sessionmaker(bind=self.engine)
        self._scoped_session = scoped_session(self.Session)
    
    def create_all(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
    
    def drop_all(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(self.engine)
    
    def session(self):
        """Get a new database session."""
        if self.Session is None:
            raise RuntimeError("Database not initialized. Call init_app() first.")
        return self.Session()
    
    @property
    def scoped_session(self):
        """Get the scoped session for thread-safe access."""
        if self._scoped_session is None:
            raise RuntimeError("Database not initialized. Call init_app() first.")
        return self._scoped_session


# Global database manager instance
db = DatabaseManager()

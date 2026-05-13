import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL de connexion PostgreSQL (à configurer via variables d'environnement)
# Format: postgresql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./profoot.db" # Fallback SQLite pour le développement local si pas de Docker
)

# Configuration de l'engine SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance pour récupérer la session de base de données dans FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

load_dotenv()

# Récupérer les variables d'environnement
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_NAME = os.getenv('POSTGRES_DATABASE')

# Construire l'URL de connexion
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require"

# Configuration de l'engine avec SSL
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require"
    },
    pool_size=5,  # Nombre de connexions dans le pool
    max_overflow=10  # Nombre maximum de connexions supplémentaires
)

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    phone = Column(String, unique=True)
    password = Column(String)
    is_phone_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(name='{self.name}', phone='{self.phone}')>"

# Créer les tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de données initialisée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
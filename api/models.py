from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Récupérer l'URL de la base de données
DATABASE_URL = os.getenv('DATABASE_URL')

# Configuration de l'engine avec SSL
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require"
    }
)

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    emailVerified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
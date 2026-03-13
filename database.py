from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./compartiendo_espacio.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, index=True)
    rut = Column(String, unique=True, index=True)
    correo = Column(String, unique=True, index=True)
    password = Column(String)
    patente = Column(String) # Nuevo campo
    rol = Column(String)     # Nuevo campo: 'cliente' o 'arrendador'

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
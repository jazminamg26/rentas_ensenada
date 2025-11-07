from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

# URL de conexión a tu base de datos PostgreSQL
DATABASE_URL = "postgresql://postgres:Hey!Jaz26:)@localhost:5432/rentasInmuebles_ensenada"

# Crear engine
engine = create_engine(DATABASE_URL, echo=True)

# Función para obtener sesión (lo que necesita FastAPI)
def get_session():
    with Session(engine) as session:
        yield session

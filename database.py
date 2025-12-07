from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

# URL de conexión a tu base de datos PostgreSQL
DATABASE_URL = "postgresql://postgres:Hey!Jaz26:)@localhost:5432/rentasInmuebles_ensenada"

# Crear engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """
    Importa todos los modelos y crea las tablas en la base de datos.
    """
    # ¡IMPORTANTE! 
    # Importa todos tus modelos aquí para que SQLModel los "vea"
    # y sepa qué tablas crear.
    
    # Asumiendo que están en 'models.py'
    from models import User, Arrendatario, Renta, HistorialRenta
    from models import CatalogoMuebles, CatalogoServicios, RentaMuebles, RentaServicios
    
    # Esta línea mágica crea todas las tablas
    SQLModel.metadata.create_all(engine)


# Función para obtener sesión (lo que necesita FastAPI)
def get_session():
    with Session(engine) as session:
        yield session

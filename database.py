
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

# URL de conexión a tu base de datos PostgreSQL
DATABASE_URL = "postgresql://u9rs9sungo2t0n:pa7301c3c9f9d74603a6c5ba2f625c7efab8cffc11e68556524e8ccfa4fed96d1@c57oa7dm3pc281.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dfgh778g67sqa6"

# Crear engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """
    Importa todos los modelos y crea las tablas en la base de datos.
    """
    
    from models import User, Arrendatario, Renta, HistorialRenta
    from models import CatalogoMuebles, CatalogoServicios, RentaMuebles, RentaServicios
    
    # Esta línea mágica crea todas las tablas
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

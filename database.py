
# from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy.orm import sessionmaker

# # URL de conexión a tu base de datos PostgreSQL
# DATABASE_URL = "postgresql://u9rs9sungo2t0n:pa7301"

# # Crear engine
# engine = create_engine(DATABASE_URL, echo=True)


# def create_db_and_tables():
#     """
#     Importa todos los modelos y crea las tablas en la base de datos.
#     """
    
#     from models import User, Arrendatario, Renta, HistorialRenta
#     from models import CatalogoMuebles, CatalogoServicios, RentaMuebles, RentaServicios
    
#     # Esta línea mágica crea todas las tablas
#     SQLModel.metadata.create_all(engine)


# def get_session():
#     with Session(engine) as session:
#         yield session


from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy.orm import sessionmaker # Esta línea ya no es necesaria si usas SQLModel.Session

# 🛠️ CAMBIO CLAVE AQUÍ: Usar tu PostgreSQL local
# Reemplaza 'usuario_local', 'contraseña_local' y 'nombre_db_local'
# con tus credenciales de PostgreSQL en tu máquina.
DATABASE_URL = "postgresql://usuario_local:Hey!Jaz26:)@localhost:5432/rentasInmuebles_ensenada"

# Si estás usando el usuario por defecto de Postgre, a veces la contraseña puede estar vacía:
# DATABASE_URL = "postgresql://postgres:@localhost:5432/nombre_db_local" 
# Nota: La sintaxis de Postgre es: dialecto://usuario:contraseña@host:puerto/nombre_base_datos

# Crear engine
# Ya no es necesario el 'connect_args' que se usaba para SQLite.
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
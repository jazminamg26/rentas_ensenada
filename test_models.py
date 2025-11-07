from sqlmodel import SQLModel, create_engine
from models import Arrendatario, Renta, HistorialRenta, CatalogoMuebles, RentaMuebles, CatalogoServicios, RentaServicios

# Base de datos de prueba (SQLite en memoria)
engine_test = create_engine("sqlite:///:memory:", echo=True)

# Crear todas las tablas en memoria
SQLModel.metadata.create_all(engine_test)

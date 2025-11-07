# models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone
# ----------------------------
# Arrendatario
# ----------------------------
class Arrendatario(SQLModel, table=True):
    __tablename__ = "arrendatario"
    id: int = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    correo: Optional[str] = None
    activo: bool = True

# ----------------------------
# Catalogo de muebles
# ----------------------------
class CatalogoMuebles(SQLModel, table=True):
    __tablename__ = "catalogo_muebles"
    id: int = Field(default=None, primary_key=True)
    mueble: str

# ----------------------------
# Catalogo de servicios
# ----------------------------
class CatalogoServicios(SQLModel, table=True):
    __tablename__ = "catalogo_servicios"
    id: int = Field(default=None, primary_key=True)
    servicio: str

# ----------------------------
# Renta
# ----------------------------
class Renta(SQLModel, table=True):
    __tablename__ = "renta"
    id: Optional[int] = Field(default=None, primary_key=True)
    edificio: str
    habitaciones: int
    banos: float
    lat: float
    lon: float
    mascotas: bool
    tinaco: bool
    estacionamiento: int
    activo: bool
    disponible: bool
    precio: int
    arrendatario_id: int = Field(foreign_key="arrendatario.id")

# ----------------------------
# Historial de renta
# ----------------------------
class HistorialRenta(SQLModel, table=True):
    __tablename__ = "historial_renta"
    id: Optional[int] = Field(default=None, primary_key=True)
    renta_id: int = Field(foreign_key="renta.id")
    fecha_inicio: date
    fecha_fin: date
    precio: int
# ----------------------------
# Renta Muebles
# ----------------------------
class RentaMuebles(SQLModel, table=True):
    __tablename__ = "renta_muebles"
    id: int = Field(default=None, primary_key=True)
    renta_id: int = Field(foreign_key="renta.id")
    mueble_id: int = Field(foreign_key="catalogo_muebles.id")

# ----------------------------
# Renta Servicios
# ----------------------------
class RentaServicios(SQLModel, table=True):
    __tablename__ = "renta_servicios"
    id: int = Field(default=None, primary_key=True)
    renta_id: int = Field(foreign_key="renta.id")
    servicio_id: int = Field(foreign_key="catalogo_servicios.id")

# ----------------------------
class User(SQLModel, table=True):
    """
    User model. 'role' can be 'regular', 'owner', or 'super_user'.
    If 'owner', 'owned_house_id' links to their ExchangeHouse.
    """
    _tablename_ = "users"
    id: int = Field(primary_key=True, index=True)
    user_name: str = Field(unique=True, index=True)
    password: str 
    role: str = Field(default="regular")
    active: bool = Field(default=True)
# models.py
from typing import Optional
# models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship  # <-- ¡Asegúrate de que sea 'Relationship'!
from datetime import date
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker, Session, relationship, DeclarativeBase, Mapped, mapped_column

# ----------------------------
# User
# ----------------------------
class User(SQLModel, table=True):
    """
    Almacena las credenciales de inicio de sesión.
    Los roles pueden ser 'super_user' o 'arrendatario'.
    """
    _tablename_ = "user"  # Nueva tabla
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    password: str
    role: str = Field(max_length=20) # 'super_user' o 'arrendatario'
    active: bool = Field(default=True)
    
    # Relación Uno-a-Uno con Arrendatario
    # Un usuario puede ser un arrendatario
    arrendatario: Optional["Arrendatario"] = Relationship(back_populates="user")

# ----------------------------
# Arrendatario
# ----------------------------
class Arrendatario(SQLModel, table=True): # Renombrado de 'User' a 'Arrendatario'
    """
    Almacena la información de contacto del propietario (landlord).
    """
    _tablename_ = "arrendatario"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    correo: Optional[str] = None
    activo: bool = True # Este 'activo' es para lógica de negocio

    # Clave foránea para vincular al modelo User
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="user.id", 
        unique=True,  # Un usuario solo puede ser un arrendatario
        index=True
    )
    
    # Relación de vuelta al User
    user: Optional[User] = Relationship(back_populates="arrendatario")

    # Relación Uno-a-Muchos con Renta
    # Un arrendatario puede tener muchas rentas
    rentas: List["Renta"] = Relationship(back_populates="arrendatario_rel")

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
    _tablename_ = "renta"
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
    
    # La clave foránea sigue apuntando a 'arrendatario.id'
    arrendatario_id: int = Field(foreign_key="arrendatario.id")
    
    # Relación de vuelta al Arrendatario
    arrendatario_rel: Optional[Arrendatario] = Relationship(back_populates="rentas")

# ----------------------------
# Historial de renta
# ----------------------------
class HistorialRenta(SQLModel, table=True):
    _tablename_ = "historial_renta"
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

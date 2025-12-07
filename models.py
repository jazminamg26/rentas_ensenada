# models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import relationship, Mapped, mapped_column

# --- User (AJUSTADO: password renombrado y campo active) ---
class User(SQLModel, table=True):
    """
    Almacena las credenciales de inicio de sesión.
    Los roles pueden ser 'super_user' o 'arrendatario'.
    """
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    # Renombrado de 'password' a 'hashed_password' para mayor claridad
    hashed_password: str 
    role: str = Field(max_length=20) # 'super_user' o 'arrendatario'
    # is_active es el nombre común en librerías de auth, lo usamos aquí.
    is_active: bool = Field(default=True, alias="active") 
    
    # Relación Uno-a-Uno con Arrendatario
    arrendatario: Optional["Arrendatario"] = Relationship(back_populates="user_rel")


# --- Arrendatario (AJUSTADO: back_populates a 'user_rel') ---
class Arrendatario(SQLModel, table=True):
    """
    Almacena la información de contacto del propietario (landlord).
    """
    __tablename__ = "arrendatario"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    correo: Optional[str] = None
    activo: bool = True # Este 'activo' es para lógica de negocio

    # Clave foránea para vincular al modelo User
    user_id: Optional[int] = Field(
        default=None, 
        foreign_key="user.id", 
        unique=True, 
        index=True
    )
    
    # Relación de vuelta al User (Cambiado a user_rel para claridad)
    user_rel: Optional[User] = Relationship(back_populates="arrendatario")

    # Relación Uno-a-Muchos con Renta
    rentas: List["Renta"] = Relationship(back_populates="arrendatario_rel")

# ----------------------------
# Catalogo de muebles (AJUSTADO: Relaciones M:M)
# ----------------------------
class CatalogoMuebles(SQLModel, table=True):
    __tablename__ = "catalogo_muebles"
    id: Optional[int] = Field(default=None, primary_key=True)
    mueble: str # Nombre real del campo en la DB
    
    renta_muebles: List["RentaMuebles"] = Relationship(back_populates="mueble_rel")

# ----------------------------
# Catalogo de servicios (AJUSTADO: Relaciones M:M)
# ----------------------------
class CatalogoServicios(SQLModel, table=True):
    __tablename__ = "catalogo_servicios"
    id: Optional[int] = Field(default=None, primary_key=True)
    servicio: str # Nombre real del campo en la DB
    
    renta_servicios: List["RentaServicios"] = Relationship(back_populates="servicio_rel")

# ----------------------------
# Renta Muebles (Tabla de Enlace M:M)
# ----------------------------
class RentaMuebles(SQLModel, table=True):
    __tablename__ = "renta_muebles"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    renta_id: int = Field(foreign_key="renta.id", index=True)
    mueble_id: int = Field(foreign_key="catalogo_muebles.id", index=True)
    
    renta_rel: Optional["Renta"] = Relationship(back_populates="muebles_link")
    mueble_rel: Optional[CatalogoMuebles] = Relationship(back_populates="renta_muebles")

# ----------------------------
# Renta Servicios (Tabla de Enlace M:M)
# ----------------------------
class RentaServicios(SQLModel, table=True):
    __tablename__ = "renta_servicios"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    renta_id: int = Field(foreign_key="renta.id", index=True)
    servicio_id: int = Field(foreign_key="catalogo_servicios.id", index=True)
    
    renta_rel: Optional["Renta"] = Relationship(back_populates="servicios_link")
    servicio_rel: Optional[CatalogoServicios] = Relationship(back_populates="renta_servicios")


# ----------------------------
# Renta (AJUSTADO: Relaciones M:M y Historial)
# ----------------------------
class Renta(SQLModel, table=True):
    __tablename__ = "renta" # Corregido a __tablename__
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
    
    # Relación Uno-a-Muchos con Arrendatario
    arrendatario_id: int = Field(foreign_key="arrendatario.id")
    arrendatario_rel: Optional[Arrendatario] = Relationship(back_populates="rentas")
    
    # Relaciones Muchos-a-Muchos para acceso directo
    muebles: List[CatalogoMuebles] = Relationship(link_model=RentaMuebles)
    servicios: List[CatalogoServicios] = Relationship(link_model=RentaServicios)
    
    # Relaciones Muchos-a-Muchos para acceso al enlace (si se necesita)
    muebles_link: List[RentaMuebles] = Relationship(back_populates="renta_rel")
    servicios_link: List[RentaServicios] = Relationship(back_populates="renta_rel")

    # Relación Uno-a-Muchos con HistorialRenta
    historial: List["HistorialRenta"] = Relationship(back_populates="renta_rel")


# ----------------------------
# Historial de renta (AJUSTADO: back_populates)
# ----------------------------
class HistorialRenta(SQLModel, table=True):
    __tablename__ = "historial_renta"
    id: Optional[int] = Field(default=None, primary_key=True)
    renta_id: int = Field(foreign_key="renta.id")
    fecha_inicio: date
    fecha_fin: date
    precio: int # Asegurar que es INTEGER como en tu DB original
    
    # Relación de vuelta a Renta
    renta_rel: Optional[Renta] = Relationship(back_populates="historial")
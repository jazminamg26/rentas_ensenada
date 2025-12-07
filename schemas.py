# schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime, timedelta, timezone

# --- Catálogo y M:M (NUEVOS) ---

class CatalogoBase(BaseModel):
    # Usado para crear o listar ítems de catálogo (muebles/servicios)
    id: Optional[int] = None
    # El nombre que se usará para la entrada (ej. "Internet")
    nombre: str 
    
    model_config = ConfigDict(from_attributes=True) 

class RentaMuebleCreate(BaseModel):
    mueble_id: int

class RentaServicioCreate(BaseModel):
    servicio_id: int

# ----------------------------

# --- Rentas ---

class RentaCreate(BaseModel):
    # ¡arrendatario_id se elimina para inferir del token!
    edificio: str
    habitaciones: int
    banos: float
    lat: float
    lon: float
    mascotas: bool
    tinaco: bool
    estacionamiento: int
    activo: bool = True
    disponible: bool = True
    precio: int # Asegurar que es int
    
    # Este campo estaba duplicado al final del archivo, se consolidó aquí.


class RentaInmueble(BaseModel):
    id: int
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
    arrendatario_id: int

    model_config = ConfigDict(from_attributes=True)


class RentaUpdate(BaseModel):
    edificio: Optional[str] = None
    habitaciones: Optional[int] = None
    banos: Optional[float] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    mascotas: Optional[bool] = None
    tinaco: Optional[bool] = None
    estacionamiento: Optional[int] = None
    activo: Optional[bool] = None
    disponible: Optional[bool] = None
    precio: Optional[int] = None # Asegurar que es int
    # arrendatario_id: Optional[int] = None # Se recomienda no actualizar por este medio


# --- Arrendatarios ---

class ArrendatarioInfo(BaseModel):
    nombre: str
    telefono: str
    correo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ArrendatarioCreate(BaseModel):
    nombre: str
    telefono: str
    correo: str
    activo: bool

class ArrendatarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    activo: Optional[bool] = None

class ArrendatarioConUserCreate(BaseModel):
    # UserCreate ya está definido abajo, se asume que es correcto.
    # No lo repito aquí para no duplicar el código.
    user_data: 'UserCreate'
    arrendatario_data: ArrendatarioCreate
    
# --- Renta Detalle (AJUSTADO: Incluye Muebles y Servicios) ---

class RentaDetalle(RentaInmueble):
    arrendatario: ArrendatarioInfo
    muebles: List[CatalogoBase] # Nuevo
    servicios: List[CatalogoBase] # Nuevo
    link_historial: str
    
    model_config = ConfigDict(from_attributes=True)


# --- Historial de Renta ---

class HistorialRentaResponse(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    precio: int # Asegurar que es int

    model_config = ConfigDict(from_attributes=True)


class HistorialRentaCreate(BaseModel):
    renta_id: int
    fecha_inicio: date
    fecha_fin: date
    precio: int # Cambiado de float a int


class HistorialRentaUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    precio: Optional[int] = None # Cambiado de float a int


# --- User & Auth ---
class UserBase(BaseModel):
    username: str
    role: str
    active : bool 

class UserSchema(UserBase):
    id: int

class UserCreate(BaseModel):
    username: str
    password: str 
    role: str # Aunque forzamos 'arrendatario', se mantiene para la estructura.


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
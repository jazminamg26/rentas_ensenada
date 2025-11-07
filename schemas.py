from typing import Optional
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional

class RentaCreate(BaseModel):
    edificio: str
    habitaciones: int
    banos: int
    lat: float
    lon: float
    mascotas: bool
    tinaco: bool
    estacionamiento: int
    activo: bool
    disponible: bool
    precio: int
    arrendatario_id: int


class RentaInmueble(BaseModel):
    id: int
    edificio: str
    habitaciones: int
    banos: int
    lat: float
    lon: float
    mascotas: bool
    tinaco: bool
    estacionamiento: int
    activo: bool
    disponible: bool
    precio: int
    arrendatario_id: int

    class Config:
        from_attributes = True


class ArrendatarioInfo(BaseModel):
    nombre: str
    telefono: str
    correo: Optional[str] = None

    class Config:
        from_attributes = True


class RentaDetalle(RentaInmueble):
    arrendatario: ArrendatarioInfo
    link_historial: str

from typing import Optional
from pydantic import BaseModel

class RentaUpdate(BaseModel):
    edificio: Optional[str] = None
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    mascotas: Optional[bool] = None
    tinaco: Optional[bool] = None
    estacionamiento: Optional[int] = None
    activo: Optional[bool] = None
    disponible: Optional[bool] = None
    precio: Optional[int] = None
    arrendatario_id: Optional[int] = None

from datetime import date

class HistorialRentaResponse(BaseModel):
    id: int
    renta_id: int
    fecha_inicio: date
    fecha_fin: date
    precio: int

    class Config:
        from_attributes = True

from pydantic import BaseModel
from datetime import date

class HistorialRentaCreate(BaseModel):
    renta_id: int
    fecha_inicio: date
    fecha_fin: date
    precio: float


from typing import Optional
from datetime import date
from pydantic import BaseModel

class HistorialRentaUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    precio: Optional[float] = None


from pydantic import BaseModel
from typing import Optional

class ArrendatarioCreate(BaseModel):
    nombre: str
    telefono: str
    correo: str
    activo: bool

from pydantic import BaseModel
from typing import Optional

class ArrendatarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    activo: Optional[bool] = None
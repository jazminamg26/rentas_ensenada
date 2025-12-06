from typing import Optional
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional
<<<<<<< HEAD
<<<<<<< HEAD
from datetime import date
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone
=======
>>>>>>> parent of 5564bcd (terminado)
=======
>>>>>>> parent of 5564bcd (terminado)

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

class ArrendatarioBase(BaseModel):
    nombre: str
    telefono: str
    correo: Optional[str] = None
    activo: bool = True

class ArrendatarioCreate(ArrendatarioBase):
    pass

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

<<<<<<< HEAD
<<<<<<< HEAD
=======
from pydantic import BaseModel
from typing import Optional
>>>>>>> parent of 5564bcd (terminado)
=======
from pydantic import BaseModel
from typing import Optional
>>>>>>> parent of 5564bcd (terminado)

class ArrendatarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    activo: Optional[bool] = None

# Adicional para permisos 
class UserBase(BaseModel):
    username: str
    role: str
    active : bool 

class UserSchema(UserBase):
    id: int
   

class UserCreate(BaseModel):
    username: str
    password: str 
    #role: str 


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class ArrendatarioConUserCreate(BaseModel):
    user_data: UserCreate
    arrendatario_data: ArrendatarioCreate


class RentaCreate(BaseModel):
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
    precio: int
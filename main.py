from fastapi import FastAPI, HTTPException, Depends, Path
from typing import List, Optional
from sqlmodel import Session, select
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, Query, status
from typing import List, Optional, Annotated


# Importar tus módulos locales
from database import get_session
from models import User, Renta, Arrendatario, HistorialRenta
from schemas import (
    RentaCreate,
    RentaInmueble,
    RentaDetalle,
    ArrendatarioInfo,
    RentaUpdate,
    HistorialRentaResponse,
    HistorialRentaCreate,
    HistorialRentaUpdate,
    ArrendatarioCreate,
    ArrendatarioUpdate
)

from schemas import (
    UserBase,
    UserCreate,
    UserSchema,
    UserUpdate,
    Token,
    TokenData
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
# We are using the bcrypt library directly to avoid passlib dependency issues.

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one using bcrypt."""
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

def get_password_hash(password: str) -> str:
    """Hashes a plain password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # Decode to string to store in the database
    return hashed_bytes.decode('utf-8')

# --- JWT Token Creation ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- User Authentication Function ---
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Finds a user in the DB and verifies their password."""
    user = db.scalars(select(User).where(User.username == username)).first()
    
    # Check for user existence AND active status
    if not user or not user.is_active: # <-- MODIFIED
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    return user


# --- 6. Authentication Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Exception for credential errors
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    """
    Dependency to get the current user from a JWT token.
    Validates token, finds user in DB.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = session.scalars(select(User).where(User.username == token_data.username)).first()
    
    # Check for user existence AND active status
    if user is None or not user.is_active: # <-- MODIFIED
        raise credentials_exception
    return user

# Base dependency for any logged-in user
CurrentUser = Annotated[User, Depends(get_current_user)]

# --- Role-Based Dependencies ---
def get_current_regular_user(current_user: CurrentUser) -> User:
    """
    Ensures the user has at least 'regular' privileges.
    (All logged-in users are at least 'regular').
    """
    return current_user

def get_current_owner(current_user: CurrentUser) -> User:
    """Ensures the user is an 'owner'."""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action. Owner role required."
        )
    return current_user

def get_current_super_user(current_user: CurrentUser) -> User:
    """Ensures the user is a 'super_user'."""
    if current_user.role != "super_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action. Super User role required."
        )
    return current_user

# Type aliases for endpoint security
RegularUser = Annotated[User, Depends(get_current_regular_user)]
OwnerUser = Annotated[User, Depends(get_current_owner)]
SuperUser = Annotated[User, Depends(get_current_super_user)]

app = FastAPI()


# -------------------------------------------------------
# 1️⃣ POST /rentas — Crear renta
# -------------------------------------------------------

@app.post("/rentas_inmuebles", tags=["Arrendatario"])
def crear_renta(renta: RentaCreate, session: Session = Depends(get_session)):
    arrendatario = session.get(Arrendatario, renta.arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    # ✅ Validar número de baños
    num_banos = renta.banos
    parte_decimal = num_banos % 1  # obtiene la parte decimal

    if parte_decimal not in (0, 0.5):
        raise HTTPException(
            status_code=400,
            detail="Sólo se aceptan medios baños o baños enteros (por ejemplo 1, 1.5, 2, 2.5, etc.)."
        )

    nueva_renta = Renta(**renta.dict())
    session.add(nueva_renta)
    session.commit()
    session.refresh(nueva_renta)

    return {
        "mensaje": "La renta del inmueble se publicó existosamente",
        "renta_id": nueva_renta.id
    }


# -------------------------------------------------------
# 2️⃣ GET /rentas_inmuebles — Obtener rentas con filtros
# -------------------------------------------------------
@app.get("/rentas_inmuebles", response_model=List[RentaInmueble])
def obtener_rentas_inmuebles(
    habitaciones: Optional[int] = None,
    banos: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    mascotas: Optional[bool] = None,
    tinaco: Optional[bool] = None,
    estacionamiento: Optional[int] = None,
    activo: Optional[bool] = None,
    disponible: Optional[bool] = None,
    precio: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(Renta)

    if habitaciones is not None:
        query = query.where(Renta.habitaciones >= habitaciones)
    if banos is not None:
        query = query.where(Renta.banos >= banos)
    if lat is not None:
        query = query.where(Renta.lat == lat)
    if lon is not None:
        query = query.where(Renta.lon == lon)
    if mascotas is not None:
        query = query.where(Renta.mascotas == mascotas)
    if tinaco is not None:
        query = query.where(Renta.tinaco == tinaco)
    if estacionamiento is not None:
        query = query.where(Renta.estacionamiento == estacionamiento)
    if activo is not None:
        query = query.where(Renta.activo == activo)
    if disponible is not None:
        query = query.where(Renta.disponible == disponible)
    if precio is not None:
        query = query.where(Renta.precio <= precio)

    return session.exec(query).all()


# -------------------------------------------------------
# 3️⃣ GET /rentas_inmuebles/{id} — Detalle con arrendatario
# -------------------------------------------------------
@app.get("/rentas_inmuebles/{id}", response_model=RentaDetalle)
def obtener_renta_detalle(
    id: int = Path(..., description="ID de la renta"),
    session: Session = Depends(get_session)
):
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    arrendatario = session.get(Arrendatario, renta.arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    arrendatario_info = ArrendatarioInfo(
        nombre=arrendatario.nombre,
        telefono=arrendatario.telefono,
        correo=arrendatario.correo
    )

    return RentaDetalle(
        **renta.__dict__,
        arrendatario=arrendatario_info,
        link_historial=f"/historial_renta/{renta.id}"
    )


# -------------------------------------------------------
# 4️⃣ PATCH /rentas/{id} — Actualizar parcialmente una renta
# -------------------------------------------------------
@app.patch("/rentas_inmuebles/{id}", tags=["Arrendatario"])
def actualizar_renta(id: int, datos: RentaUpdate, session: Session = Depends(get_session)):
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(renta, key, value)

    session.add(renta)
    session.commit()
    session.refresh(renta)

    return {"mensaje": "El inmueble fue actualizado correctamente", "renta_actualizada": renta}


# -------------------------------------------------------
# 5️⃣ GET /historial_renta/{renta_id} — Obtener historial
# -------------------------------------------------------
@app.get("/historial_renta/{renta_id}", response_model=List[HistorialRentaResponse])
def obtener_historial_renta(renta_id: int, session: Session = Depends(get_session)):
    renta = session.get(Renta, renta_id)
    if not renta:
        raise HTTPException(status_code=404, detail="No se encontró el inmueble")

    query = select(HistorialRenta).where(HistorialRenta.renta_id == renta_id)
    return session.exec(query).all()


# -------------------------------------------------------
# 6️⃣ POST /historial_renta — Crear nuevo historial
# -------------------------------------------------------
@app.post("/historial_renta", tags=["Arrendatario"])
def crear_historial_renta(historial: HistorialRentaCreate, session: Session = Depends(get_session)):
    renta = session.get(Renta, historial.renta_id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    nuevo_historial = HistorialRenta(**historial.dict())
    session.add(nuevo_historial)
    session.commit()
    session.refresh(nuevo_historial)

    return {"mensaje": "Historial agregado exitosamente"}


# -------------------------------------------------------
# 7️⃣ PATCH /historial_renta/{id} — Actualizar historial
# -------------------------------------------------------
@app.patch("/historial_renta/{id}")
def actualizar_historial_renta(
    id: int,
    datos: HistorialRentaUpdate,
    session: Session = Depends(get_session)
):
    historial = session.get(HistorialRenta, id)
    if not historial:
        raise HTTPException(status_code=404, detail="Registro de historial no encontrado")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(historial, key, value)

    session.add(historial)
    session.commit()
    session.refresh(historial)

    return {"mensaje": "Modificación exitosa"}


# -------------------------------------------------------
# 8️⃣ POST /arrendatario — Crear arrendatario
# -------------------------------------------------------
@app.post("/arrendatario")
def crear_arrendatario(arrendatario: ArrendatarioCreate, session: Session = Depends(get_session)):
    nuevo_arrendatario = Arrendatario(**arrendatario.dict())
    session.add(nuevo_arrendatario)
    session.commit()
    session.refresh(nuevo_arrendatario)

    return {"mensaje": "Arrendatario publicado exitosamente", "arrendatario_id": nuevo_arrendatario.id}


# -------------------------------------------------------
# 9️⃣ PATCH /arrendatario/{id} — Actualizar arrendatario
# -------------------------------------------------------
@app.patch("/arrendatario/{arrendatario_id}")
def actualizar_arrendatario(
    arrendatario_id: int,
    datos: ArrendatarioUpdate,
    session: Session = Depends(get_session)
):
    arrendatario = session.get(Arrendatario, arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(arrendatario, key, value)

    session.add(arrendatario)
    session.commit()
    session.refresh(arrendatario)

    return {"mensaje": "Modificación exitosa"}


# -------------------------------------------------------

@app.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    """
    Log in to get a JWT token.
    
    Username and password are sent in form data (x-www-form-urlencoded).
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
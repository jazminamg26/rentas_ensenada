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
from database import create_db_and_tables, get_session, engine
from typing import Dict, Any
# Importar tus módulos locales
from models import Arrendatario, User, Renta, HistorialRenta
from schemas import (
    RentaCreate,
    RentaInmueble,
    RentaDetalle,
    ArrendatarioInfo,
    RentaUpdate,
    HistorialRentaResponse,
    HistorialRentaCreate,
    HistorialRentaUpdate,
    ArrendatarioUpdate
)

from schemas import (
    Token,
    TokenData
)

from schemas import ArrendatarioConUserCreate

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
    if not user or not user.active: # <-- MODIFIED
        return None
    
    if not verify_password(password, user.password):
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
    if user is None or not user.active: # <-- MODIFIED
        raise credentials_exception
    return user

# Base dependency for any logged-in user
CurrentUser = Annotated[User, Depends(get_current_user)]

# --- Role-Based Dependencies ---
def get_current_arrendatario(current_user: CurrentUser) -> User:
    """Asegura que el usuario es un 'arrendatario'."""
    if current_user.role != "arrendatario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de Arrendatario."
        )
    return current_user

def get_current_super_user(current_user: CurrentUser) -> User:
    """Asegura que el usuario es un 'super_user'."""
    if current_user.role != "super_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de Super Usuario."
        )
    return current_user

# Type aliases for endpoint security
ArrendatarioUser = Annotated[User, Depends(get_current_arrendatario)]
SuperUser = Annotated[User, Depends(get_current_super_user)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables() 
    crear_super_usuario_inicial()


def crear_super_usuario_inicial():
    """Crea un superusuario por defecto si no existe."""
    with Session(engine) as session:
        # Cambia estos valores si quieres personalizar el superusuario
        username = "admin"
        password = "admin123"
        role = "super_user"

        # Verifica si ya existe
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()

        if existing_user:
            print(f"✅ Super usuario '{username}' ya existe.")
            return

        # Si no existe, lo crea
        hashed_password = get_password_hash(password)
        super_user = User(
            username=username,
            password=hashed_password,
            role=role,
            active=True
        )
        session.add(super_user)
        session.commit()
        print(f"Super usuario creado: {username} / {password}")




# -------------------------------------------------------
# POST /rentas_inmuebles — Crear renta
# -------------------------------------------------------
@app.post("/rentas_inmuebles", tags=["Arrendatario"])
def crear_renta(
    renta: RentaCreate,
    current_user: ArrendatarioUser,          
    session: Session = Depends(get_session)  # <-- Al final
):

    # 1. Encontrar el perfil de Arrendatario del usuario logueado
    arrendatario = session.scalars(
        select(Arrendatario).where(Arrendatario.user_id == current_user.id)
    ).first()
    
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Perfil de arrendatario no encontrado para este usuario.")

    # 2. Validar baños (tu lógica existente)
    num_banos = renta.banos
    parte_decimal = num_banos % 1
    if parte_decimal not in (0, 0.5):
        raise HTTPException(
            status_code=400,
            detail="Sólo se aceptan medios baños o baños enteros (por ejemplo 1, 1.5, 2, 2.5, etc.)."
        )

    # 3. Crear la renta, inyectando el arrendatario_id del usuario logueado
    nueva_renta = Renta(
        **renta.dict(),
        arrendatario_id=arrendatario.id  # <-- ID inferido del token
    )
    session.add(nueva_renta)
    session.commit()
    session.refresh(nueva_renta)

    return {
        "mensaje": "La renta del inmueble se publicó existosamente",
        "renta_id": nueva_renta.id
    }
# -------------------------------------------------------
# GET /rentas_inmuebles — Obtener rentas con filtros
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
# GET /rentas_inmuebles/{id} — Detalle con arrendatario
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
# PATCH /rentas_inmuebles/{id} — Actualizar parcialmente una renta
# -------------------------------------------------------
@app.patch("/rentas_inmuebles/{id}", tags=["Arrendatario"])
def actualizar_renta(
    id: int, 
    datos: RentaUpdate,
    current_user: ArrendatarioUser,           # <-- Antes de 'session'
    session: Session = Depends(get_session)   # <-- Al final
):
    # 1. Encontrar el perfil del Arrendatario logueado
    arrendatario = session.scalars(
        select(Arrendatario).where(Arrendatario.user_id == current_user.id)
    ).first()
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Perfil de arrendatario no encontrado.")

    # 2. Obtener la renta
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    # 3. ¡Verificación de propiedad!
    if renta.arrendatario_id != arrendatario.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este inmueble.")

    # 4. Aplicar cambios (tu lógica existente)
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(renta, key, value)

    session.add(renta)
    session.commit()
    session.refresh(renta)

    return {"mensaje": "El inmueble fue actualizado correctamente", "renta_actualizada": renta}

# -------------------------------------------------------
# GET /historial_renta/{renta_id} — Obtener historial
# -------------------------------------------------------
@app.get("/historial_renta/{renta_id}", response_model=List[HistorialRentaResponse])
def obtener_historial_renta(renta_id: int, session: Session = Depends(get_session)):
    renta = session.get(Renta, renta_id)
    if not renta:
        raise HTTPException(status_code=404, detail="No se encontró el inmueble")

    query = select(HistorialRenta).where(HistorialRenta.renta_id == renta_id)
    return session.exec(query).all()



# -------------------------------------------------------
# POST /historial_renta — Crear nuevo historial (Solo Arrendatario Dueño)
# -------------------------------------------------------
@app.post("/historial_renta", tags=["Arrendatario"], status_code=status.HTTP_201_CREATED)
def crear_historial_renta(
    historial: HistorialRentaCreate,
    current_user: CurrentUser, 
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Crea un nuevo registro en el historial de renta.
    Solo permitido para el usuario con rol 'arrendatario' que sea dueño de la renta asociada.
    """

    # 1. Lógica de permisos por ROL: Solo Arrendatario
    if current_user.role != "arrendatario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo el Arrendatario asociado puede crear registros de historial."
        )

    # 2. Validar que la Renta (a la que se añade el historial) existe
    renta = session.get(Renta, historial.renta_id)
    if not renta:
        raise HTTPException(status_code=404, detail="Renta no encontrada")

    # 3. Lógica para Arrendatario (solo sus rentas)
    
    # 3.1. Encontrar el perfil de arrendatario del usuario logueado
    arrendatario_logueado = session.scalars(
        select(Arrendatario).where(Arrendatario.user_id == current_user.id)
    ).first()

    if not arrendatario_logueado:
        raise HTTPException(status_code=404, detail="Perfil de arrendatario no encontrado.")

    # 3.2. ¡Verificación de propiedad!
    # Comprobar si el 'arrendatario_id' de la Renta es el ID del logueado
    if renta.arrendatario_id != arrendatario_logueado.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para agregar historial a esta renta, ya que no eres el arrendatario asociado."
        )
        
    # 4. Crear el historial (Si pasó los filtros de seguridad)
    nuevo_historial = HistorialRenta(**historial.dict())
    session.add(nuevo_historial)
    session.commit()
    session.refresh(nuevo_historial)

    return {"mensaje": "Historial agregado exitosamente", "historial_id": nuevo_historial.id}

# -------------------------------------------------------
# PATCH /historial_renta/{id} — Actualizar historial (Solo Super User)
# -------------------------------------------------------
@app.patch("/historial_renta/{id}", tags=["Admin"], status_code=status.HTTP_200_OK)
def actualizar_historial_renta(
    id: int,
    datos: HistorialRentaUpdate,
    current_user: CurrentUser,                      # <-- Requerimos el usuario para verificar el rol
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Permite la actualización de un registro de historial de renta.
    Restringido únicamente al rol 'super_user'.
    """

    # 1. Lógica de permisos por ROL
    # Solo se permite la ejecución si el rol es 'super_user'
    if current_user.role != "super_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo un Super User puede modificar registros de historial de renta."
        )

    # 2. Obtener el historial que se quiere modificar
    historial = session.get(HistorialRenta, id)
    if not historial:
        raise HTTPException(status_code=404, detail="Registro de historial no encontrado")

    # 3. Si todo está bien (y el usuario es super_user), aplicar cambios
    # Se eliminó la lógica de verificación de propiedad de arrendatario.
    
    # Aplicar los datos de actualización, ignorando campos no proporcionados (exclude_unset=True)
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(historial, key, value)

    session.add(historial)
    session.commit()
    session.refresh(historial)

    return {"mensaje": "Modificación exitosa", "historial_id": historial.id}


# -------------------------------------------------------
# POST /arrendatario — Crear arrendatario
# -------------------------------------------------------
@app.post("/arrendatario", tags=["Admin"])
def crear_arrendatario(
    datos: ArrendatarioConUserCreate,
    current_admin: SuperUser,                 # <-- Antes de 'session'
    session: Session = Depends(get_session)   # <-- Al final
):
    # 1. Verificar si el username ya existe
    user_existente = session.scalars(
        select(User).where(User.username == datos.user_data.username)
    ).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    # 2. Crear el objeto User con password hasheado
    hashed_password = get_password_hash(datos.user_data.password)
    nuevo_user = User(
        username=datos.user_data.username,
        password=hashed_password,
        role="arrendatario", # Forzar rol
        active=True
    )
    
    session.add(nuevo_user)
    session.commit()
    session.refresh(nuevo_user)

    # 3. Crear el objeto Arrendatario y vincularlo al User
    nuevo_arrendatario = Arrendatario(
        **datos.arrendatario_data.dict(),
        user_id=nuevo_user.id  # <-- El VÍNCULO
    )
    
    session.add(nuevo_arrendatario)
    session.commit()
    session.refresh(nuevo_arrendatario)

    return {
        "mensaje": "Arrendatario y cuenta de usuario creados exitosamente",
        "arrendatario_id": nuevo_arrendatario.id,
        "user_id": nuevo_user.id
    }


# -------------------------------------------------------
# PATCH /arrendatario/{id} — Actualizar arrendatario (Admin y Dueño)
# -------------------------------------------------------
@app.patch("/arrendatario/{arrendatario_id}", tags=["Arrendatario", "Admin"])
def actualizar_arrendatario(
    arrendatario_id: int,
    datos: ArrendatarioUpdate,
    current_user: CurrentUser,                 # <-- AÑADIDO: Pide el usuario logueado (cualquier rol)
    session: Session = Depends(get_session)
):
    # --- Lógica para Super User ---
    if current_user.role == "super_user":
        # El super_user puede editar a CUALQUIER arrendatario por ID
        arrendatario = session.get(Arrendatario, arrendatario_id)
        if not arrendatario:
            raise HTTPException(status_code=404, detail="Arrendatario no encontrado")
        
        # Aplicar cambios
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(arrendatario, key, value)

        session.add(arrendatario)
        session.commit()
        session.refresh(arrendatario)
        return {"mensaje": "Modificación (Admin) exitosa", "arrendatario_actualizado": arrendatario}

    # --- Lógica para Arrendatario (solo él mismo) ---
    elif current_user.role == "arrendatario":
        # 1. Encontrar el perfil de arrendatario del usuario logueado
        arrendatario_logueado = session.scalars(
            select(Arrendatario).where(Arrendatario.user_id == current_user.id)
        ).first()

        if not arrendatario_logueado:
            raise HTTPException(status_code=404, detail="Perfil de arrendatario no encontrado para este usuario.")

        # 2. ¡Verificación de propiedad!
        # Comprobar si el ID que intenta editar (de la URL) es su propio ID
        if arrendatario_logueado.id != arrendatario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar este perfil.")
        
        # 3. Si son el mismo, aplicar cambios (el objeto a modificar es arrendatario_logueado)
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(arrendatario_logueado, key, value)
        
        session.add(arrendatario_logueado)
        session.commit()
        session.refresh(arrendatario_logueado)
        return {"mensaje": "Tu perfil ha sido actualizado exitosamente", "arrendatario_actualizado": arrendatario_logueado}

    # --- Si no es ninguno de esos roles ---
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos necesarios para esta acción."
        )




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


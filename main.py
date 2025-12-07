from fastapi import FastAPI, HTTPException, Depends, Path, Query, status
from typing import List, Optional, Annotated
from sqlmodel import Session, select
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# --- Importar tus módulos locales (AJUSTADO) ---
from database import get_session, create_db_and_tables 
from models import (
    User, Renta, HistorialRenta, Arrendatario, # Existentes
    CatalogoMuebles, CatalogoServicios, RentaMuebles, RentaServicios # Nuevos
)
from schemas import (
    RentaCreate, RentaInmueble, RentaDetalle, ArrendatarioInfo, RentaUpdate,
    HistorialRentaResponse, HistorialRentaCreate, HistorialRentaUpdate,
    ArrendatarioCreate, ArrendatarioUpdate,
    UserBase, UserSchema, Token, TokenData, ArrendatarioConUserCreate,
    # Nuevos esquemas para M:M y Catálogos
    CatalogoBase, RentaMuebleCreate, RentaServicioCreate 
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
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

# --- User Authentication Function (AJUSTADO) ---
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Finds a user in the DB and verifies their password."""
    # Usar el campo correcto: User.username
    user = db.scalars(select(User).where(User.username == username)).first()
    
    # Check for user existence AND active status (usando el campo correcto 'is_active')
    if not user or not user.is_active: 
        return None
    
    # Usar el campo correcto: user.hashed_password
    if not verify_password(password, user.hashed_password): 
        return None
    return user


# --- Authentication Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    """
    Dependency to get the current user from a JWT token.
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
    if user is None or not user.is_active: 
        raise credentials_exception
    return user

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

app = FastAPI(
    title="API de Gestión de Rentas",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    # Solo crea las tablas, asumiendo que la base de datos ya está llena.
    # Si usas SQLite, esta función también crea el archivo de la DB.
    create_db_and_tables() 

# -------------------------------------------------------
# 1️⃣ POST /rentas_inmuebles — Crear renta (Arrendatario)
# -------------------------------------------------------
@app.post("/rentas_inmuebles", response_model=RentaInmueble, tags=["Rentas (Arrendatario)"])
def crear_renta(
    renta: RentaCreate,
    current_user: ArrendatarioUser,          
    session: Session = Depends(get_session)
):
    # 1. Encontrar el perfil de Arrendatario del usuario logueado
    arrendatario = session.scalars(
        select(Arrendatario).where(Arrendatario.user_id == current_user.id)
    ).first()
    
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Perfil de arrendatario no encontrado para este usuario.")

    # 2. Validar baños (tu lógica existente)
    num_banos = renta.banos
    parte_decimal = round(num_banos % 1, 1) # Usar round() para manejar precisión float
    if parte_decimal not in (0.0, 0.5):
        raise HTTPException(
            status_code=400,
            detail="Sólo se aceptan medios baños o baños enteros (por ejemplo 1, 1.5, 2, 2.5, etc.)."
        )

    # 3. Crear la renta, inyectando el arrendatario_id del usuario logueado
    nueva_renta = Renta(
        **renta.model_dump(), # Usar model_dump() para Pydantic v2
        arrendatario_id=arrendatario.id
    )
    session.add(nueva_renta)
    session.commit()
    session.refresh(nueva_renta)

    return nueva_renta # Devuelve la renta creada para coincidir con response_model

# -------------------------------------------------------
# 2️⃣ GET /rentas_inmuebles — Obtener rentas con filtros (Abierto)
# -------------------------------------------------------
@app.get("/rentas_inmuebles", response_model=List[RentaInmueble], tags=["Rentas (Abierto)"])
def obtener_rentas_inmuebles(
    habitaciones: Optional[int] = Query(None, description="Mínimo de habitaciones"),
    banos: Optional[float] = Query(None, description="Mínimo de baños"),
    # ... otros filtros ...
    disponible: Optional[bool] = True, # Asumimos que por defecto se buscan disponibles
    precio: Optional[int] = Query(None, description="Precio máximo"),
    session: Session = Depends(get_session)
):
    query = select(Renta)

    if habitaciones is not None:
        query = query.where(Renta.habitaciones >= habitaciones)
    if banos is not None:
        query = query.where(Renta.banos >= banos)
    # ... (Otros filtros como lat/lon/mascotas/tinaco/estacionamiento/activo) ...
    # Se recomienda usar filtros de rango para lat/lon, pero mantengo la igualdad por ahora.
    
    # Filtros de disponibilidad/precio
    if disponible is not None:
        query = query.where(Renta.disponible == disponible)
    if precio is not None:
        query = query.where(Renta.precio <= precio)

    # Solo mostrar rentas activas por defecto, a menos que se solicite lo contrario
    query = query.where(Renta.activo == True)

    return session.exec(query).all()


# -------------------------------------------------------
# 3️⃣ GET /rentas_inmuebles/{id} — Detalle con Arrendatario, Muebles y Servicios (ACTUALIZADO)
# -------------------------------------------------------
@app.get("/rentas_inmuebles/{id}", response_model=RentaDetalle, tags=["Rentas (Abierto)"])
def obtener_renta_detalle(
    id: int = Path(..., description="ID de la renta"),
    session: Session = Depends(get_session)
):
    # 1. Obtener la Renta (SQLModel carga las relaciones automáticamente)
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    # 2. Obtener la información del Arrendatario (usando la relación ORM)
    arrendatario = renta.arrendatario_rel 
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    arrendatario_info = ArrendatarioInfo(
        nombre=arrendatario.nombre,
        telefono=arrendatario.telefono,
        correo=arrendatario.correo
    )
    
    # 3. Mapear las listas de Muebles y Servicios a CatalogoBase
    # El campo ORM es 'mueble'/'servicio', el campo Pydantic es 'nombre'
    muebles_list = [
        CatalogoBase(id=m.id, nombre=m.mueble) for m in renta.muebles
    ]
    
    servicios_list = [
        CatalogoBase(id=s.id, nombre=s.servicio) for s in renta.servicios
    ]

    # 4. Construir la respuesta RentaDetalle
    # Usamos RentaInmueble para facilitar el mapeo de los campos directos
    renta_base = RentaInmueble.model_validate(renta)
    
    return RentaDetalle(
        **renta_base.model_dump(),
        arrendatario=arrendatario_info,
        muebles=muebles_list,
        servicios=servicios_list,
        link_historial=f"/historial_renta/{renta.id}"
    )


# -------------------------------------------------------
# 4️⃣ PATCH /rentas_inmuebles/{id} — Actualizar parcialmente una renta (Arrendatario)
# -------------------------------------------------------
@app.patch("/rentas_inmuebles/{id}", tags=["Rentas (Arrendatario)"])
def actualizar_renta(
    id: int, 
    datos: RentaUpdate,
    current_user: ArrendatarioUser, 
    session: Session = Depends(get_session) 
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

    # 4. Aplicar cambios
    for key, value in datos.model_dump(exclude_unset=True).items(): # Usar model_dump()
        setattr(renta, key, value)

    session.add(renta)
    session.commit()
    session.refresh(renta)

    return {"mensaje": "El inmueble fue actualizado correctamente", "renta_actualizada": RentaInmueble.model_validate(renta)}


# -------------------------------------------------------
# 5️⃣ GET /historial_renta/{renta_id} — Obtener historial (Abierto)
# -------------------------------------------------------
# ... (Ruta 5, 6, 7 para HistorialRenta se mantienen igual, asegurando que usan 'int' para precio) ...


# -------------------------------------------------------
# 8️⃣ POST /arrendatario — Crear arrendatario (SuperUser)
# -------------------------------------------------------
@app.post("/arrendatario", tags=["Admin"])
def crear_arrendatario(
    datos: ArrendatarioConUserCreate,
    current_admin: SuperUser, 
    session: Session = Depends(get_session)
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
        hashed_password=hashed_password,
        role="arrendatario", # Forzar rol
        is_active=True # Usar is_active
    )
    
    session.add(nuevo_user)
    session.commit()
    session.refresh(nuevo_user)

    # 3. Crear el objeto Arrendatario y vincularlo al User
    nuevo_arrendatario = Arrendatario(
        **datos.arrendatario_data.model_dump(), # Usar model_dump()
        user_id=nuevo_user.id 
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
# 9️⃣ PATCH /arrendatario/{id} — Actualizar arrendatario
# -------------------------------------------------------
# ... (Ruta 9 se mantiene igual) ...

# -------------------------------------------------------
# Rutas de Catálogo y M:M (Añadidas)
# -------------------------------------------------------

## Catálogos (SuperUser/Admin)
@app.post("/catalogo/muebles", response_model=CatalogoBase, tags=["Catalogos (SuperUser)"])
def crear_mueble(
    mueble_data: CatalogoBase, current_admin: SuperUser, session: Session = Depends(get_session)
):
    mueble_existente = session.scalars(select(CatalogoMuebles).where(CatalogoMuebles.mueble == mueble_data.nombre)).first()
    if mueble_existente:
        raise HTTPException(status_code=400, detail="El mueble ya existe.")
        
    # El modelo ORM usa 'mueble'
    nuevo_mueble = CatalogoMuebles(mueble=mueble_data.nombre) 
    session.add(nuevo_mueble)
    session.commit()
    session.refresh(nuevo_mueble)
    # Devolvemos un CatalogoBase con el ID
    return CatalogoBase(id=nuevo_mueble.id, nombre=nuevo_mueble.mueble) 

@app.get("/catalogo/muebles", response_model=List[CatalogoBase], tags=["Catalogos (Abierto)"])
def listar_muebles(session: Session = Depends(get_session)):
    # Mapear el campo 'mueble' a 'nombre' del esquema para la respuesta
    muebles_db = session.exec(select(CatalogoMuebles)).all()
    return [CatalogoBase(id=m.id, nombre=m.mueble) for m in muebles_db]

@app.post("/catalogo/servicios", response_model=CatalogoBase, tags=["Catalogos (SuperUser)"])
def crear_servicio(
    servicio_data: CatalogoBase, current_admin: SuperUser, session: Session = Depends(get_session)
):
    servicio_existente = session.scalars(select(CatalogoServicios).where(CatalogoServicios.servicio == servicio_data.nombre)).first()
    if servicio_existente:
        raise HTTPException(status_code=400, detail="El servicio ya existe.")
        
    # El modelo ORM usa 'servicio'
    nuevo_servicio = CatalogoServicios(servicio=servicio_data.nombre) 
    session.add(nuevo_servicio)
    session.commit()
    session.refresh(nuevo_servicio)
    return CatalogoBase(id=nuevo_servicio.id, nombre=nuevo_servicio.servicio)

@app.get("/catalogo/servicios", response_model=List[CatalogoBase], tags=["Catalogos (Abierto)"])
def listar_servicios(session: Session = Depends(get_session)):
    # Mapear el campo 'servicio' a 'nombre' del esquema para la respuesta
    servicios_db = session.exec(select(CatalogoServicios)).all()
    return [CatalogoBase(id=s.id, nombre=s.servicio) for s in servicios_db]

## Relaciones M:M (Arrendatario)
@app.post("/rentas/{renta_id}/muebles", tags=["Rentas (Arrendatario)"])
def agregar_mueble_a_renta(
    renta_id: int, mueble_data: RentaMuebleCreate, current_user: ArrendatarioUser, session: Session = Depends(get_session)
):
    # 1. Verificar propiedad y existencia (lógica consolidada)
    renta = session.get(Renta, renta_id)
    arrendatario = session.scalars(select(Arrendatario).where(Arrendatario.user_id == current_user.id)).first()
    if not renta or not arrendatario or renta.arrendatario_id != arrendatario.id:
        raise HTTPException(status_code=403, detail="Inmueble no encontrado o no autorizado.")
        
    mueble = session.get(CatalogoMuebles, mueble_data.mueble_id)
    if not mueble:
        raise HTTPException(status_code=404, detail=f"Mueble con ID {mueble_data.mueble_id} no encontrado.")

    # 2. Verificar duplicidad
    relacion_existente = session.scalars(
        select(RentaMuebles).where(RentaMuebles.renta_id == renta_id, RentaMuebles.mueble_id == mueble_data.mueble_id)
    ).first()
    if relacion_existente:
        raise HTTPException(status_code=400, detail="Este mueble ya está asociado a esta renta.")

    # 3. Crear relación
    nueva_relacion = RentaMuebles(renta_id=renta_id, mueble_id=mueble_data.mueble_id)
    session.add(nueva_relacion)
    session.commit()
    
    return {"mensaje": f"Mueble '{mueble.mueble}' agregado a la renta {renta_id}."}

@app.delete("/rentas/{renta_id}/muebles/{mueble_id}", tags=["Rentas (Arrendatario)"])
def eliminar_mueble_de_renta(
    renta_id: int, mueble_id: int, current_user: ArrendatarioUser, session: Session = Depends(get_session)
):
    # Lógica de verificación similar a POST...
    renta = session.get(Renta, renta_id)
    arrendatario = session.scalars(select(Arrendatario).where(Arrendatario.user_id == current_user.id)).first()
    if not renta or not arrendatario or renta.arrendatario_id != arrendatario.id:
        raise HTTPException(status_code=403, detail="Inmueble no encontrado o no autorizado.")

    # Encontrar la relación a eliminar
    relacion = session.scalars(
        select(RentaMuebles).where(RentaMuebles.renta_id == renta_id, RentaMuebles.mueble_id == mueble_id)
    ).first()

    if not relacion:
        raise HTTPException(status_code=404, detail="Relación mueble-renta no encontrada.")

    # Eliminar la relación
    session.delete(relacion)
    session.commit()
    
    return {"mensaje": "Mueble desasociado de la renta exitosamente."}

# Rutas para Servicios (POST y DELETE, similar a Muebles)
@app.post("/rentas/{renta_id}/servicios", tags=["Rentas (Arrendatario)"])
def agregar_servicio_a_renta(
    renta_id: int, servicio_data: RentaServicioCreate, current_user: ArrendatarioUser, session: Session = Depends(get_session)
):
    # Lógica de verificación similar a Muebles...
    renta = session.get(Renta, renta_id)
    arrendatario = session.scalars(select(Arrendatario).where(Arrendatario.user_id == current_user.id)).first()
    if not renta or not arrendatario or renta.arrendatario_id != arrendatario.id:
        raise HTTPException(status_code=403, detail="Inmueble no encontrado o no autorizado.")
        
    servicio = session.get(CatalogoServicios, servicio_data.servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail=f"Servicio con ID {servicio_data.servicio_id} no encontrado.")

    relacion_existente = session.scalars(
        select(RentaServicios).where(RentaServicios.renta_id == renta_id, RentaServicios.servicio_id == servicio_data.servicio_id)
    ).first()

    if relacion_existente:
        raise HTTPException(status_code=400, detail="Este servicio ya está asociado a esta renta.")

    nueva_relacion = RentaServicios(renta_id=renta_id, servicio_id=servicio_data.servicio_id)
    session.add(nueva_relacion)
    session.commit()
    
    return {"mensaje": f"Servicio '{servicio.servicio}' agregado a la renta {renta_id}."}

@app.delete("/rentas/{renta_id}/servicios/{servicio_id}", tags=["Rentas (Arrendatario)"])
def eliminar_servicio_de_renta(
    renta_id: int, servicio_id: int, current_user: ArrendatarioUser, session: Session = Depends(get_session)
):
    # Lógica de verificación similar a Muebles...
    renta = session.get(Renta, renta_id)
    arrendatario = session.scalars(select(Arrendatario).where(Arrendatario.user_id == current_user.id)).first()
    if not renta or not arrendatario or renta.arrendatario_id != arrendatario.id:
        raise HTTPException(status_code=403, detail="Inmueble no encontrado o no autorizado.")

    relacion = session.scalars(
        select(RentaServicios).where(RentaServicios.renta_id == renta_id, RentaServicios.servicio_id == servicio_id)
    ).first()

    if not relacion:
        raise HTTPException(status_code=404, detail="Relación servicio-renta no encontrada.")

    session.delete(relacion)
    session.commit()
    
    return {"mensaje": "Servicio desasociado de la renta exitosamente."}

# -------------------------------------------------------

@app.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    """
    Log in to get a JWT token.
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
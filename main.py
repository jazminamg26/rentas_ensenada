from fastapi import FastAPI, HTTPException, Depends, Path
from typing import List, Optional
from sqlmodel import Session, select

# Importar tus módulos locales
from database import get_session
from models import Renta, Arrendatario, HistorialRenta
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

app = FastAPI()


# -------------------------------------------------------
# 1️⃣ POST /rentas — Crear renta
# -------------------------------------------------------
@app.post("/rentas/")
def crear_renta(renta: RentaCreate, session: Session = Depends(get_session)):
    arrendatario = session.get(Arrendatario, renta.arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    nueva_renta = Renta(**renta.dict())
    session.add(nueva_renta)
    session.commit()
    session.refresh(nueva_renta)

    return {"mensaje": "La renta del inmueble se publicó existosamente", "renta_id": nueva_renta.id}


# -------------------------------------------------------
# 2️⃣ GET /rentas_inmuebles — Obtener rentas con filtros
# -------------------------------------------------------
@app.get("/rentas_inmuebles", response_model=List[RentaInmueble])
def obtener_rentas_inmuebles(
    edificio: Optional[str] = None,
    habitaciones: Optional[int] = None,
    banos: Optional[int] = None,
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

    if edificio is not None:
        query = query.where(Renta.edificio == edificio)
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
        query = query.where(Renta.precio >= precio)

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
@app.patch("/rentas/{id}")
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
@app.post("/historial_renta")
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
# 7️⃣ PATCH /historial_renta/{renta_id} — Actualizar historial
# -------------------------------------------------------
@app.patch("/historial_renta/{renta_id}")
def actualizar_historial_renta(
    renta_id: int,
    datos: HistorialRentaUpdate,
    session: Session = Depends(get_session)
):
    historial = session.get(HistorialRenta, renta_id)
    if not historial:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

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
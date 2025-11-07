from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_session
from models import Renta, Arrendatario
from schemas import RentaCreate
from typing import List, Optional
from sqlmodel import Session, select
from database import get_session  
from models import Renta  
from schemas import RentaInmueble
app = FastAPI()

# POST RENTAS
@app.post("/rentas/")
def crear_renta(renta: RentaCreate, session: Session = Depends(get_session)):
    # Verificar que el arrendatario exista
    arrendatario = session.get(Arrendatario, renta.arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")
    
    nueva_renta = Renta(**renta.dict())
    session.add(nueva_renta)
    session.commit()
    session.refresh(nueva_renta)
    
    return {
        "mensaje": "La renta del inmueble se publicó existosamente",
        "renta_id": nueva_renta.id
    }


# GET RENTAS
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

    result = session.exec(query).all()
    return result



from schemas import RentaInmueble, RentaDetalle, ArrendatarioInfo
from fastapi import Path


@app.get("/rentas_inmuebles/{id}", response_model=RentaDetalle)
def obtener_renta_detalle(
    id: int = Path(..., description="ID de la renta"),
    session: Session = Depends(get_session)
):
    # Buscar la renta
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    # Buscar arrendatario
    arrendatario = session.get(Arrendatario, renta.arrendatario_id)
    if not arrendatario:
        raise HTTPException(status_code=404, detail="Arrendatario no encontrado")

    # Armar respuesta
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


from schemas import RentaUpdate  
@app.patch("/rentas/{id}")
def actualizar_renta(id: int, datos: RentaUpdate, session: Session = Depends(get_session)):
    renta = session.get(Renta, id)
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    
    # Actualizar solo los campos enviados
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(renta, key, value)
    
    session.add(renta)
    session.commit()
    session.refresh(renta)
    
    return {
        "mensaje": "El inmueble fue actualizado correctamente",
        "renta_actualizada": renta
    }

from models import HistorialRenta
from schemas import HistorialRentaResponse
from schemas import HistorialRentaCreate

@app.get("/historial_renta/{renta_id}", response_model=list[HistorialRentaResponse])
def obtener_historial_renta(renta_id: int, session: Session = Depends(get_session)):
    # Verificar si la renta existe
    renta = session.get(Renta, renta_id)
    if not renta:
        raise HTTPException(status_code=404, detail="No se encontró el inmueble")

    # Consultar historial asociado
    query = select(HistorialRenta).where(HistorialRenta.renta_id == renta_id)
    historial = session.exec(query).all()

    return historial

@app.post("/historial_renta")
def crear_historial_renta(historial: HistorialRentaCreate, session: Session = Depends(get_session)):
    # Buscar la renta por id
    renta = session.get(Renta, historial.renta_id)
    
    # Si no existe, responder con mensaje de error
    if not renta:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    
    # Crear nuevo registro en historial
    nuevo_historial = HistorialRenta(
        renta_id=historial.renta_id,
        fecha_inicio=historial.fecha_inicio,
        fecha_fin=historial.fecha_fin,
        precio=historial.precio
    )
    session.add(nuevo_historial)
    session.commit()
    session.refresh(nuevo_historial)

    return {"mensaje": "Historial agregado exitosamente"}


from schemas import HistorialRentaUpdate

@app.patch("/historial_renta/{renta_id}")
def actualizar_historial_renta(
    renta_id: int,
    datos: HistorialRentaUpdate,
    session: Session = Depends(get_session)
):
    # Verificar si existe el historial
    historial = session.get(HistorialRenta, renta_id)
    if not historial:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    
    # Actualizar solo los campos que fueron enviados
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(historial, key, value)

    session.add(historial)
    session.commit()
    session.refresh(historial)

    return {"mensaje": "Modificación exitosa"}

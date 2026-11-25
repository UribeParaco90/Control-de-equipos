from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EquipoCrear, EquipoRespuesta
from app.services import equipos as servicio

router = APIRouter(prefix="/equipos", tags=["Equipos"])


@router.post("", response_model=EquipoRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_equipo(datos: EquipoCrear, db: Session = Depends(get_db)):
    return servicio.registrar_equipo(db, datos)


@router.get("", response_model=list[EquipoRespuesta])
def listar_equipos(marca: Optional[str] = None, db: Session = Depends(get_db)):
    return servicio.listar_equipos(db, marca)


@router.get("/{equipo_id}", response_model=EquipoRespuesta)
def consultar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    return servicio.consultar_equipo(db, equipo_id)


@router.put("/{equipo_id}", response_model=EquipoRespuesta)
def actualizar_equipo(equipo_id: int, datos: EquipoCrear, db: Session = Depends(get_db)):
    return servicio.actualizar_equipo(db, equipo_id, datos)


@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    servicio.eliminar_equipo(db, equipo_id)

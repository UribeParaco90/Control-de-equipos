from typing import Optional

from sqlalchemy.orm import Session

from app.models import Equipo
from app.repositories import equipos as repositorio
from app.schemas import EquipoCrear
from app.services.errors import ConflictError, NotFoundError


def listar_equipos(db: Session, marca: Optional[str] = None) -> list[Equipo]:
    return repositorio.listar(db, marca)


def consultar_equipo(db: Session, equipo_id: int) -> Equipo:
    equipo = repositorio.obtener(db, equipo_id)
    if equipo is None:
        raise NotFoundError("Equipo no encontrado")
    return equipo


def registrar_equipo(db: Session, datos: EquipoCrear) -> Equipo:
    if repositorio.obtener_por_codigo(db, datos.codigo_inventario) is not None:
        raise ConflictError("Ya existe un equipo con ese código de inventario")
    return repositorio.crear(db, datos)


def actualizar_equipo(db: Session, equipo_id: int, datos: EquipoCrear) -> Equipo:
    equipo = consultar_equipo(db, equipo_id)
    if repositorio.obtener_por_codigo(db, datos.codigo_inventario, equipo_id) is not None:
        raise ConflictError("Ese código de inventario ya lo usa otro equipo")
    return repositorio.actualizar(db, equipo, datos)


def eliminar_equipo(db: Session, equipo_id: int) -> None:
    repositorio.eliminar(db, consultar_equipo(db, equipo_id))

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Equipo
from app.schemas import EquipoCrear


def listar(db: Session, marca: Optional[str] = None) -> list[Equipo]:
    consulta = select(Equipo).order_by(Equipo.id)
    if marca is not None:
        consulta = consulta.where(func.lower(Equipo.marca) == marca.lower())
    return list(db.scalars(consulta).all())


def obtener(db: Session, equipo_id: int) -> Optional[Equipo]:
    return db.get(Equipo, equipo_id)


def obtener_por_codigo(
    db: Session, codigo: str, excluir_id: Optional[int] = None
) -> Optional[Equipo]:
    consulta = select(Equipo).where(Equipo.codigo_inventario == codigo)
    if excluir_id is not None:
        consulta = consulta.where(Equipo.id != excluir_id)
    return db.scalar(consulta)


def crear(db: Session, datos: EquipoCrear) -> Equipo:
    equipo = Equipo(**datos.model_dump())
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def actualizar(db: Session, equipo: Equipo, datos: EquipoCrear) -> Equipo:
    for campo, valor in datos.model_dump().items():
        setattr(equipo, campo, valor)
    db.commit()
    db.refresh(equipo)
    return equipo


def eliminar(db: Session, equipo: Equipo) -> None:
    db.delete(equipo)
    db.commit()

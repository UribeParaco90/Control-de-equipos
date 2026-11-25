from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario
from app.schemas import UsuarioCrear


def listar(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.id)).all())


def obtener(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.get(Usuario, usuario_id)


def obtener_por_correo(
    db: Session, correo: str, excluir_id: Optional[int] = None
) -> Optional[Usuario]:
    consulta = select(Usuario).where(Usuario.correo == correo)
    if excluir_id is not None:
        consulta = consulta.where(Usuario.id != excluir_id)
    return db.scalar(consulta)


def crear(db: Session, datos: dict[str, str]) -> Usuario:
    usuario = Usuario(**datos)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar(db: Session, usuario: Usuario, datos: dict[str, str]) -> Usuario:
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()

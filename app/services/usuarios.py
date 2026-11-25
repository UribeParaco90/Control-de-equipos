from sqlalchemy.orm import Session

from app.models import Usuario
from app.repositories import usuarios as repositorio
from app.schemas import UsuarioCrear
from app.services.errors import ConflictError, NotFoundError


def listar_usuarios(db: Session) -> list[Usuario]:
    return repositorio.listar(db)


def consultar_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = repositorio.obtener(db, usuario_id)
    if usuario is None:
        raise NotFoundError("Usuario no encontrado")
    return usuario


def registrar_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    valores = datos.model_dump()
    valores["correo"] = valores["correo"].lower()
    if repositorio.obtener_por_correo(db, valores["correo"]) is not None:
        raise ConflictError("Ya existe un usuario con ese correo")
    return repositorio.crear(db, valores)


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioCrear) -> Usuario:
    usuario = consultar_usuario(db, usuario_id)
    valores = datos.model_dump()
    valores["correo"] = valores["correo"].lower()
    if repositorio.obtener_por_correo(db, valores["correo"], usuario_id) is not None:
        raise ConflictError("Ese correo ya lo usa otro usuario")
    return repositorio.actualizar(db, usuario, valores)


def eliminar_usuario(db: Session, usuario_id: int) -> None:
    repositorio.eliminar(db, consultar_usuario(db, usuario_id))

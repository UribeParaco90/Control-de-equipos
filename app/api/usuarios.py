from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UsuarioCrear, UsuarioRespuesta
from app.services import usuarios as servicio

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    return servicio.registrar_usuario(db, datos)


@router.get("", response_model=list[UsuarioRespuesta])
def listar_usuarios(db: Session = Depends(get_db)):
    return servicio.listar_usuarios(db)


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def consultar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return servicio.consultar_usuario(db, usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(usuario_id: int, datos: UsuarioCrear, db: Session = Depends(get_db)):
    return servicio.actualizar_usuario(db, usuario_id, datos)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    servicio.eliminar_usuario(db, usuario_id)

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EquipoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    codigo_inventario: str = Field(min_length=1, max_length=50)
    marca: str = Field(min_length=1, max_length=50)
    modelo: str = Field(min_length=1, max_length=50)
    fecha_adquisicion: date


class EquipoRespuesta(EquipoCrear):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: str = Field(min_length=3, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    cargo: str = Field(min_length=1, max_length=80)


class UsuarioRespuesta(UsuarioCrear):
    id: int
    model_config = ConfigDict(from_attributes=True)

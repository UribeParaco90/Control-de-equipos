from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_inventario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    marca: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_adquisicion: Mapped[date] = mapped_column(Date, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    cargo: Mapped[str] = mapped_column(String(80), nullable=False)

# =====================================================================
# Ejercicio 10. API para control de equipos tecnológicos
# Aprendiz: Evelio Restrepo Marín
# Stack: FastAPI + SQLAlchemy + PostgreSQL (Neon)
# =====================================================================

# ---------------------------------------------------------------------
# 1. IMPORTACIONES
# ---------------------------------------------------------------------
import os                                  # Para leer variables de entorno (la URL de Neon)
from datetime import date                  # Tipo de dato "fecha" para fecha_adquisicion
from typing import Optional                # Para marcar un parámetro como opcional (filtro de marca)

from dotenv import load_dotenv             # Lee el archivo .env y lo carga como variables de entorno
from fastapi import Depends, FastAPI, HTTPException, status  # Piezas principales de FastAPI
from pydantic import BaseModel, ConfigDict, Field            # Pydantic: valida los datos que entran y salen
from sqlalchemy import Date, Integer, String, create_engine, func, select  # Tipos de columna y consultas
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker  # ORM

# ---------------------------------------------------------------------
# 2. CONEXIÓN A NEON
# ---------------------------------------------------------------------
load_dotenv()                              # Busca el archivo .env y carga sus variables
DATABASE_URL = os.getenv("DATABASE_URL")   # Lee la URL de conexión; devuelve None si no existe

if DATABASE_URL is None:                   # Si olvidaste crear el .env, avisamos con un mensaje claro
    raise RuntimeError("Falta DATABASE_URL en el archivo .env")

# El "engine" es el objeto que mantiene la conexión con la base de datos.
# pool_pre_ping=True prueba la conexión antes de usarla: Neon suspende la base
# cuando no se usa, y así evitamos errores por conexiones "dormidas".
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal fabrica sesiones: una sesión es una "conversación" con la base de datos.
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# ---------------------------------------------------------------------
# 3. MODELO (la tabla en la base de datos)
# ---------------------------------------------------------------------
class Base(DeclarativeBase):               # Clase base de la que heredan todas las tablas
    pass


class Equipo(Base):                        # Cada objeto Equipo es una fila de la tabla
    __tablename__ = "equipos"              # Nombre real de la tabla en Neon

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)       # ID autoincremental
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)             # Nombre del equipo
    codigo_inventario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # No se repite
    marca: Mapped[str] = mapped_column(String(50), nullable=False, index=True)   # index=True acelera el filtro
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)              # Modelo del equipo
    fecha_adquisicion: Mapped[date] = mapped_column(Date, nullable=False)        # Fecha de compra


Base.metadata.create_all(bind=engine)      # Crea la tabla en Neon si todavía no existe


# ---------------------------------------------------------------------
# 4. ESQUEMAS (qué datos aceptamos y devolvemos)
# ---------------------------------------------------------------------
class EquipoCrear(BaseModel):              # Datos que el cliente envía al registrar o actualizar
    nombre: str = Field(min_length=1, max_length=100)             # Obligatorio, entre 1 y 100 caracteres
    codigo_inventario: str = Field(min_length=1, max_length=50)
    marca: str = Field(min_length=1, max_length=50)
    modelo: str = Field(min_length=1, max_length=50)
    fecha_adquisicion: date                                       # Formato esperado: AAAA-MM-DD


class EquipoRespuesta(EquipoCrear):        # Lo que devolvemos: los mismos datos + el id
    id: int
    model_config = ConfigDict(from_attributes=True)  # Permite convertir un objeto Equipo de SQLAlchemy a JSON


# ---------------------------------------------------------------------
# 5. APLICACIÓN Y DEPENDENCIA DE BASE DE DATOS
# ---------------------------------------------------------------------
app = FastAPI(
    title="API Control de Equipos Tecnológicos",
    description="Ejercicio 10 - Aprendiz: Evelio Restrepo Marín",
)


def get_db():                              # Entrega una sesión a cada petición
    with SessionLocal() as db:             # "with" garantiza que la sesión se cierre al terminar
        yield db                           # FastAPI le pasa esta sesión al endpoint


def obtener_o_404(db: Session, equipo_id: int) -> Equipo:
    equipo = db.get(Equipo, equipo_id)     # Busca por llave primaria; devuelve None si no existe
    if equipo is None:                     # Si no existe...
        raise HTTPException(status_code=404, detail="Equipo no encontrado")  # ...respondemos 404
    return equipo


# ---------------------------------------------------------------------
# 6. ENDPOINTS (las 6 actividades del ejercicio)
# ---------------------------------------------------------------------

# Actividad 1: Registrar equipos
@app.post("/equipos", response_model=EquipoRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_equipo(datos: EquipoCrear, db: Session = Depends(get_db)):
    # Buscamos si ya hay un equipo con ese código de inventario
    existente = db.scalar(select(Equipo).where(Equipo.codigo_inventario == datos.codigo_inventario))
    if existente is not None:              # Si ya existe, no lo duplicamos
        raise HTTPException(status_code=409, detail="Ya existe un equipo con ese código de inventario")
    equipo = Equipo(**datos.model_dump())  # Convierte los datos validados en un objeto Equipo
    db.add(equipo)                         # Lo agrega a la sesión
    db.commit()                            # Guarda definitivamente en Neon
    db.refresh(equipo)                     # Recarga el objeto para obtener el id que generó la base
    return equipo


# Actividades 2 y 5: Consultar todos los equipos (con filtro opcional por marca)
@app.get("/equipos", response_model=list[EquipoRespuesta])
def listar_equipos(marca: Optional[str] = None, db: Session = Depends(get_db)):
    consulta = select(Equipo).order_by(Equipo.id)          # Consulta base: todos, ordenados por id
    if marca is not None:                                  # Si el cliente envió ?marca=...
        # Comparamos en minúsculas para que "Dell", "dell" y "DELL" den el mismo resultado
        consulta = consulta.where(func.lower(Equipo.marca) == marca.lower())
    return db.scalars(consulta).all()                      # Ejecuta y devuelve la lista


# Actividad 3: Consultar un equipo por ID
@app.get("/equipos/{equipo_id}", response_model=EquipoRespuesta)
def consultar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    return obtener_o_404(db, equipo_id)


# Actividad 4: Actualizar la información de un equipo
@app.put("/equipos/{equipo_id}", response_model=EquipoRespuesta)
def actualizar_equipo(equipo_id: int, datos: EquipoCrear, db: Session = Depends(get_db)):
    equipo = obtener_o_404(db, equipo_id)                  # Primero verificamos que exista
    # Verificamos que el nuevo código no pertenezca a OTRO equipo
    duplicado = db.scalar(
        select(Equipo).where(
            Equipo.codigo_inventario == datos.codigo_inventario,
            Equipo.id != equipo_id,
        )
    )
    if duplicado is not None:
        raise HTTPException(status_code=409, detail="Ese código de inventario ya lo usa otro equipo")
    for campo, valor in datos.model_dump().items():        # Recorre cada dato enviado...
        setattr(equipo, campo, valor)                      # ...y lo asigna al equipo (equipo.nombre = ..., etc.)
    db.commit()                                            # Guarda los cambios
    db.refresh(equipo)
    return equipo


# Actividad 6: Eliminar equipos
@app.delete("/equipos/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = obtener_o_404(db, equipo_id)
    db.delete(equipo)                      # Marca el equipo para borrarlo
    db.commit()                            # Ejecuta el borrado en Neon

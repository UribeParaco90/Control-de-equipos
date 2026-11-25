from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.equipos import router as equipos_router
from app.api.usuarios import router as usuarios_router
from app.database import Base, engine
from app.services.errors import ConflictError, NotFoundError

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Control de Equipos Tecnológicos",
    description="Ejercicio 10 - Aprendiz: Evelio Restrepo Marín",
    docs_url=None,
    redoc_url=None,
)


@app.exception_handler(NotFoundError)
async def manejar_no_encontrado(request: Request, error: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(ConflictError)
async def manejar_conflicto(request: Request, error: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(error)})


app.include_router(equipos_router)
app.include_router(usuarios_router)

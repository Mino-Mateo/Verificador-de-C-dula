from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from validators import REGISTRO
from validators.base import ResultadoValidacion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ValidateRequest(BaseModel):
    pais: str
    valor: str


@app.get("/api/paises")
def listar_paises() -> list[str]:
    return sorted(REGISTRO.keys())


@app.post("/api/validate")
def validate(req: ValidateRequest):
    pais = req.pais.strip().upper()
    valor = req.valor.strip()

    if not valor:
        return JSONResponse(status_code=400, content={"error": "Valor vacío"})

    validador = REGISTRO.get(pais)
    if validador is None:
        return JSONResponse(status_code=400, content={"error": "País no soportado"})

    try:
        resultado = validador(valor)
    except Exception:
        resultado = ResultadoValidacion(False, "Formato inválido")

    return {"valido": resultado.valido, "mensaje": resultado.mensaje}

# Verificador de Cédula Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir una herramienta web que valida números de identificación (Ecuador, Chile, México) mediante cálculo algorítmico puro, sin consultar bases de datos externas.

**Architecture:** Backend FastAPI con un validador independiente por país (registrados en un diccionario central) expuesto vía REST; frontend React/Vite con un formulario de un solo campo que consume esa API.

**Tech Stack:** Python 3.12 + FastAPI + pytest (backend), React + TypeScript + Vite (frontend).

**Spec:** `docs/superpowers/specs/2026-09-22-verificador-cedula-design.md`

## Global Constraints

- Sin persistencia: no hay base de datos, no se guarda ni loggea el valor ingresado.
- Cada validador devuelve el motivo específico del resultado (no solo `true`/`false`).
- Colombia queda excluido de este alcance (sin dígito verificador estandarizado).
- Ninguna excepción interna debe llegar al cliente como error 500 crudo; se traduce a `{"valido": false, "mensaje": "Formato inválido"}`.
- El frontend no requiere tests automatizados (alcance de formulario simple); se verifica manualmente.
- Todas las pruebas de backend se corren con `python -m pytest` (no `pytest` a secas) para que Python resuelva `import validators` usando el directorio de trabajo (`backend/`) en `sys.path`.

---

## File Structure

```
backend/
  requirements.txt
  main.py
  validators/
    __init__.py            # REGISTRO: dict código país -> función validar
    base.py                 # ResultadoValidacion
    ecuador.py
    chile.py
    mexico.py
  tests/
    test_base.py
    test_ecuador.py
    test_chile.py
    test_mexico.py
    test_main.py

frontend/                   # generado por `npm create vite@latest`
  src/
    api.ts                  # fetch a /api/paises y /api/validate
    App.tsx                 # formulario país + valor + resultado
    App.css
  vite.config.ts            # proxy /api -> backend en dev

README.md                   # instrucciones de uso (actualizado en Task 7)
```

---

### Task 1: Scaffolding del backend

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/validators/__init__.py`
- Create: `backend/validators/base.py`
- Test: `backend/tests/test_base.py`

**Interfaces:**
- Produces: `ResultadoValidacion(valido: bool, mensaje: str)` dataclass en `validators/base.py`, usado por todos los validadores de países.
- Produces: `validators.REGISTRO: dict[str, Callable[[str], ResultadoValidacion]]` (vacío en este task, se completa en Tasks 2-4).

- [ ] **Step 1: Crear estructura de carpetas y `requirements.txt`**

```bash
mkdir -p backend/validators backend/tests
cat > backend/requirements.txt <<'EOF'
fastapi
uvicorn[standard]
pytest
httpx
EOF
```

- [ ] **Step 2: Crear entorno virtual e instalar dependencias**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

- [ ] **Step 3: Escribir el test que falla (`test_base.py`)**

```python
# backend/tests/test_base.py
from validators.base import ResultadoValidacion
from validators import REGISTRO


def test_resultado_validacion_construye_correctamente():
    r = ResultadoValidacion(valido=True, mensaje="ok")
    assert r.valido is True
    assert r.mensaje == "ok"


def test_registro_vacio_al_inicio():
    assert REGISTRO == {}
```

- [ ] **Step 4: Correr el test y verificar que falla**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_base.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'validators'` (los archivos aún no existen)

- [ ] **Step 5: Crear `validators/base.py` y `validators/__init__.py`**

```python
# backend/validators/base.py
from dataclasses import dataclass


@dataclass
class ResultadoValidacion:
    valido: bool
    mensaje: str
```

```python
# backend/validators/__init__.py
REGISTRO = {}
```

- [ ] **Step 6: Correr el test y verificar que pasa**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_base.py -v`
Expected: PASS (2 tests)

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/validators/base.py backend/validators/__init__.py backend/tests/test_base.py
git commit -m "feat: scaffolding del backend con ResultadoValidacion y REGISTRO"
```

---

### Task 2: Validador de Ecuador

**Files:**
- Create: `backend/validators/ecuador.py`
- Modify: `backend/validators/__init__.py`
- Test: `backend/tests/test_ecuador.py`

**Interfaces:**
- Consumes: `ResultadoValidacion` de `validators.base` (Task 1).
- Produces: `validators.ecuador.validar(valor: str) -> ResultadoValidacion`, registrado en `REGISTRO["EC"]`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
# backend/tests/test_ecuador.py
from validators.ecuador import validar


def test_cedula_valida():
    r = validar("1712345675")
    assert r.valido is True
    assert r.mensaje == "Cédula válida"


def test_digito_verificador_incorrecto():
    r = validar("1712345670")
    assert r.valido is False
    assert "esperado 5" in r.mensaje
    assert "recibido 0" in r.mensaje


def test_formato_invalido_longitud():
    r = validar("171234567")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_no_numerico():
    r = validar("17123456AB")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_provincia_invalida():
    r = validar("9912345675")
    assert r.valido is False
    assert "provincia" in r.mensaje.lower()
```

- [ ] **Step 2: Correr los tests y verificar que fallan**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_ecuador.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'validators.ecuador'`

- [ ] **Step 3: Implementar `validators/ecuador.py`**

```python
# backend/validators/ecuador.py
import re

from .base import ResultadoValidacion

COEFICIENTES = [2, 1, 2, 1, 2, 1, 2, 1, 2]


def validar(valor: str) -> ResultadoValidacion:
    valor = valor.strip()

    if not re.fullmatch(r"\d{10}", valor):
        return ResultadoValidacion(False, "Formato inválido: debe tener 10 dígitos numéricos")

    provincia = int(valor[0:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        return ResultadoValidacion(False, "Código de provincia inválido")

    tercer_digito = int(valor[2])
    if tercer_digito >= 6:
        return ResultadoValidacion(False, "Tercer dígito inválido para persona natural")

    suma = 0
    for i in range(9):
        producto = int(valor[i]) * COEFICIENTES[i]
        if producto > 9:
            producto -= 9
        suma += producto

    esperado = (10 - (suma % 10)) % 10
    recibido = int(valor[9])

    if esperado != recibido:
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {esperado}, recibido {recibido})"
        )

    return ResultadoValidacion(True, "Cédula válida")
```

- [ ] **Step 4: Registrar el validador**

```python
# backend/validators/__init__.py
from .ecuador import validar as _validar_ecuador

REGISTRO = {
    "EC": _validar_ecuador,
}
```

- [ ] **Step 5: Correr los tests y verificar que pasan**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_ecuador.py tests/test_base.py -v`
Expected: PASS (todos los tests; `test_registro_vacio_al_inicio` ahora debe actualizarse porque `REGISTRO` ya no está vacío)

- [ ] **Step 6: Actualizar `test_base.py` para reflejar el registro no vacío**

```python
# backend/tests/test_base.py — reemplazar la función test_registro_vacio_al_inicio
def test_registro_contiene_ecuador():
    assert "EC" in REGISTRO
```

- [ ] **Step 7: Correr toda la suite y verificar que pasa**

Run: `cd backend && source .venv/bin/activate && python -m pytest -v`
Expected: PASS (todos los tests)

- [ ] **Step 8: Commit**

```bash
git add backend/validators/ecuador.py backend/validators/__init__.py backend/tests/test_ecuador.py backend/tests/test_base.py
git commit -m "feat: validador de cédula ecuatoriana (módulo 10)"
```

---

### Task 3: Validador de Chile

**Files:**
- Create: `backend/validators/chile.py`
- Modify: `backend/validators/__init__.py`
- Test: `backend/tests/test_chile.py`

**Interfaces:**
- Consumes: `ResultadoValidacion` de `validators.base` (Task 1).
- Produces: `validators.chile.validar(valor: str) -> ResultadoValidacion`, registrado en `REGISTRO["CL"]`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
# backend/tests/test_chile.py
from validators.chile import validar


def test_rut_valido():
    r = validar("12345678-5")
    assert r.valido is True
    assert r.mensaje == "RUT válido"


def test_digito_verificador_incorrecto():
    r = validar("12345678-3")
    assert r.valido is False
    assert "esperado 5" in r.mensaje
    assert "recibido 3" in r.mensaje


def test_formato_invalido_sin_guion():
    r = validar("123456785")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_cuerpo_corto():
    r = validar("123-5")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje
```

- [ ] **Step 2: Correr los tests y verificar que fallan**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_chile.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'validators.chile'`

- [ ] **Step 3: Implementar `validators/chile.py`**

```python
# backend/validators/chile.py
import re

from .base import ResultadoValidacion

PESOS = [2, 3, 4, 5, 6, 7]


def validar(valor: str) -> ResultadoValidacion:
    valor = valor.strip().upper().replace(".", "")

    match = re.fullmatch(r"(\d{7,8})-([0-9K])", valor)
    if not match:
        return ResultadoValidacion(False, "Formato inválido: use NNNNNNNN-V")

    cuerpo, dv = match.group(1), match.group(2)

    suma = 0
    for i, digito in enumerate(reversed(cuerpo)):
        suma += int(digito) * PESOS[i % len(PESOS)]

    resto = 11 - (suma % 11)
    if resto == 11:
        esperado = "0"
    elif resto == 10:
        esperado = "K"
    else:
        esperado = str(resto)

    if esperado != dv:
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {esperado}, recibido {dv})"
        )

    return ResultadoValidacion(True, "RUT válido")
```

- [ ] **Step 4: Registrar el validador**

```python
# backend/validators/__init__.py
from .ecuador import validar as _validar_ecuador
from .chile import validar as _validar_chile

REGISTRO = {
    "EC": _validar_ecuador,
    "CL": _validar_chile,
}
```

- [ ] **Step 5: Correr toda la suite y verificar que pasa**

Run: `cd backend && source .venv/bin/activate && python -m pytest -v`
Expected: PASS (todos los tests)

- [ ] **Step 6: Commit**

```bash
git add backend/validators/chile.py backend/validators/__init__.py backend/tests/test_chile.py
git commit -m "feat: validador de RUT chileno (módulo 11)"
```

---

### Task 4: Validador de México

**Files:**
- Create: `backend/validators/mexico.py`
- Modify: `backend/validators/__init__.py`
- Test: `backend/tests/test_mexico.py`

**Interfaces:**
- Consumes: `ResultadoValidacion` de `validators.base` (Task 1).
- Produces: `validators.mexico.validar(valor: str) -> ResultadoValidacion`, registrado en `REGISTRO["MX"]`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
# backend/tests/test_mexico.py
from validators.mexico import validar


def test_curp_valido():
    r = validar("GOMJ900101HDFMTR01")
    assert r.valido is True
    assert r.mensaje == "CURP válido"


def test_digito_verificador_incorrecto():
    r = validar("GOMJ900101HDFMTR00")
    assert r.valido is False
    assert "esperado 1" in r.mensaje
    assert "recibido 0" in r.mensaje


def test_formato_invalido_longitud():
    r = validar("GOMJ900101HDFMTR0")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_mes_fuera_de_rango():
    # mes "13" no existe
    r = validar("GOMJ901301HDFMTR05")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_sexo_incorrecto():
    r = validar("GOMJ900101XDFMTR01")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje
```

- [ ] **Step 2: Correr los tests y verificar que fallan**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_mexico.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'validators.mexico'`

- [ ] **Step 3: Implementar `validators/mexico.py`**

```python
# backend/validators/mexico.py
import re

from .base import ResultadoValidacion

FORMATO = re.compile(
    r"^[A-Z]{4}"          # 4 letras (nombre)
    r"\d{6}"               # fecha AAMMDD
    r"[HM]"                # sexo
    r"[A-Z]{2}"            # entidad
    r"[BCDFGHJKLMNPQRSTVWXYZ]{3}"  # 3 consonantes internas
    r"[A-Z0-9]"            # diferenciador
    r"\d$"                 # dígito verificador
)

TABLA_VALORES = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"


def validar(valor: str) -> ResultadoValidacion:
    valor = valor.strip().upper()

    if not FORMATO.match(valor):
        return ResultadoValidacion(False, "Formato inválido")

    mes = int(valor[6:8])
    dia = int(valor[8:10])
    if not (1 <= mes <= 12 and 1 <= dia <= 31):
        return ResultadoValidacion(False, "Formato inválido: fecha fuera de rango")

    suma = 0
    for i, caracter in enumerate(valor[:17]):
        valor_caracter = TABLA_VALORES.index(caracter)
        peso = 18 - (i + 1)
        suma += valor_caracter * peso

    esperado = (10 - (suma % 10)) % 10
    recibido = int(valor[17])

    if esperado != recibido:
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {esperado}, recibido {recibido})"
        )

    return ResultadoValidacion(True, "CURP válido")
```

- [ ] **Step 4: Registrar el validador**

```python
# backend/validators/__init__.py
from .ecuador import validar as _validar_ecuador
from .chile import validar as _validar_chile
from .mexico import validar as _validar_mexico

REGISTRO = {
    "EC": _validar_ecuador,
    "CL": _validar_chile,
    "MX": _validar_mexico,
}
```

- [ ] **Step 5: Correr toda la suite y verificar que pasa**

Run: `cd backend && source .venv/bin/activate && python -m pytest -v`
Expected: PASS (todos los tests)

- [ ] **Step 6: Commit**

```bash
git add backend/validators/mexico.py backend/validators/__init__.py backend/tests/test_mexico.py
git commit -m "feat: validador de CURP mexicano"
```

---

### Task 5: API FastAPI

**Files:**
- Create: `backend/main.py`
- Test: `backend/tests/test_main.py`

**Interfaces:**
- Consumes: `validators.REGISTRO` (Tasks 2-4), `ResultadoValidacion` de `validators.base` (Task 1).
- Produces: `GET /api/paises` → `list[str]`; `POST /api/validate` (body `{"pais": str, "valor": str}`) → `{"valido": bool, "mensaje": str}` en 200, o `{"error": str}` en 400. Usado por el frontend en Task 6.

- [ ] **Step 1: Escribir los tests que fallan**

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_listar_paises():
    response = client.get("/api/paises")
    assert response.status_code == 200
    paises = response.json()
    assert set(paises) == {"EC", "CL", "MX"}


def test_validar_cedula_ecuatoriana_valida():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "1712345675"})
    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is True
    assert body["mensaje"] == "Cédula válida"


def test_validar_cedula_ecuatoriana_invalida():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "1712345670"})
    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is False


def test_pais_no_soportado():
    response = client.post("/api/validate", json={"pais": "CO", "valor": "123456"})
    assert response.status_code == 400
    assert response.json() == {"error": "País no soportado"}


def test_valor_vacio():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "   "})
    assert response.status_code == 400
    assert response.json() == {"error": "Valor vacío"}


def test_pais_case_insensitive():
    response = client.post("/api/validate", json={"pais": "ec", "valor": "1712345675"})
    assert response.status_code == 200
    assert response.json()["valido"] is True
```

- [ ] **Step 2: Correr los tests y verificar que fallan**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_main.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Implementar `main.py`**

```python
# backend/main.py
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
```

- [ ] **Step 4: Correr los tests y verificar que pasan**

Run: `cd backend && source .venv/bin/activate && python -m pytest -v`
Expected: PASS (todos los tests del backend)

- [ ] **Step 5: Commit**

```bash
git add backend/main.py backend/tests/test_main.py
git commit -m "feat: API FastAPI con /api/paises y /api/validate"
```

---

### Task 6: Frontend (React + Vite)

**Files:**
- Create: `frontend/` (generado por scaffold de Vite)
- Create: `frontend/src/api.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/App.css`
- Modify: `frontend/vite.config.ts`

**Interfaces:**
- Consumes: `GET /api/paises` y `POST /api/validate` (Task 5), vía proxy de Vite en `/api`.

- [ ] **Step 1: Generar el proyecto Vite**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
cd ..
```

- [ ] **Step 2: Configurar el proxy de desarrollo**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 3: Crear el cliente de API**

```typescript
// frontend/src/api.ts
export interface ValidateResponse {
  valido?: boolean
  mensaje?: string
  error?: string
}

export async function listarPaises(): Promise<string[]> {
  const res = await fetch('/api/paises')
  return res.json()
}

export async function validar(pais: string, valor: string): Promise<ValidateResponse> {
  const res = await fetch('/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pais, valor }),
  })
  return res.json()
}
```

- [ ] **Step 4: Reemplazar `App.tsx` con el formulario**

```tsx
// frontend/src/App.tsx
import { useEffect, useState, type FormEvent } from 'react'
import { listarPaises, validar } from './api'
import type { ValidateResponse } from './api'
import './App.css'

const NOMBRES: Record<string, string> = {
  EC: 'Ecuador',
  CL: 'Chile',
  MX: 'México',
}

function App() {
  const [paises, setPaises] = useState<string[]>([])
  const [pais, setPais] = useState('')
  const [valorInput, setValorInput] = useState('')
  const [resultado, setResultado] = useState<ValidateResponse | null>(null)

  useEffect(() => {
    listarPaises().then((lista) => {
      setPaises(lista)
      if (lista.length > 0) setPais(lista[0])
    })
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const r = await validar(pais, valorInput)
    setResultado(r)
  }

  return (
    <div className="container">
      <h1>Verificador de Cédula</h1>
      <form onSubmit={handleSubmit}>
        <select value={pais} onChange={(e) => setPais(e.target.value)}>
          {paises.map((p) => (
            <option key={p} value={p}>
              {NOMBRES[p] ?? p}
            </option>
          ))}
        </select>
        <input
          type="text"
          value={valorInput}
          onChange={(e) => setValorInput(e.target.value)}
          placeholder="Ingresá el número"
        />
        <button type="submit">Verificar</button>
      </form>
      {resultado && (
        <p className={resultado.valido ? 'ok' : 'fail'}>
          {resultado.mensaje ?? resultado.error}
        </p>
      )}
    </div>
  )
}

export default App
```

- [ ] **Step 5: Simplificar `App.css`**

```css
/* frontend/src/App.css */
.container {
  max-width: 480px;
  margin: 4rem auto;
  font-family: system-ui, sans-serif;
  text-align: center;
}

form {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

select,
input {
  flex: 1;
  padding: 0.5rem;
}

button {
  padding: 0.5rem 1rem;
}

.ok {
  color: #1a7f37;
  font-weight: bold;
}

.fail {
  color: #cf222e;
  font-weight: bold;
}
```

- [ ] **Step 6: Verificar que el build de TypeScript no tiene errores**

Run: `cd frontend && npm run build`
Expected: build exitoso, sin errores de TypeScript, genera `frontend/dist/`

- [ ] **Step 7: Commit**

```bash
git add frontend
git commit -m "feat: frontend React con formulario de verificación"
```

---

### Task 7: Verificación manual end-to-end y documentación

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: backend completo (Tasks 1-5) y frontend completo (Task 6).

- [ ] **Step 1: Levantar el backend**

```bash
cd backend && source .venv/bin/activate && python -m uvicorn main:app --reload --port 8000
```

Expected: servidor corriendo en `http://localhost:8000`, `curl http://localhost:8000/api/paises` devuelve `["CL","EC","MX"]`

- [ ] **Step 2: Levantar el frontend (en otra terminal)**

```bash
cd frontend && npm run dev
```

Expected: servidor corriendo en `http://localhost:5173`

- [ ] **Step 3: Checklist de verificación manual en el navegador**

Abrir `http://localhost:5173` y probar cada caso, confirmando que el mensaje mostrado coincide:

| País | Valor | Resultado esperado |
|------|-------|---------------------|
| Ecuador | `1712345675` | Válido — "Cédula válida" |
| Ecuador | `1712345670` | Inválido — dígito verificador (esperado 5, recibido 0) |
| Ecuador | `171234567` | Inválido — "Formato inválido" |
| Chile | `12345678-5` | Válido — "RUT válido" |
| Chile | `12345678-3` | Inválido — dígito verificador (esperado 5, recibido 3) |
| Chile | `123456785` | Inválido — "Formato inválido" |
| México | `GOMJ900101HDFMTR01` | Válido — "CURP válido" |
| México | `GOMJ900101HDFMTR00` | Inválido — dígito verificador (esperado 1, recibido 0) |
| México | `GOMJ900101HDFMTR0` | Inválido — "Formato inválido" |

- [ ] **Step 4: Actualizar el `README.md`**

```markdown
# Verificador de Cédula

Herramienta web que valida números de identificación (Ecuador, Chile,
México) mediante cálculo algorítmico puro (dígitos verificadores). No
consulta bases de datos externas ni entrega datos personales.

## Cómo correrlo

### Backend

\`\`\`bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
\`\`\`

### Frontend

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Abrir `http://localhost:5173`.

## Tests

\`\`\`bash
cd backend
source .venv/bin/activate
python -m pytest -v
\`\`\`

## Agregar un país nuevo

Crear `backend/validators/<pais>.py` con una función
`validar(valor: str) -> ResultadoValidacion`, y registrarla en
`backend/validators/__init__.py` bajo `REGISTRO`. No requiere cambios en
el frontend ni en los demás validadores.
```

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: instrucciones de instalación y uso"
```

---

## Self-Review Notes

- **Cobertura de spec**: arquitectura (Tasks 1, 5, 6), extensibilidad/registro (Tasks 1-4), algoritmos Ecuador/Chile/México (Tasks 2-4, valores de prueba verificados a mano contra las fórmulas de la spec), contrato de API (Task 5), manejo de errores (Task 5, try/except + `JSONResponse` con forma `{"error": ...}`), estructura de archivos (sección File Structure), testing backend (Tasks 1-5) y verificación manual frontend (Task 7). Colombia queda explícitamente fuera, sin tareas asociadas.
- **Placeholders**: ninguno — todo el código de cada step es completo y ejecutable.
- **Consistencia de tipos**: `ResultadoValidacion(valido, mensaje)` se usa idéntico en Tasks 2-5; `REGISTRO` se construye incrementalmente con las mismas claves (`EC`, `CL`, `MX`) en Tasks 2-4 y se consume igual en Task 5; `validar(pais, valor)` en `api.ts` (Task 6) coincide con el body `{"pais", "valor"}` que espera `ValidateRequest` en `main.py` (Task 5).

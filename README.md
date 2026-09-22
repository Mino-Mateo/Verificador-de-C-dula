# Verificador de Cédula

Herramienta web que valida números de identificación (Ecuador, Chile,
México) mediante cálculo algorítmico puro (dígitos verificadores). No
consulta bases de datos externas ni entrega datos personales.

## Cómo correrlo

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`.

## Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```

## Agregar un país nuevo

Crear `backend/validators/<pais>.py` con una función
`validar(valor: str) -> ResultadoValidacion`, y registrarla en
`backend/validators/__init__.py` bajo `REGISTRO`. No requiere cambios en
el frontend ni en los demás validadores.

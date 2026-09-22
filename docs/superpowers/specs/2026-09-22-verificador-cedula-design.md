# Verificador de Cédula — Diseño

## Propósito

Herramienta web simple: el usuario selecciona un país, escribe un número de
identificación (cédula, RUT, CURP, etc.) y la aplicación indica si es
**matemáticamente válido**, aplicando el algoritmo de verificación oficial de
cada país. No consulta bases de datos externas, no confirma identidad real,
no entrega datos personales — es puro cálculo (checksum/formato).

## Alcance inicial

Países soportados al lanzamiento:

- **Ecuador** — cédula, 10 dígitos, verificador módulo 10.
- **Chile** — RUT, verificador módulo 11 (dígito 0-9 o `K`).
- **México** — CURP, 18 caracteres, verificador basado en tabla de valores.

**Excluido por ahora**: Colombia. La cédula de ciudadanía colombiana no tiene
un dígito verificador público estandarizado (solo el NIT lo tiene), y el
objetivo de esta herramienta es validación algorítmica real, no un chequeo
trivial de longitud/formato. Se puede reconsiderar más adelante si se define
qué tipo de validación tiene sentido ofrecer.

La arquitectura está diseñada para que agregar un país nuevo sea añadir un
archivo, sin tocar el resto del sistema (ver "Extensibilidad").

## Arquitectura

- **Backend**: Python + FastAPI. Expone la lógica de validación vía API REST.
- **Frontend**: React (Vite). Un formulario simple: selector de país, input
  de texto, botón "Verificar", resultado con motivo.
- **Sin persistencia**: no hay base de datos. Cada validación es stateless;
  no se guarda ni se loggea el valor ingresado por el usuario.

### Por qué esta división

Separar backend/frontend permite reusar la lógica de validación desde otros
consumidores en el futuro (otra UI, un CLI, integración con otro sistema) sin
duplicar los algoritmos. Dado que el cálculo es puro (sin efectos
secundarios, sin estado), el backend no necesita más que las funciones de
validación expuestas por HTTP.

## Extensibilidad (registro de validadores)

Cada país es un módulo independiente bajo `backend/validators/`:

```python
# backend/validators/base.py
@dataclass
class ResultadoValidacion:
    valido: bool
    mensaje: str
```

```python
# backend/validators/ecuador.py
def validar(valor: str) -> ResultadoValidacion:
    ...
```

```python
# backend/validators/__init__.py
from . import ecuador, chile, mexico

REGISTRO = {
    "EC": ecuador.validar,
    "CL": chile.validar,
    "MX": mexico.validar,
}
```

Agregar un país nuevo: crear `backend/validators/<pais>.py` con una función
`validar(valor: str) -> ResultadoValidacion`, y añadir una línea a
`REGISTRO`. No requiere cambios en `main.py`, en el frontend (más allá de que
`GET /api/paises` ya refleja el registro automáticamente), ni en los demás
validadores.

## Algoritmos

### Ecuador (cédula, 10 dígitos)

1. Formato: exactamente 10 dígitos numéricos.
2. Dígitos 1-2 (código de provincia): entre 01 y 24, o 30 (casos especiales /
   extranjeros).
3. Dígito 3: debe ser menor a 6 (identifica persona natural).
4. Dígito verificador (posición 10): se aplican coeficientes alternos
   `[2,1,2,1,2,1,2,1,2]` a los primeros 9 dígitos. Para cada producto mayor a
   9, se resta 9. Se suman todos los resultados. El verificador esperado es
   `(10 - (suma % 10)) % 10`. Válido si coincide con el dígito 10 real.

### Chile (RUT, módulo 11)

1. Formato: `NNNNNNNN-V` (7 u 8 dígitos, guion, dígito verificador que puede
   ser `0-9` o `K`). Se acepta con o sin puntos de miles; se normalizan antes
   de validar.
2. Verificador: se recorren los dígitos del cuerpo de derecha a izquierda,
   multiplicando cada uno por la secuencia cíclica `[2,3,4,5,6,7]`. Se suman
   los productos. `resto = 11 - (suma % 11)`. Si `resto == 11` → `0`; si
   `resto == 10` → `K`; si no, el dígito es `resto`. Válido si coincide con
   el verificador ingresado (comparación case-insensitive para `K`).

### México (CURP, 18 caracteres)

1. Formato validado con regex: 4 letras + 6 dígitos (fecha `AAMMDD`, mes
   01-12, día 01-31) + 1 letra de sexo (`H` o `M`) + 2 letras de entidad + 3
   consonantes internas + 1 carácter diferenciador (dígito o letra) + 1
   dígito verificador.
2. Verificador (posición 18): a cada uno de los primeros 17 caracteres se le
   asigna un valor numérico según la tabla oficial CURP (`0`-`9` → su propio
   valor, `A`-`Z` → 10-36 en orden, con la `Ñ` valiendo 24). Cada valor se
   pondera por `(18 - posición)`, se suman los productos, y
   `verificador = (10 - (suma % 10)) % 10`. Válido si coincide con el
   carácter 18.
3. No se valida que la fecha de nacimiento sea "real" más allá de rango de
   mes/día — eso es parte del chequeo de formato, no del checksum.

Todos los validadores devuelven el motivo específico del fallo (formato
inválido, dígito verificador no coincide y cuál se esperaba, etc.), nunca
solo `false`.

## Contrato de API

```
GET  /api/paises
  200: ["EC", "CL", "MX"]

POST /api/validate
  body: {"pais": "EC", "valor": "1234567890"}

  200: {"valido": true, "mensaje": "Cédula válida"}
  200: {"valido": false, "mensaje": "Dígito verificador incorrecto (esperado 5, recibido 3)"}
  400: {"error": "País no soportado"}
  400: {"error": "Valor vacío"}
```

El input se normaliza (trim, uppercase para letras/K) antes de validar. No
requiere sanitización adicional: no se usa en queries SQL, no se ejecuta como
código, no se persiste — es únicamente entrada a funciones aritméticas y
regex.

## Manejo de errores

- Valor vacío o país no reconocido → `400` con mensaje claro, antes de
  invocar cualquier validador.
- Cualquier excepción inesperada dentro de un validador se captura y se
  traduce a `{"valido": false, "mensaje": "Formato inválido"}` — el usuario
  nunca ve un error 500 crudo ni un stack trace.

## Estructura de archivos

```
backend/
  main.py                  # FastAPI app, endpoints
  validators/
    __init__.py            # registro {codigo_pais: funcion_validar}
    base.py                # ResultadoValidacion
    ecuador.py
    chile.py
    mexico.py
  tests/
    test_ecuador.py
    test_chile.py
    test_mexico.py

frontend/
  src/
    App.tsx                # selector país + input + resultado
    api.ts                 # fetch a /api/validate
  vite.config.ts
```

## Testing

- Backend: `pytest`, casos por país: un valor real válido, uno con dígito
  verificador alterado (debe fallar con mensaje específico), uno con formato
  incorrecto (longitud errónea, caracteres no permitidos).
- Frontend: sin tests automatizados dado el alcance (formulario simple);
  verificación manual en navegador de los casos válido/inválido por país.

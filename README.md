# Verificador de Cédula

Herramienta web que valida números de identificación (Ecuador, Chile,
México, Brasil) mediante cálculo algorítmico puro (dígitos verificadores).
No consulta bases de datos externas ni entrega datos personales, y no
verifica que una persona real exista o sea dueña del número: solo confirma
si el número es matemáticamente consistente con el algoritmo oficial de
cada país.

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

## Cómo funciona cada validador (por qué es matemáticamente confiable)

Cada país incluido tiene un algoritmo de dígito verificador **oficial y
públicamente documentado** por la entidad emisora. Esto es lo que separa
un país "soportado" de uno "excluido" en esta herramienta.

### Ecuador — cédula (módulo 10)

Los primeros 9 dígitos se multiplican por coeficientes alternos
`[2,1,2,1,2,1,2,1,2]`. Si un producto supera 9, se le resta 9 (esto es
equivalente a sumar los dígitos del producto, la base del algoritmo de
Luhn). La suma de esos 9 resultados se usa para calcular
`(10 - (suma % 10)) % 10`, que debe coincidir con el décimo dígito. Es el
mismo principio que el algoritmo de Luhn usado en tarjetas de crédito.

### Chile — RUT (módulo 11)

El cuerpo del RUT se recorre de derecha a izquierda multiplicando cada
dígito por la secuencia cíclica `[2,3,4,5,6,7]`. La suma total, reducida
módulo 11, determina el dígito verificador (`0` si el resto es 11, `K` si
es 10). Es un checksum ponderado clásico: cualquier dígito mal transcrito
o dos dígitos adyacentes transpuestos casi siempre cambia el resultado del
módulo, por eso sirve para detectar errores de tipeo.

### México — CURP (checksum posicional)

Los primeros 17 caracteres del CURP se convierten a un valor numérico
mediante una tabla fija (`0-9` valen su propio número, `A-Z` valen 10-36,
con la `Ñ` intercalada entre la `N` y la `O`). Cada valor se multiplica por
su peso posicional (`18 - posición`), se suman todos los productos, y
`(10 - (suma % 10)) % 10` debe coincidir con el dígito 18. Esto verifica
que el CURP no fue alterado carácter por carácter después de ser emitido.

### Brasil — CPF (doble módulo 11)

El CPF tiene 11 dígitos: 9 de base + 2 verificadores, calculados en dos
pasadas de módulo 11 (algoritmo oficial de la Receita Federal). El primer
dígito pondera los 9 dígitos base con pesos `10..2`; el segundo pondera los
10 dígitos anteriores (base + primer verificador) con pesos `11..2`. En
ambos casos, si el resto de la división por 11 es menor a 2, el dígito
esperado es `0`; si no, es `11 - resto`. Además, los CPF con los 11
dígitos iguales (ej. `11111111111`) pasan matemáticamente este cálculo
pero la Receita Federal nunca los emite, por lo que se rechazan
explícitamente.

## Países excluidos (y por qué)

Estos países **no están soportados** porque no existe un algoritmo de
dígito verificador oficial y confiable para su documento de identidad
principal. Agregarlos solo permitiría validar longitud/formato, lo cual
contradice el propósito de esta herramienta (verificación matemática
real, no un chequeo superficial):

- **Colombia** — la cédula de ciudadanía es un número secuencial asignado
  por la Registraduría, sin dígito verificador matemático (el NIT sí tiene
  uno, pero es un identificador tributario distinto, no la cédula).
- **Argentina** — el DNI es un número secuencial asignado por RENAPER, sin
  ningún dígito de control matemático.
- **Perú** — el DNI de 8 dígitos de RENIEC no tiene un dígito verificador
  oficial. Existen algoritmos de módulo 11 que circulan en herramientas de
  terceros, pero son heurísticas de ingeniería inversa no confirmadas por
  RENIEC: pueden coincidir con muchos DNIs reales por casualidad
  estadística, pero no hay garantía de que sean el mecanismo real, así que
  no se incluyen aquí.

## Agregar un país nuevo

Crear `backend/validators/<pais>.py` con una función
`validar(valor: str) -> ResultadoValidacion`, y registrarla en
`backend/validators/__init__.py` bajo `REGISTRO`. No requiere cambios en
el frontend ni en los demás validadores. Antes de agregar un país, verificar
que su documento de identidad tenga un dígito verificador **oficial y
documentado** — si no lo tiene, agregarlo a la sección "Países excluidos"
en vez de implementar una validación de formato que dé una falsa sensación
de certeza matemática.

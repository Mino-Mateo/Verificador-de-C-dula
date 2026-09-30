"""Genera los diagramas SVG del README y comprueba cada cálculo.

Uso: python3 docs/generar-diagramas.py  (desde la raíz del repo)
Cada ejemplo es ficticio. El script calcula el dígito verificador y falla si no coincide.
"""
from html import escape

FONDO, PANEL, BORDE = "#0d0b14", "#17141f", "#2a2536"
TEXTO, TENUE = "#f4f1f8", "#a8a1b5"
COLORES = {
    "origen": "#fa93fa",
    "tipo": "#7dd3fc",
    "datos": "#f5b454",
    "secuencia": "#9ca3af",
    "verificador": "#4ade80",
}
LEYENDA = {
    "origen": "Lugar",
    "tipo": "Tipo",
    "datos": "Datos de la persona",
    "secuencia": "Secuencia",
    "verificador": "Se calcula",
}
FUENTE = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
MONO = "font-family='JetBrains Mono, Consolas, monospace'"


def t(x, y, s, size=14, color=TEXTO, anchor="start", mono=False, peso="400"):
    f = MONO if mono else FUENTE
    return f"<text x='{x}' y='{y}' {f} font-size='{size}' font-weight='{peso}' fill='{color}' text-anchor='{anchor}'>{escape(str(s))}</text>"


def caja(x, y, w, h, rol, radio=6):
    c = COLORES[rol]
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{radio}' fill='{c}' fill-opacity='0.16' stroke='{c}' stroke-width='1.5'/>"


def diagrama(ruta, titulo, subtitulo, grupos, filas, formula, resultado, ancho=900):
    """grupos: [(texto, rol, etiqueta)]; filas: [(nombre, [valores por columna], rol_por_columna o None)]"""
    partes = []
    y = 40
    partes.append(t(32, y, titulo, 22, peso="700"))
    partes.append(t(32, y + 24, subtitulo, 14, TENUE))
    # Tira con el número partido por roles
    celda, gap, x = 42, 4, 32
    y_tira = 100
    for i, (texto, rol, etiqueta) in enumerate(grupos):
        x0 = x
        for ch in texto:
            partes.append(caja(x, y_tira, celda, 50, rol))
            partes.append(t(x + celda / 2, y_tira + 33, ch, 22, TEXTO, "middle", True, "600"))
            x += celda + gap
        x1 = x - gap
        c = COLORES[rol]
        # Etiquetas en dos alturas alternadas para que las de grupos angostos no se encimen
        baja = 22 * (i % 2)
        partes.append(f"<path d='M{x0} {y_tira + 60} v8 H{x1} v-8 M{(x0 + x1) / 2} {y_tira + 68} v{6 + baja}' fill='none' stroke='{c}' stroke-width='1.5'/>")
        partes.append(t((x0 + x1) / 2, y_tira + 90 + baja, etiqueta, 13, c, "middle", peso="600"))
        x += 10
    ancho = max(ancho, int(x + 22))
    # Leyenda de colores
    y_ley = y_tira + 150
    lx = 32
    for rol in dict.fromkeys(r for _, r, _ in grupos):
        partes.append(caja(lx, y_ley - 12, 14, 14, rol, 3))
        partes.append(t(lx + 22, y_ley, LEYENDA[rol], 13, TENUE))
        lx += 40 + 8 * len(LEYENDA[rol])
    # Panel de cálculo: columnas según el nombre de fila más largo
    col0 = 44 + 7 * max(len(str(f[0])) for f in filas) + 36
    colw = 40
    ancho = max(ancho, int(col0 + colw * max(len(f[1]) for f in filas) + 40))
    y_pan = y_ley + 30
    alto_pan = 60 + 34 * len(filas) + 80
    partes.append(f"<rect x='24' y='{y_pan}' width='{ancho - 48}' height='{alto_pan}' rx='10' fill='{PANEL}' stroke='{BORDE}'/>")
    partes.append(t(44, y_pan + 32, "Cálculo del dígito verificador", 15, TEXTO, peso="700"))
    for i, (nombre, valores, roles) in enumerate(filas):
        yy = y_pan + 70 + i * 34
        partes.append(t(44, yy, nombre, 13, TENUE))
        for j, v in enumerate(valores):
            cx = col0 + j * colw
            if roles and roles[j]:
                partes.append(caja(cx - 16, yy - 20, 32, 28, roles[j], 4))
            partes.append(t(cx, yy, v, 15, TEXTO, "middle", True))
    yf = y_pan + 70 + len(filas) * 34 + 10
    partes.append(t(44, yf, formula, 14, TENUE, mono=True))
    partes.append(caja(44, yf + 16, ancho - 136, 36, "verificador"))
    partes.append(t(60, yf + 40, resultado, 15, TEXTO, mono=True, peso="600"))
    alto = y_pan + alto_pan + 24
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{ancho}' height='{alto}' viewBox='0 0 {ancho} {alto}' role='img' aria-label='{escape(titulo)}'>"
           f"<rect width='{ancho}' height='{alto}' rx='14' fill='{FONDO}'/>" + "".join(partes) + "</svg>\n")
    open(ruta, "w", encoding="utf-8").write(svg)


# Ecuador: 1234567897 (ficticio)
ced = "1234567897"
coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
prod = [int(d) * c for d, c in zip(ced[:9], coef)]
ajus = [p - 9 if p > 9 else p for p in prod]
suma = sum(ajus)
dv = (10 - suma % 10) % 10
assert dv == int(ced[9]), dv
diagrama("docs/ecuador.svg", "Ecuador: cédula de identidad", "Ejemplo ficticio 1234567897 (10 dígitos)",
         [(ced[:2], "origen", "Provincia 12: Los Ríos"), (ced[2], "tipo", "0 a 5"), (ced[3:9], "secuencia", "Consecutivo"), (ced[9], "verificador", "Verificador")],
         [("Dígito", list(ced[:9]), None), ("Coeficiente", coef, None), ("Producto", prod, None),
          ("Si pasa de 9, -9", ajus, ["verificador" if p > 9 else None for p in prod])],
         f"suma = {' + '.join(map(str, ajus))} = {suma}",
         f"(10 - {suma} mod 10) mod 10 = (10 - {suma % 10}) mod 10 = {dv}   coincide con el décimo dígito")

# Chile: 12.345.678-5 (ejemplo clásico)
cuerpo = "12345678"
pesos = [2, 3, 4, 5, 6, 7, 2, 3]
inv = list(reversed(cuerpo))
prod = [int(d) * p for d, p in zip(inv, pesos)]
suma = sum(prod)
r = 11 - suma % 11
dvc = "0" if r == 11 else "K" if r == 10 else str(r)
assert dvc == "5", dvc
diagrama("docs/chile.svg", "Chile: RUN / RUT", "Ejemplo 12.345.678-5: el cuerpo se recorre de derecha a izquierda",
         [(cuerpo, "secuencia", "Número asignado"), ("5", "verificador", "Verificador")],
         [("Dígito (der. a izq.)", inv, None), ("Peso (2 a 7, cíclico)", pesos, None), ("Producto", prod, None)],
         f"suma = {suma};  {suma} mod 11 = {suma % 11};  11 - {suma % 11} = {r}",
         f"verificador = {dvc}   (si da 11 es 0, si da 10 es K)")

# México: CURP ficticia de "Juan Pérez López", 1990-01-01, Puebla
curp = "PELJ900101HPLRPN00"
tabla = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
vals = [tabla.index(c) for c in curp[:17]]
pes = list(range(18, 1, -1))
prod = [v * p for v, p in zip(vals, pes)]
suma = sum(prod)
dvm = (10 - suma % 10) % 10
assert dvm == int(curp[17]), dvm
diagrama("docs/mexico.svg", "México: CURP", "Ejemplo ficticio de Juan Pérez López, nacido el 01/01/1990 en Puebla (18 caracteres)",
         [(curp[:4], "datos", "Iniciales"), (curp[4:10], "datos", "Nacimiento AAMMDD"), (curp[10], "datos", "Sexo"),
          (curp[11:13], "origen", "Estado"), (curp[13:16], "datos", "Consonantes"), (curp[16], "secuencia", "Homoclave"), (curp[17], "verificador", "Verif.")],
         [("Carácter", list(curp[:17]), None), ("Valor (tabla)", vals, None), ("Peso (18 a 2)", pes, None), ("Producto", prod, None)],
         f"suma = {suma};  {suma} mod 10 = {suma % 10}",
         f"(10 - {suma % 10}) mod 10 = {dvm}   coincide con el carácter 18", ancho=920)

# Brasil: CPF 123.456.789-09 (ejemplo clásico)
cpf = "12345678909"
def dv_cpf(base, desde):
    s = sum(int(d) * p for d, p in zip(base, range(desde, 1, -1)))
    return s, (0 if s % 11 < 2 else 11 - s % 11)
s1, d1 = dv_cpf(cpf[:9], 10)
s2, d2 = dv_cpf(cpf[:9] + str(d1), 11)
assert f"{d1}{d2}" == cpf[9:], (d1, d2)
diagrama("docs/brasil.svg", "Brasil: CPF", "Ejemplo 123.456.789-09: dos verificadores, uno sobre el otro",
         [(cpf[:8], "secuencia", "Número base"), (cpf[8], "origen", "Región fiscal 9: PR, SC"), (cpf[9:], "verificador", "Verificadores")],
         [("Dígito", list(cpf[:10]), [None] * 9 + ["verificador"]), ("Peso 1.er DV (10 a 2)", list(range(10, 1, -1)), None),
          ("Peso 2.º DV (11 a 2)", list(range(11, 1, -1)), None)],
         f"1.er: suma {s1}, {s1} mod 11 = {s1 % 11} (< 2) -> 0;   2.º: suma {s2}, {s2} mod 11 = {s2 % 11} -> 11 - {s2 % 11} = {d2}",
         f"verificadores = {d1}{d2}   (resto menor que 2 da 0; si no, 11 - resto)", ancho=900)
print("ok: 4 diagramas, todos los cálculos coinciden")

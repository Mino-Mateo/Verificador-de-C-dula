import re

from .base import ResultadoValidacion

FORMATO = re.compile(
    r"^[A-Z]{4}"          # 4 letras (nombre)
    r"[0-9]{6}"            # fecha AAMMDD
    r"[HM]"                # sexo
    r"[A-Z]{2}"            # entidad
    r"[BCDFGHJKLMNPQRSTVWXYZ]{3}"  # 3 consonantes internas
    r"[A-Z0-9]"            # diferenciador
    r"[0-9]$"              # dígito verificador
)

TABLA_VALORES = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

# Claves de entidad federativa de RENAPO; NE = nacido en el extranjero
ESTADOS = {
    "AS", "BC", "BS", "CC", "CS", "CH", "CL", "CM", "DF", "DG", "GT", "GR", "HG", "JC", "MC", "MN", "MS",
    "NT", "NL", "OC", "PL", "QT", "QR", "SP", "SL", "SR", "TC", "TS", "TL", "VZ", "YN", "ZS", "NE",
}


def validar(valor: str) -> ResultadoValidacion:
    valor = valor.strip().upper()

    if not FORMATO.match(valor):
        return ResultadoValidacion(False, "Formato inválido")

    mes = int(valor[6:8])
    dia = int(valor[8:10])
    if not (1 <= mes <= 12 and 1 <= dia <= 31):
        return ResultadoValidacion(False, "Formato inválido: fecha fuera de rango")

    if valor[11:13] not in ESTADOS:
        return ResultadoValidacion(False, "Formato inválido: clave de estado inexistente")

    suma = 0
    for i, caracter in enumerate(valor[:17]):
        valor_caracter = TABLA_VALORES.index(caracter)
        peso = 18 - i  # pesos 18 a 2 (ver tests con CURP publicadas)
        suma += valor_caracter * peso

    esperado = (10 - (suma % 10)) % 10
    recibido = int(valor[17])

    if esperado != recibido:
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {esperado}, recibido {recibido})"
        )

    return ResultadoValidacion(True, "CURP válido")

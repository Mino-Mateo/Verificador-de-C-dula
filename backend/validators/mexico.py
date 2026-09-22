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

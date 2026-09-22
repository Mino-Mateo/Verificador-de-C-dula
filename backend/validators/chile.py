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

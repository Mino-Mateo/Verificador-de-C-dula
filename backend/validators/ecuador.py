import re

from .base import ResultadoValidacion

COEFICIENTES = [2, 1, 2, 1, 2, 1, 2, 1, 2]


def validar(valor: str) -> ResultadoValidacion:
    valor = valor.strip()

    if not re.fullmatch(r"[0-9]{10}", valor):
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

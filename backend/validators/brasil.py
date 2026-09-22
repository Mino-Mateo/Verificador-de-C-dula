import re

from .base import ResultadoValidacion


def _digito_verificador(digitos: list[int], peso_inicial: int) -> int:
    suma = sum(d * (peso_inicial - i) for i, d in enumerate(digitos))
    resto = suma % 11
    return 0 if resto < 2 else 11 - resto


def validar(valor: str) -> ResultadoValidacion:
    valor = re.sub(r"[.\-]", "", valor.strip())

    if not re.fullmatch(r"[0-9]{11}", valor):
        return ResultadoValidacion(False, "Formato inválido: debe tener 11 dígitos numéricos")

    if len(set(valor)) == 1:
        return ResultadoValidacion(False, "CPF inválido: todos los dígitos son iguales")

    base = [int(c) for c in valor[:9]]
    digito1 = _digito_verificador(base, 10)
    if digito1 != int(valor[9]):
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {digito1}, recibido {valor[9]})"
        )

    digito2 = _digito_verificador(base + [digito1], 11)
    if digito2 != int(valor[10]):
        return ResultadoValidacion(
            False, f"Dígito verificador incorrecto (esperado {digito2}, recibido {valor[10]})"
        )

    return ResultadoValidacion(True, "CPF válido")

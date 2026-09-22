from validators.base import ResultadoValidacion
from validators import REGISTRO


def test_resultado_validacion_construye_correctamente():
    r = ResultadoValidacion(valido=True, mensaje="ok")
    assert r.valido is True
    assert r.mensaje == "ok"


def test_registro_vacio_al_inicio():
    assert REGISTRO == {}

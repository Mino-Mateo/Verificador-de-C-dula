from validators.ecuador import validar


def test_cedula_valida():
    r = validar("1712345675")
    assert r.valido is True
    assert r.mensaje == "Cédula válida"


def test_digito_verificador_incorrecto():
    r = validar("1712345670")
    assert r.valido is False
    assert "esperado 5" in r.mensaje
    assert "recibido 0" in r.mensaje


def test_formato_invalido_longitud():
    r = validar("171234567")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_no_numerico():
    r = validar("17123456AB")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_provincia_invalida():
    r = validar("9912345675")
    assert r.valido is False
    assert "provincia" in r.mensaje.lower()

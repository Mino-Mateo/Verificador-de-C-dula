from validators.chile import validar


def test_rut_valido():
    r = validar("12345678-5")
    assert r.valido is True
    assert r.mensaje == "RUT válido"


def test_digito_verificador_incorrecto():
    r = validar("12345678-3")
    assert r.valido is False
    assert "esperado 5" in r.mensaje
    assert "recibido 3" in r.mensaje


def test_formato_invalido_sin_guion():
    r = validar("123456785")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_cuerpo_corto():
    r = validar("123-5")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje

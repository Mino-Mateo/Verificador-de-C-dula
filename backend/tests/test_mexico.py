from validators.mexico import validar


def test_curp_valido():
    r = validar("GOMJ900101HDFMTR01")
    assert r.valido is True
    assert r.mensaje == "CURP válido"


def test_digito_verificador_incorrecto():
    r = validar("GOMJ900101HDFMTR00")
    assert r.valido is False
    assert "esperado 1" in r.mensaje
    assert "recibido 0" in r.mensaje


def test_formato_invalido_longitud():
    r = validar("GOMJ900101HDFMTR0")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_mes_fuera_de_rango():
    # mes "13" no existe
    r = validar("GOMJ901301HDFMTR05")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_sexo_incorrecto():
    r = validar("GOMJ900101XDFMTR01")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje

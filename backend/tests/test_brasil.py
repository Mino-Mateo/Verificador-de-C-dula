from validators.brasil import validar


def test_cpf_valido():
    r = validar("11144477735")
    assert r.valido is True
    assert r.mensaje == "CPF válido"


def test_digito_verificador_incorrecto():
    r = validar("11144477730")
    assert r.valido is False
    assert "esperado 5" in r.mensaje
    assert "recibido 0" in r.mensaje


def test_todos_los_digitos_iguales_es_invalido():
    r = validar("11111111111")
    assert r.valido is False
    assert "todos los dígitos son iguales" in r.mensaje


def test_formato_invalido_longitud():
    r = validar("1114447773")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_formato_invalido_digitos_unicode():
    r = validar("１１１４４４７７７３５")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_acepta_formato_con_puntos_y_guion():
    r = validar("111.444.777-35")
    assert r.valido is True

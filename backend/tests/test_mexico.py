from validators.mexico import validar


# CURP publicadas como válidas en los tests de python-stdnum
# (https://github.com/arthurdejong/python-stdnum, tests/test_mx_curp.doctest)
CURP_REFERENCIA = [
    "AAAA000101HDFCCC09",
    "AAMG890608HDFLJL00",
    "BAAA890317HDFRLL03",
    "BAAD890419HMNRRV07",
    "BEML920313HMCLNS09",
    "HEGG560427MVZRRL04",
    "HEGR891009HMNRRD09",
    "MARR890512HMNRMN09",
    "MESJ890928HMNZNS00",
    "OOMG890727HMNRSR06",
    "PEGL890909MJCRMS08",
    "TOMA880125HMNRRN02",
    "TOMA880125HMNRRNO2",
    "VIAA900930MMNCLL08",
]


def test_curp_de_referencia_validas():
    for curp in CURP_REFERENCIA:
        r = validar(curp)
        assert r.valido is True, (curp, r.mensaje)


def test_curp_valido():
    r = validar("BOXW310820HNERXN09")
    assert r.valido is True
    assert r.mensaje == "CURP válido"


def test_digito_verificador_incorrecto():
    r = validar("BOXW310820HNERXN08")
    assert r.valido is False
    assert "esperado 9" in r.mensaje
    assert "recibido 8" in r.mensaje


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


def test_formato_invalido_digitos_unicode():
    # fullwidth digits U+FF10-FF19 should be rejected, not cause ValueError
    r = validar("GOMJ９００101HDFMTR01")
    assert r.valido is False
    assert "Formato inválido" in r.mensaje


def test_estado_inexistente():
    # El verificador cuadra, pero QQ no es una entidad federativa
    r = validar("PEGL890909MQQRMS02")
    assert r.valido is False
    assert "estado inexistente" in r.mensaje

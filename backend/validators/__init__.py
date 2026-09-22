from .ecuador import validar as _validar_ecuador
from .chile import validar as _validar_chile
from .mexico import validar as _validar_mexico
from .brasil import validar as _validar_brasil

REGISTRO = {
    "EC": _validar_ecuador,
    "CL": _validar_chile,
    "MX": _validar_mexico,
    "BR": _validar_brasil,
}

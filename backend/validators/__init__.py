from .ecuador import validar as _validar_ecuador
from .chile import validar as _validar_chile

REGISTRO = {
    "EC": _validar_ecuador,
    "CL": _validar_chile,
}

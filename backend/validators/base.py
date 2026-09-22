from dataclasses import dataclass


@dataclass
class ResultadoValidacion:
    valido: bool
    mensaje: str

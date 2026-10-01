"""caboclink - calculadora de enlace de cobre.

Calculadora e validador de orcamento de perda para enlace de cabeamento
estruturado em cobre. Funciona offline, so com a biblioteca padrao do Python
alem de PyYAML para leitura de arquivos.

Copper link loss budget calculator and validator. Runs offline using only the
Python standard library plus PyYAML for file parsing.
"""

from .orcamento import Enlace, Resultado, orcar
from .certificacao import Laudo, gerar_laudo
from .perdas import CABOS, COMPONENTES

__all__ = [
    "Enlace",
    "Resultado",
    "orcar",
    "Laudo",
    "gerar_laudo",
    "CABOS",
    "COMPONENTES",
]

__version__ = "1.0.0"
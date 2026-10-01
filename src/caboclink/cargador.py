"""Carregamento de arquivos YAML de materiais e de enlace.

Loading of YAML material and link definition files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .orcamento import Enlace


def carregar_materiais(caminho: str | Path) -> dict[str, Any]:
    """Le o arquivo de catalogo de materiais.

    Read the material catalog file.

    Args:
        caminho: Caminho para o ``.yaml``.

    Returns:
        O conteudo do YAML como ``dict``.
    """
    with open(caminho, "r", encoding="utf-8") as fh:
        dados = yaml.safe_load(fh)
    if not isinstance(dados, dict):
        raise ValueError(f"{caminho}: esperado um mapeamento no topo / expected a mapping at the top")
    return dados


def carregar_enlace(caminho: str | Path) -> Enlace:
    """Le um arquivo de enlace e converte para :class:`Enlace`.

    Read a link file and convert it to an :class:`Enlace`.

    Args:
        caminho: Caminho para o ``.yaml``.

    Returns:
        O enlace descrito no arquivo.

    Raises:
        ValueError: Se a categoria nao existir ou o comprimento for negativo.
    """
    dados = carregar_materiais(caminho)

    categoria = str(dados.get("categoria", "6"))
    comprimento = float(dados.get("comprimento_canal_m", 90.0))
    if comprimento < 0:
        raise ValueError("comprimento_canal_m nao pode ser negativo / must not be negative")

    frequencias = dados.get("frequencias") or ()
    if isinstance(frequencias, list):
        frequencias = tuple(int(f) for f in frequencias)

    return Enlace(
        categoria=categoria,
        comprimento_canal_m=comprimento,
        patch_cords=int(dados.get("patch_cords", 2)),
        conectores=int(dados.get("conectores", 2)),
        patch_panels=int(dados.get("patch_panels", 1)),
        divisor=bool(dados.get("divisor", False)),
        frequencias=frequencias,
    )
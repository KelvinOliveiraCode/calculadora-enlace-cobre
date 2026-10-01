"""Tabelas de perda de enlace em cabeamento estruturado cobre.

Loss tables for structured copper cabling.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Limite fisico do canal em cobre, em metros (ISO/IEC 11801).
LIMITE_CANAL_M = 90.0

#: Limite do enlace total, incluindo patch cords, em metros.
LIMITE_ENLACE_M = 100.0


@dataclass(frozen=True)
class Material:
    """Um componente de enlace com suas perdas por frequencia.

    A component with frequency-dependent loss figures.

    Atributos:
        nome: Identificador do material.
        tipo: Um de ``cabo``, ``patch_panel``, ``conector``, ``patch_cord``,
            ``divisor``.
        perda_db: Perda de insercao em dB, por frequencia, no comprimento
            de referencia da tabela.
        comprimento_ref_m: Comprimento ao qual ``perda_db`` se aplica.
    """

    nome: str
    tipo: str
    perda_db: dict[int, float]
    comprimento_ref_m: float = 100.0

    def perda_em(self, frequencia: int, comprimento_m: float) -> float:
        """Perda em dB para uma frequencia e um comprimento dados.

        Returns ``0.0`` quando a frequencia nao tem valor definido, para nao
        inventar numero onde a tabela nao diz nada.

        Returns ``0.0`` when the frequency has no defined value, so we never
        invent a number where the table is silent.
        """
        base = self.perda_db.get(frequencia)
        if base is None:
            return 0.0
        if self.tipo == "cabo":
            if self.comprimento_ref_m == 0:
                return base
            return base * (comprimento_m / self.comprimento_ref_m)
        return base


# --------------------------------------------------------------------------
# Cabos: perda de insercao maxima do canal, por 100 m (ISO/IEC 11801).
# --------------------------------------------------------------------------
CABOS: dict[str, Material] = {
    "5e": Material("Cat5e", "cabo", {100: 20.0}),
    "6": Material("Cat6", "cabo", {100: 20.7, 250: 26.6}),
    "6A": Material("Cat6A", "cabo", {100: 21.0, 250: 26.0, 500: 32.0}),
}

# --------------------------------------------------------------------------
# Componentes do canal. Perdas praticamente independentes do comprimento.
# --------------------------------------------------------------------------
COMPONENTES: dict[str, Material] = {
    "patch_panel": Material(
        "Patch panel", "patch_panel", {100: 1.0, 250: 1.3, 500: 1.8}
    ),
    "conector": Material(
        "Conector RJ45", "conector", {100: 1.1, 250: 1.5, 500: 2.0}
    ),
    "patch_cord": Material(
        "Patch cord", "patch_cord", {100: 1.2, 250: 1.6, 500: 2.2}
    ),
    "divisor": Material(
        "Divisor/splitter", "divisor", {100: 1.4, 250: 1.8, 500: 2.4}
    ),
}

# --------------------------------------------------------------------------
# NEXT e PS-NEXT: sao pisos (valores mais altos sao melhores), nao tetos.
# --------------------------------------------------------------------------
NEXT_MINIMO: dict[str, dict[int, float]] = {
    "5e": {100: 32.4},
    "6": {100: 41.8, 250: 38.6},
    "6A": {100: 44.4, 250: 41.4, 500: 39.1},
}

PS_NEXT_MINIMO: dict[str, dict[int, float]] = {
    "5e": {100: 27.4},
    "6": {100: 39.1, 250: 36.1},
    "6A": {100: 42.4, 250: 39.4, 500: 37.2},
}

#: Categoria cobre a banda ate esta frequencia.
FREQUENCIA_MAXIMA: dict[str, int] = {"5e": 100, "6": 250, "6A": 500}


@dataclass(frozen=True)
class CabosDisponiveis:
    """Vista publica das tabelas, para CLI e testes.

    Public view of the tables, for CLI and tests.
    """

    categorias: tuple[str, ...] = field(default=("5e", "6", "6A"))

    def frequencias(self, categoria: str) -> tuple[int, ...]:
        """Frequencias de avaliacao de uma categoria, em MHz.

        Evaluation frequencies for a category, in MHz.
        """
        return tuple(sorted(CABOS[categoria].perda_db.keys()))

    def suporta(self, categoria: str, frequencia: int) -> bool:
        """Se a categoria cobre a frequencia informada.

        Whether the category covers the given frequency.
        """
        return frequencia in CABOS[categoria].perda_db

    def next_piso(self, categoria: str, frequencia: int) -> float | None:
        """Piso de NEXT da categoria na frequencia, ou ``None``.

        NEXT floor for the category at that frequency, or ``None``.
        """
        return NEXT_MINIMO.get(categoria, {}).get(frequencia)

    def ps_next_piso(self, categoria: str, frequencia: int) -> float | None:
        """Piso de PS-NEXT da categoria na frequencia, ou ``None``.

        PS-NEXT floor for the category at that frequency, or ``None``.
        """
        return PS_NEXT_MINIMO.get(categoria, {}).get(frequencia)


CABOS_DISPONIVEIS = CabosDisponiveis()
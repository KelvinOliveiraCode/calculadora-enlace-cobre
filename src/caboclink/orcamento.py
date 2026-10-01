"""Orcamento de perda e classificacao de um enlace de cobre.

Insertion loss budget and classification of a copper link.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .perdas import (
    CABOS,
    CABOS_DISPONIVEIS,
    COMPONENTES,
    FREQUENCIA_MAXIMA,
    LIMITE_CANAL_M,
    LIMITE_ENLACE_M,
)

#: Classificacoes possiveis, da melhor para a pior.
APROVADO = "APROVADO"
APROVADO_COM_RESSALVA = "APROVADO COM RESSALVA"
REPROVADO = "REPROVADO"
INVIavel = "INVIAVEL"


@dataclass
class Enlace:
    """Um enlace de cobre a ser orcado.

    A copper link to be budgeted.

    Atributos:
        categoria: ``5e``, ``6`` ou ``6A``.
        comprimento_canal_m: Comprimento do cabo horizontal em metros.
        patch_cords: Quantidade de patch cords no caminho.
        conectores: Quantidade de conectores RJ45 no caminho.
        patch_panels: Quantidade de patch panels atravessados.
        divisor: Se ha divisor de sinal no caminho.
        frequencias: Frequencias a avaliar. Vazio usa as da categoria.
    """

    categoria: str = "6"
    comprimento_canal_m: float = 90.0
    patch_cords: int = 2
    conectores: int = 2
    patch_panels: int = 1
    divisor: bool = False
    frequencias: tuple[int, ...] = ()


@dataclass
class Resultado:
    """Resultado do orcamento de um enlace.

    Result of a link budget.

    Atributos:
        veredito: Classificacao final.
        detalhes: Uma linha por combinacao avaliada.
        avisos: Observacoes que nao mudam o veredito.
    """

    veredito: str = APROVADO
    detalhes: list[dict] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @property
    def aprovado(self) -> bool:
        """Se o enlace pode ser usado.

        Whether the link may be used.
        """
        return self.veredito in (APROVADO, APROVADO_COM_RESSALVA)

    def como_texto(self) -> str:
        """Saida tabular para o terminal.

        Tabular output for the terminal.
        """
        linhas = [
            f"{'FREQ':>6} {'ORCAMENTO':>10} {'LIMITE':>9} {'MARGEM':>9}  SITUACAO",
            f"{'-' * 6} {'-' * 10} {'-' * 9} {'-' * 9}  {'-' * 10}",
        ]
        for d in self.detalhes:
            if "parametro" in d:
                continue
            linhas.append(
                f"{d['frequencia']:>6} {d['orcamento_db']:>10.2f} "
                f"{d['limite_db']:>9.2f} {d['margem_db']:>9.2f}  {d['situacao']}"
            )
        if self.avisos:
            linhas.append("")
            linhas.append("Avisos / warnings:")
            linhas.extend(f"  - {a}" for a in self.avisos)
        linhas.append("")
        linhas.append(f"VEREDITO: {self.veredito}")
        return "\n".join(linhas)


def _perda_componentes(components: dict[str, int], frequencia: int) -> float:
    """Soma das perdas de componentes nao-cabo.

    Sum of non-cable component losses.
    """
    total = 0.0
    for nome, quantidade in components.items():
        material = COMPONENTES[nome]
        total += material.perda_em(frequencia, 0.0) * quantidade
    return total


def orcar(
    enlace: Enlace, margem_minima_db: float = 1.5
) -> Resultado:
    """Calcula o orcamento de perda e classifica o enlace.

    Calcula o orcamento de perda do enlace em cada frequencia e devolve o
    veredito. A regra de margem: se a folga para o limite for menor que
    ``margem_minima_db``, o veredito cai para "APROVADO COM RESSALVA" - porque
    um enlace que passa raspando no limite medido falha quando o ambiente muda.

    Compute the link loss budget and classify the link.

    Args:
        enlace: Descricao do enlace.
        margem_minima_db: Folga minima exigida contra o limite.

    Returns:
        O :class:`Resultado` com detalhes por frequencia e avisos.
    """
    resultado = Resultado()

    if enlace.categoria not in CABOS:
        raise ValueError(f"Categoria desconhecida: {enlace.categoria!r}")

    cabo = CABOS[enlace.categoria]
    componentes = {
        "patch_cord": enlace.patch_cords,
        "conector": enlace.conectores,
        "patch_panel": enlace.patch_panels,
    }
    if enlace.divisor:
        componentes["divisor"] = 1

    frequencias = enlace.frequencias or CABOS_DISPONIVEIS.frequencias(
        enlace.categoria
    )

    # Limites fisicos sao verificados antes de qualquer conta de perda.
    if enlace.comprimento_canal_m > LIMITE_CANAL_M:
        resultado.veredito = REPROVADO
        resultado.avisos.append(
            f"Canal com {enlace.comprimento_canal_m:.1f} m excede o limite "
            f"fisico de {LIMITE_CANAL_M:.0f} m."
        )
        return resultado

    comprimento_total = (
        enlace.comprimento_canal_m
        + enlace.patch_cords * 2.0
        + enlace.conectores * 0.3
    )
    if comprimento_total > LIMITE_ENLACE_M:
        resultado.veredito = REPROVADO
        resultado.avisos.append(
            f"Enlace total de {comprimento_total:.1f} m excede "
            f"{LIMITE_ENLACE_M:.0f} m."
        )
        return resultado

    pior_situacao = APROVADO
    _piorizar = {APROVADO: 0, APROVADO_COM_RESSALVA: 1, REPROVADO: 2}
    veredito = APROVADO

    for freq in sorted(frequencias):
        if not CABOS_DISPONIVEIS.suporta(enlace.categoria, freq):
            resultado.veredito = INVIavel
            resultado.avisos.append(
                f"{cabo.nome} nao especifica {freq} MHz "
                f"(maximo {FREQUENCIA_MAXIMA[enlace.categoria]} MHz)."
            )
            return resultado

        perda_cabo = cabo.perda_em(freq, enlace.comprimento_canal_m)
        perda_comp = _perda_componentes(componentes, freq)
        orcamento = perda_cabo + perda_comp
        limite = cabo.perda_db[freq]
        margem = limite - orcamento

        if margem < 0:
            situacao = REPROVADO
            veredito = REPROVADO
        elif margem < margem_minima_db:
            situacao = APROVADO_COM_RESSALVA
            if _piorizar[APROVADO_COM_RESSALVA] > _piorizar[veredito]:
                veredito = APROVADO_COM_RESSALVA
        else:
            situacao = APROVADO

        if _piorizar[situacao] > _piorizar[pior_situacao]:
            pior_situacao = situacao

        resultado.detalhes.append(
            {
                "frequencia": freq,
                "orcamento_db": round(orcamento, 2),
                "limite_db": round(limite, 2),
                "margem_db": round(margem, 2),
                "situacao": situacao,
                "perda_cabo_db": round(perda_cabo, 2),
                "perda_componentes_db": round(perda_comp, 2),
            }
        )

    resultado.veredito = veredito

    # NEXT e PS-NEXT sao pisos: se nem a tabela define, nao inventamos.
    for freq in sorted(frequencias):
        piso = CABOS_DISPONIVEIS.next_piso(enlace.categoria, freq)
        if piso is None:
            continue
        perda_total = next(
            (d["orcamento_db"] for d in resultado.detalhes if d["frequencia"] == freq),
            0.0,
        )
        # NEXT nao se soma a perda de insercao. E um par a par. O que importa
        # aqui e so registrar o piso aplicavel como contexto do laudo.
        resultado.detalhes.append(
            {
                "frequencia": freq,
                "parametro": "NEXT",
                "piso_db": round(piso, 2),
                "orcamento_db": round(perda_total, 2),
                "situacao": "CONTEXTO",
            }
        )

    if veredito == APROVADO_COM_RESSALVA:
        resultado.avisos.append(
            f"Margem menor que {margem_minima_db} dB em ao menos uma "
            f"frequencia. Passe com folga maior antes de instalar."
        )

    return resultado
"""Geracao do laudo de certificacao no formato de equipamento.

Certification report generation in equipment output format.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .orcamento import APROVADO, Enlace, Resultado


@dataclass
class Laudo:
    """Dados do laudo a emitir.

    Data of the report to emit.
    """

    enlace: Enlace
    resultado: Resultado
    gerado_em: datetime
    equipamento: str = "Certificador de cabo (simulado)"
    operador: str = "caboclink"

    def como_markdown(self) -> str:
        """Monta o laudo em Markdown.

        Build the report as Markdown.
        """
        e = self.enlace
        r = self.resultado
        marca = "PASS" if r.aprovado else "FAIL"
        detalhe_perda = [d for d in r.detalhes if "parametro" not in d]

        linhas = [
            "# Laudo de certificacao de enlace de cobre",
            "",
            "| Campo | Valor |",
            "|---|---|",
            f"| Equipamento | {self.equipamento} |",
            f"| Operador | {self.operador} |",
            f"| Gerado em | {self.gerado_em.astimezone().strftime('%Y-%m-%d %H:%M:%S %z')} |",
            f"| Categoria | {e.categoria} |",
            f"| Comprimento do canal | {e.comprimento_canal_m:.2f} m |",
            f"| Patch cords | {e.patch_cords} |",
            f"| Conectores | {e.conectores} |",
            f"| Patch panels | {e.patch_panels} |",
            f"| Divisor | {'sim' if e.divisor else 'nao'} |",
            f"| **Veredito** | **{marca} - {r.veredito}** |",
            "",
            "## Resultados por frequencia",
            "",
            "| Freq (MHz) | Orcamento (dB) | Limite (dB) | Margem (dB) | Situacao |",
            "|---:|---:|---:|---:|---|",
        ]
        for d in detalhe_perda:
            linhas.append(
                f"| {d['frequencia']} | {d['orcamento_db']:.2f} | "
                f"{d['limite_db']:.2f} | {d['margem_db']:.2f} | {d['situacao']} |"
            )

        pisos = [d for d in r.detalhes if d.get("parametro") == "NEXT"]
        if pisos:
            linhas += [
                "",
                "## Pisos de acoplamento (referencia)",
                "",
                "| Freq (MHz) | Parametro | Piso (dB) |",
                "|---:|---|---:|",
            ]
            for d in pisos:
                linhas.append(
                    f"| {d['frequencia']} | {d['parametro']} | {d['piso_db']:.2f} |"
                )

        linhas += ["", "## Comprovacao manual", ""]
        linhas += self._conferencia_manual()

        if r.avisos:
            linhas += ["", "## Avisos", ""]
            linhas += [f"- {a}" for a in r.avisos]

        linhas += [
            "",
            "---",
            "",
            "> Simulacao deterministica. Nao substitui medicao com equipamento "
            "de certificacao real.",
        ]
        return "\n".join(linhas)

    def _conferencia_manual(self) -> list[str]:
        """Detalha a conta para conferencia manual do resultado.

        Detail the arithmetic so a human can check it by hand.
        """
        linhas: list[str] = []
        for d in self.resultado.detalhes:
            if "parametro" in d:
                continue
            linhas.append(
                f"- **{d['frequencia']} MHz**: cabo {d['perda_cabo_db']:.2f} dB "
                f"+ componentes {d['perda_componentes_db']:.2f} dB = "
                f"{d['orcamento_db']:.2f} dB, contra limite de "
                f"{d['limite_db']:.2f} dB. Margem {d['margem_db']:.2f} dB."
            )
        return linhas


def gerar_laudo(enlace: Enlace, resultado: Resultado) -> Laudo:
    """Cria o laudo para um enlace e seu resultado.

    Create the report for a link and its result.

    Args:
        enlace: Enlace avaliado.
        resultado: Resultado devolvido por :func:`caboclink.orcamento.orcar`.

    Returns:
        O :class:`Laudo` pronto para :meth:`Laudo.como_markdown`.
    """
    return Laudo(
        enlace=enlace,
        resultado=resultado,
        gerado_em=datetime.now(timezone.utc),
    )
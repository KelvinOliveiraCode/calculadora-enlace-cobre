"""CLI do caboclink - calculadora de enlace de cobre.

CLI entry point for caboclink.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cargador import carregar_enlace, carregar_materiais
from .certificacao import gerar_laudo
from .orcamento import APROVADO, INVIavel, REPROVADO, orcar
from .perdas import CABOS, CABOS_DISPONIVEIS, COMPONENTES


def _cmd_materiais(_args: argparse.Namespace) -> int:
    """Lista as categorias e componentes disponiveis.

    List available categories and components.
    """
    print("Categorias de cabo / cable categories:")
    for chave, mat in CABOS.items():
        freqs = ", ".join(f"{f} MHz" for f in CABOS_DISPONIVEIS.frequencias(chave))
        print(f"  {chave:<4} {mat.nome:<8} {freqs}")
    print()
    print("Componentes / components:")
    for chave, mat in COMPONENTES.items():
        freqs = ", ".join(f"{f} MHz" for f in sorted(mat.perda_db))
        print(f"  {chave:<14} {mat.nome:<16} {freqs}")
    return 0


def _cmd_orcamento(args: argparse.Namespace) -> int:
    """Executa o orcamento de um enlace.

    Run a link budget.
    """
    enlace = carregar_enlace(args.enlace)
    resultado = orcar(enlace, margem_minima_db=args.margem)

    print(resultado.como_texto())

    if args.laudo:
        caminho = Path(args.laudo)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        laudo = gerar_laudo(enlace, resultado)
        caminho.write_text(laudo.como_markdown(), encoding="utf-8")
        print(f"Laudo gravado em: {caminho}")

    if resultado.veredito in (REPROVADO, INVIavel):
        return 1
    return 0


def _cmd_inspecionar(args: argparse.Namespace) -> int:
    """Mostra a tabela de perdas de uma categoria.

    Show the loss table for a category.
    """
    if args.categoria not in CABOS:
        print(
            f"Categoria invalida / invalid category: {args.categoria!r}. "
            f"Use uma de: {', '.join(CABOS)}",
            file=sys.stderr,
        )
        return 2
    dados = carregar_materiais(args.materiais) if args.materiais else {}
    if dados:
        print(f"Fonte / source: {args.materiais}")
        print()
    mat = CABOS[args.categoria]
    print(f"{mat.nome} - perda de insercao maxima por 100 m")
    for freq in CABOS_DISPONIVEIS.frequencias(args.categoria):
        piso_next = CABOS_DISPONIVEIS.next_piso(args.categoria, freq)
        piso_ps = CABOS_DISPONIVEIS.ps_next_piso(args.categoria, freq)
        print(
            f"  {freq:>4} MHz   insercao {mat.perda_db[freq]:>5.2f} dB   "
            f"NEXT >= {piso_next:.2f} dB   PS-NEXT >= {piso_ps:.2f} dB"
        )
    return 0


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos.

    Build the argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="caboclink",
        description=(
            "Calcula e valida orcamento de perda de enlace de cobre. "
            "Calculates and validates copper link loss budget."
        ),
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_orc = sub.add_parser(
        "orcamento",
        help="Orcamenta um enlace a partir de um YAML.",
    )
    p_orc.add_argument("enlace", help="Caminho do YAML do enlace.")
    p_orc.add_argument("--laudo", help="Grava laudo Markdown neste caminho.")
    p_orc.add_argument(
        "--margem",
        type=float,
        default=1.5,
        help="Folga minima em dB antes de marcar ressalva (default 1.5).",
    )
    p_orc.set_defaults(func=_cmd_orcamento)

    p_mat = sub.add_parser("materiais", help="Lista categorias e componentes.")
    p_mat.set_defaults(func=_cmd_materiais)

    p_ins = sub.add_parser("inspecionar", help="Mostra tabela de perdas.")
    p_ins.add_argument("categoria", help="5e, 6 ou 6A.")
    p_ins.add_argument("--materiais", help="YAML de catalogo (opcional).")
    p_ins.set_defaults(func=_cmd_inspecionar)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI.

    CLI entry point.
    """
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError) as exc:
        print(f"Erro / error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
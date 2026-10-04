"""Confere o encoding dos arquivos de texto do repositório.

Varre cada arquivo de texto da raiz e recusa três coisas: BOM UTF-8 no
início do arquivo, caractere de substituição U+FFFD e ideograma CJK.
Nenhum dos três pertence a um arquivo limpo; se um aparecer, a varredura
falha com exit code 1.
"""

from __future__ import annotations

import sys
from pathlib import Path

#: Raiz do repositório.
RAIZ = Path(__file__).resolve().parent.parent

#: Extensões varridas. Binários ficam de propósito fora.
EXTENSOES = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".ps1",
}

#: Diretories que a varredura ignora.
IGNORAR_DIRETORIOS = {
    ".git", "__pycache__", ".pytest_cache", ".coverage",
}

#: Extensões binárias que a varredura ignora.
IGNORAR_EXTENSOES = {".png", ".jpg", ".mp4", ".woff", ".woff2"}

#: Intervalo de ideogramas CJK.
CJK = range(0x3000, 0x9FFF + 1)

#: Caractere de substituição.
SUBSTITUICAO = 0xFFFD

#: BOM do UTF-8 em bytes.
BOM_BYTES = b"\xef\xbb\xbf"


def varrer(raiz: Path = RAIZ) -> tuple[list[tuple[str, int, str]], int]:
    """Procura arquivo de texto com encoding inválido.

    Args:
        raiz: Diretório a varrer.

    Returns:
        Tupla ``(problemas, conferidos)``; cada problema é
        ``(caminho, linha, motivo)``.
    """
    problemas: list[tuple[str, int, str]] = []
    conferidos = 0
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file():
            continue
        if any(parte in IGNORAR_DIRETORIOS for parte in caminho.parts):
            continue
        sufixo = caminho.suffix.lower()
        if sufixo in IGNORAR_EXTENSOES or sufixo not in EXTENSOES:
            continue
        conferidos += 1
        onde = str(caminho.relative_to(raiz))
        bruto = caminho.read_bytes()
        if bruto.startswith(BOM_BYTES):
            problemas.append((onde, 1, "BOM UTF-8 no inicio do arquivo"))
            continue
        try:
            texto = bruto.decode("utf-8")
        except UnicodeDecodeError as exc:
            problemas.append((onde, 0, f"nao decodifica como UTF-8: {exc}"))
            continue
        for numero, linha in enumerate(texto.splitlines(), 1):
            for caractere in linha:
                ponto = ord(caractere)
                if ponto == SUBSTITUICAO:
                    problemas.append((
                        onde, numero,
                        "caractere de substituicao U+FFFD",
                    ))
                    break
                if ponto in CJK:
                    problemas.append((
                        onde, numero,
                        f"ideograma CJK U+{ponto:04X}",
                    ))
                    break
    return problemas, conferidos


def main() -> int:
    """Executa a varredura e reporta.
    """
    problemas, conferidos = varrer()
    if not problemas:
        print(f"encoding ok: {conferidos} arquivo(s) conferido(s)")
        return 0
    print(
        f"encoding FALHOU: {len(problemas)} ocorrencia(s) em "
        f"{conferidos} arquivo(s) conferido(s)"
    )
    for caminho, linha, motivo in problemas:
        onde = f"{caminho}:{linha}" if linha else caminho
        print(f"  {onde}: {motivo}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

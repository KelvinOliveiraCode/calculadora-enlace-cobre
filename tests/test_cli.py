"""Testes da CLI e do carregamento de arquivos.

Tests for the CLI and file loading.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from caboclink.cargador import carregar_enlace, carregar_materiais
from caboclink.cli import main
from caboclink.orcamento import APROVADO, REPROVADO

DADOS = Path(__file__).resolve().parents[1] / "dados"


class TestCarregamentoMateriais:
    """Leitura do catalogo."""

    def test_le_catalogo_completo(self) -> None:
        dados = carregar_materiais(DADOS / "materiais.yaml")
        assert "cabos" in dados
        assert "componentes" in dados

    def test_catalogo_tem_tres_categorias(self) -> None:
        dados = carregar_materiais(DADOS / "materiais.yaml")
        assert set(dados["cabos"]) == {"5e", "6", "6A"}

    def test_yaml_invalido_levanta_erro(self) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write("- apenas\n- uma\n- lista\n")
            caminho = Path(fh.name)
        with pytest.raises(ValueError, match="mapeamento"):
            carregar_materiais(caminho)
        caminho.unlink()

    def test_arquivo_inexistente_levanta_oserror(self) -> None:
        with pytest.raises(OSError):
            carregar_materiais(DADOS / "nao-existe.yaml")


class TestCarregamentoEnlace:
    """Leitura do arquivo de enlace."""

    def test_le_enlace_de_exemplo(self) -> None:
        enlace = carregar_enlace(DADOS / "exemplo-enlace.yaml")
        assert enlace.categoria == "6"
        assert enlace.comprimento_canal_m == 45.0
        assert enlace.frequencias == (100, 250)

    def test_frequencias_vazias_viram_tupla_vazia(self) -> None:
        enlace = carregar_enlace(DADOS / "exemplo-enlace.yaml")
        assert isinstance(enlace.frequencias, tuple)

    def test_comprimento_negativo_rejeitado(self) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write("categoria: '6'\ncomprimento_canal_m: -5\n")
            caminho = Path(fh.name)
        with pytest.raises(ValueError, match="negativo"):
            carregar_enlace(caminho)
        caminho.unlink()

    def test_valores_padrao_sao_aplicados(self) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write("categoria: '6'\n")
            caminho = Path(fh.name)
        enlace = carregar_enlace(caminho)
        assert enlace.patch_cords == 2
        assert enlace.conectores == 2
        caminho.unlink()


class TestCLIMateriais:
    """Subcomando materiais."""

    def test_lista_categorias(self, capsys) -> None:
        assert main(["materiais"]) == 0
        saida = capsys.readouterr().out
        assert "Cat6A" in saida

    def test_lista_componentes(self, capsys) -> None:
        main(["materiais"])
        assert "patch_panel" in capsys.readouterr().out


class TestCLIInspecionar:
    """Subcomando inspecionar."""

    def test_categoria_valida_retorna_zero(self, capsys) -> None:
        assert main(["inspecionar", "6A"]) == 0
        assert "500" in capsys.readouterr().out

    def test_categoria_invalida_retorna_dois(self, capsys) -> None:
        assert main(["inspecionar", "8"]) == 2
        assert "invalid category" in capsys.readouterr().err

    def test_mostra_pisos_next(self, capsys) -> None:
        main(["inspecionar", "6"])
        assert "PS-NEXT" in capsys.readouterr().out


class TestCLIOrcamento:
    """Subcomando orcamento."""

    def test_enlace_valido_retorna_zero(self, capsys) -> None:
        codigo = main(["orcamento", str(DADOS / "exemplo-enlace.yaml")])
        assert codigo == 0
        assert "APROVADO" in capsys.readouterr().out

    def test_enlace_com_ressalva_ainda_retorna_zero(self, capsys) -> None:
        codigo = main(
            ["orcamento", str(DADOS / "exemplo-enlace.yaml"), "--margem", "12"]
        )
        assert codigo == 0

    def test_enlace_reprovado_retorna_um(self, capsys) -> None:
        codigo = main(["orcamento", str(DADOS / "enlace-longo-cat5e.yaml")])
        assert codigo == 1
        assert "REPROVADO" in capsys.readouterr().out

    def test_grava_laudo(self, capsys, tmp_path) -> None:
        destino = tmp_path / "laudo.md"
        codigo = main(
            ["orcamento", str(DADOS / "exemplo-enlace.yaml"), "--laudo", str(destino)]
        )
        assert codigo == 0
        assert destino.exists()
        assert "Laudo de certificacao" in destino.read_text(encoding="utf-8")

    def test_laudo_contem_conferencia_manual(self, tmp_path) -> None:
        destino = tmp_path / "laudo.md"
        main(["orcamento", str(DADOS / "exemplo-enlace.yaml"), "--laudo", str(destino)])
        texto = destino.read_text(encoding="utf-8")
        assert "Conferencia manual" in texto or "Comprovacao manual" in texto

    def test_arquivo_inexistente_retorna_dois(self, capsys) -> None:
        codigo = main(["orcamento", str(DADOS / "nao-existe.yaml")])
        assert codigo == 2
        assert "Erro" in capsys.readouterr().err


class TestCLIHelp:
    """Toda CLI precisa de --help."""

    def test_help_raiz(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_help_orcamento(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["orcamento", "--help"])
        assert exc.value.code == 0

    def test_sem_subcomando_falha(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code != 0

    def test_help_menciona_bilingue(self) -> None:
        with pytest.raises(SystemExit):
            main(["--help"])
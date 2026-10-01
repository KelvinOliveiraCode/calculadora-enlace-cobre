"""Testes do orcamento de perda e da classificacao.

Tests for the loss budget and classification.
"""

from __future__ import annotations

import pytest

from caboclink.orcamento import (
    APROVADO,
    APROVADO_COM_RESSALVA,
    INVIavel,
    REPROVADO,
    Enlace,
    orcar,
)
from caboclink.perdas import LIMITE_CANAL_M


def _por_freq(resultado, freq):
    """Achata o detalhe de uma frequencia."""
    return next(d for d in resultado.detalhes if d["frequencia"] == freq and "parametro" not in d)


class TestEnlaceCurtoAprovado:
    """Enlace curto e limpo passa com folga."""

    def test_cat6_10m_aprova(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=10.0))
        assert r.veredito == APROVADO
        assert r.aprovado is True

    def test_margem_e_positiva_em_toda_frequencia(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=10.0))
        for d in r.detalhes:
            if "parametro" not in d:
                assert d["margem_db"] > 0

    def test_curto_tem_margem_maior_que_longo(self) -> None:
        curto = _por_freq(orcar(Enlace("6", 10.0)), 100)
        longo = _por_freq(orcar(Enlace("6", 80.0)), 100)
        assert curto["margem_db"] > longo["margem_db"]


class TestCategoriaInvalida:
    """Categoria fora da tabela e erro explicito."""

    def test_categoria_desconhecida_levanta_valueerror(self) -> None:
        with pytest.raises(ValueError, match="Categoria desconhecida"):
            orcar(Enlace("8"))

    def test_mensagem_e_bilingue_na_pratica(self) -> None:
        with pytest.raises(ValueError) as exc:
            orcar(Enlace("X"))
        assert "Categoria desconhecida" in str(exc.value)


class TestLimiteFisicoCanal:
    """Acima de 90 m de canal o enlace reprova sem conta de perda."""

    def test_exatamente_90m_ainda_avalia(self) -> None:
        r = orcar(Enlace("6A", comprimento_canal_m=LIMITE_CANAL_M))
        assert r.veredito != REPROVADO or "limite fisico" not in " ".join(r.avisos)

    def test_acima_de_90m_reprova(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=91.0))
        assert r.veredito == REPROVADO
        assert any("limite fisico" in a for a in r.avisos)

    def test_150m_reprova_com_valor_citado(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=150.0))
        assert r.veredito == REPROVADO
        assert "150.0 m" in r.avisos[0]

    def test_reprovacao_fisica_nao_calcula_perda(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=200.0))
        assert r.detalhes == []


class TestLimiteFisicoEnlaceTotal:
    """O total do enlace tambem tem teto."""

    def test_total_acima_de_100m_reprova(self) -> None:
        # 88 m de canal (dentro do limite de 90) + 6 patch cords de 2 m cada.
        # Total = 88 + 12 + 0,6 = 100,6 m, acima do teto de enlace.
        r = orcar(Enlace("6", comprimento_canal_m=88.0, patch_cords=6))
        assert r.veredito == REPROVADO
        assert any("Enlace total" in a for a in r.avisos)

    def test_canal_dentro_do_limite_nao_dispara_aviso_de_canal(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=88.0, patch_cords=6))
        assert not any("limite fisico" in a for a in r.avisos)


class TestFrequenciaForaDeSpec:
    """Frequencia acima da categoria e inviavel."""

    def test_500mhz_em_cat5e_e_inviavel(self) -> None:
        r = orcar(Enlace("5e", frequencias=(500,)))
        assert r.veredito == INVIavel

    def test_aviso_cita_o_maximo_da_categoria(self) -> None:
        r = orcar(Enlace("5e", frequencias=(250,)))
        assert any("100 MHz" in a for a in r.avisos)

    def test_inviavel_nao_aprovado(self) -> None:
        r = orcar(Enlace("5e", frequencias=(500,)))
        assert r.aprovado is False


class TestMargemRessalva:
    """Folga pequena demais vira ressalva."""

    def test_margem_minima_zero_aprova_quando_ha_folga(self) -> None:
        # Com folga minima 0, qualquer folga positiva aprova.
        r = orcar(Enlace("6", comprimento_canal_m=45.0), margem_minima_db=0.0)
        assert r.veredito == APROVADO

    def test_margem_minima_alta_forca_ressalva(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=70.0), margem_minima_db=10.0)
        assert r.veredito == APROVADO_COM_RESSALVA
        assert r.aprovado is True

    def test_ressalva_gera_aviso(self) -> None:
        r = orcar(Enlace("6", comprimento_canal_m=70.0), margem_minima_db=10.0)
        assert any("Margem menor" in a for a in r.avisos)


class TestReprovacaoPorPerda:
    """Orcamento acima do limite reprova."""

    def test_cat5e_88m_com_divisor_reprova_em_100mhz(self) -> None:
        r = orcar(Enlace("5e", comprimento_canal_m=88.0, divisor=True))
        assert r.veredito == REPROVADO

    def test_margem_negativa_no_detalhe(self) -> None:
        r = orcar(Enlace("5e", comprimento_canal_m=88.0, divisor=True))
        assert _por_freq(r, 100)["margem_db"] < 0

    def test_orcamento_excede_limite(self) -> None:
        r = orcar(Enlace("5e", comprimento_canal_m=88.0, divisor=True))
        d = _por_freq(r, 100)
        assert d["orcamento_db"] > d["limite_db"]


class TestComponentesContribuem:
    """Cada componente adicional piora o orcamento."""

    def test_mais_patch_cords_aumenta_perda(self) -> None:
        base = _por_freq(orcar(Enlace("6", 50.0, patch_cords=2)), 100)
        mais = _por_freq(orcar(Enlace("6", 50.0, patch_cords=4)), 100)
        assert mais["orcamento_db"] > base["orcamento_db"]

    def test_divisor_aumenta_perda(self) -> None:
        base = _por_freq(orcar(Enlace("6", 50.0, divisor=False)), 100)
        com = _por_freq(orcar(Enlace("6", 50.0, divisor=True)), 100)
        assert com["orcamento_db"] > base["orcamento_db"]

    def test_patch_panel_aumenta_perda(self) -> None:
        base = _por_freq(orcar(Enlace("6", 50.0, patch_panels=0)), 100)
        dois = _por_freq(orcar(Enlace("6", 50.0, patch_panels=2)), 100)
        assert dois["orcamento_db"] > base["orcamento_db"]


class TestCategoriaMelhorPiora:
    """Subir de categoria melhora a margem."""

    def test_6a_tem_margem_maior_que_5e(self) -> None:
        cat5e = _por_freq(orcar(Enlace("5e", 50.0)), 100)
        cat6a = _por_freq(orcar(Enlace("6A", 50.0)), 100)
        assert cat6a["margem_db"] > cat5e["margem_db"]


class TestDeterminismo:
    """Mesma entrada, mesma saida."""

    def test_dois_calculos_identicos(self) -> None:
        a = orcar(Enlace("6", 45.0, patch_cords=2, conectores=2))
        b = orcar(Enlace("6", 45.0, patch_cords=2, conectores=2))
        assert a.veredito == b.veredito
        assert a.detalhes == b.detalhes

    def test_ordem_das_frequencias_nao_importa(self) -> None:
        a = orcar(Enlace("6A", 40.0, frequencias=(500, 100, 250)))
        b = orcar(Enlace("6A", 40.0, frequencias=(100, 250, 500)))
        assert a.detalhes == b.detalhes


class TestSaidaTexto:
    """A tabela textual contem o veredito."""

    def test_texto_tem_veredito(self) -> None:
        assert "VEREDITO" in orcar(Enlace("6", 10.0)).como_texto()

    def test_texto_lista_frequencias(self) -> None:
        texto = orcar(Enlace("6A", 30.0)).como_texto()
        assert "100" in texto and "250" in texto and "500" in texto
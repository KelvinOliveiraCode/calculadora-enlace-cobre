"""Testes das tabelas de perda.

Tests for the loss tables.
"""

from __future__ import annotations

import pytest

from caboclink.perdas import (
    CABOS,
    CABOS_DISPONIVEIS,
    COMPONENTES,
    FREQUENCIA_MAXIMA,
    LIMITE_CANAL_M,
    LIMITE_ENLACE_M,
    Material,
)


class TestLimitesFisicos:
    """Os limites de comprimento nao mudam com categoria."""

    def test_limite_canal_e_90m(self) -> None:
        assert LIMITE_CANAL_M == 90.0

    def test_limite_enlace_e_100m(self) -> None:
        assert LIMITE_ENLACE_M == 100.0


class TestTabelaCabos:
    """Cobertura e coerencia da tabela de cabos."""

    def test_existe_5e_6_e_6a(self) -> None:
        assert set(CABOS) == {"5e", "6", "6A"}

    def test_cada_categoria_tem_500_apenas_em_6a(self) -> None:
        com_500 = [k for k, m in CABOS.items() if 500 in m.perda_db]
        assert com_500 == ["6A"]

    def test_frequencia_maxima_bate_com_tabela(self) -> None:
        for chave, mat in CABOS.items():
            assert max(mat.perda_db) == FREQUENCIA_MAXIMA[chave]

    def test_perda_cresce_com_frequencia(self) -> None:
        for mat in CABOS.values():
            freqs = sorted(mat.perda_db)
            valores = [mat.perda_db[f] for f in freqs]
            assert valores == sorted(valores), f"{mat.nome} fora de ordem"

    def test_next_cai_com_frequencia(self) -> None:
        for chave in CABOS:
            pisos = CABOS_DISPONIVEIS.next_piso(chave, 100)
            if chave == "6A":
                assert pisos > CABOS_DISPONIVEIS.next_piso(chave, 500)


class TestMaterialPerdaEm:
    """Escala de perda por comprimento."""

    def test_cabo_100m_usa_tabela_direta(self) -> None:
        cabo = CABOS["6"]
        assert cabo.perda_em(100, 100.0) == pytest.approx(20.7)

    def test_cabo_escala_linearmente(self) -> None:
        cabo = CABOS["6"]
        assert cabo.perda_em(100, 50.0) == pytest.approx(20.7 / 2)

    def test_componente_ignora_comprimento(self) -> None:
        painel = COMPONENTES["patch_panel"]
        assert painel.perda_em(100, 0.0) == pytest.approx(1.0)
        assert painel.perda_em(100, 90.0) == pytest.approx(1.0)

    def test_frequencia_desconhecida_retorna_zero(self) -> None:
        cabo = CABOS["5e"]
        assert cabo.perda_em(500, 90.0) == 0.0

    def test_comprimento_zero_retorna_zero_para_cabo(self) -> None:
        assert CABOS["6"].perda_em(100, 0.0) == 0.0


class TestSuporte:
    """Consulta de suporte por categoria."""

    def test_5e_nao_suporta_250(self) -> None:
        assert CABOS_DISPONIVEIS.suporta("5e", 250) is False

    def test_6_suporta_250(self) -> None:
        assert CABOS_DISPONIVEIS.suporta("6", 250) is True

    def test_6A_suporta_500(self) -> None:
        assert CABOS_DISPONIVEIS.suporta("6A", 500) is True

    def test_categoria_desconhecida_levanta_keyerror(self) -> None:
        with pytest.raises(KeyError):
            CABOS_DISPONIVEIS.frequencias("8")


class TestPisos:
    """NEXT e PS-NEXT tem piso para toda frequencia da categoria."""

    def test_piso_next_existe_para_toda_frequencia(self) -> None:
        for chave in CABOS:
            for freq in CABOS_DISPONIVEIS.frequencias(chave):
                assert CABOS_DISPONIVEIS.next_piso(chave, freq) is not None

    def test_ps_next_always_menor_que_next(self) -> None:
        for chave in CABOS:
            for freq in CABOS_DISPONIVEIS.frequencias(chave):
                assert (
                    CABOS_DISPONIVEIS.ps_next_piso(chave, freq)
                    < CABOS_DISPONIVEIS.next_piso(chave, freq)
                )

    def test_piso_inexistente_retorna_none(self) -> None:
        assert CABOS_DISPONIVEIS.next_piso("5e", 500) is None
        assert CABOS_DISPONIVEIS.ps_next_piso("5e", 250) is None


class TestMaterialDataclass:
    """Construcao direta de Material."""

    def test_material_personalizado(self) -> None:
        m = Material("X", "cabo", {100: 10.0}, comprimento_ref_m=50.0)
        assert m.perda_em(100, 100.0) == pytest.approx(20.0)

    def test_referencia_zero_evita_divisao(self) -> None:
        m = Material("Y", "cabo", {100: 5.0}, comprimento_ref_m=0.0)
        assert m.perda_em(100, 10.0) == pytest.approx(5.0)
<div align="center">

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/testes-72%20passing-brightgreen?style=flat-square" alt="Testes">
  <img src="https://img.shields.io/badge/cobertura-97%25-brightgreen?style=flat-square" alt="Cobertura">
  <img src="https://img.shields.io/badge/licenca-MIT-yellow?style=flat-square" alt="Licenca">
</p>

# calculadora-enlace-cobre

**Orçamento de perda de inserção e laudo de certificação para enlace de cabeamento estruturado em cobre, feito para rodar antes de puxar o cabo.**

</div>

---

## Problema / Por que existe

Perda de inserção calculada errada é a causa mais comum de link instável após a instalação. O limite da ISO/IEC 11801 vale para o canal inteiro — cabo horizontal, conectores, patch panel e patch cords — e quase toda planilha compara apenas o cabo contra o limite. O resultado é um enlace que "aprova" no papel e falha em campo, depois de puxar o cabo e subir no teto.

O projeto nasceu vendo esse cálculo feito de cabeça em planejamento de infraestrutura. O valor da ferramenta não está no número final: está em mostrar a conta aberta para que qualquer pessoa confira à mão, e em declarar explicitamente o que o modelo não cobre.

## O que faz

A CLI `caboclink` lê um YAML que descreve o enlace (categoria, comprimento do canal horizontal e quantidades de patch cords, conectores, patch panels e divisor opcional) e:

1. Soma a perda do cabo (escala linear com o comprimento) com a perda de cada componente, por frequência.
2. Compara o total com o limite da categoria em cada frequência avaliada (100 MHz, 250 MHz e 500 MHz, segundo a categoria).
3. Classifica: APROVADO, APROVADO COM RESSALVA (margem menor que 1,5 dB), REPROVADO (orçamento acima do limite ou limites físicos excedidos) ou INVIAVEL (frequência acima da categoria).
4. Emite, opcionalmente, um laudo Markdown com a conta aberta (cabo + componentes = total, contra o limite) e os pisos NEXT/PS-NEXT da categoria como referência.

Códigos de saída: 0 aprovado ou ressalva, 1 reprovado ou inviável, 2 erro de entrada (arquivo inexistente ou inválido).

## Stack

- Python 3.10 ou superior
- PyYAML 6.0 ou superior (única dependência de runtime)
- pytest e pytest-cov (dev)
- Executa offline, sem dependência de rede ou de equipamento de certificação

## Como funciona

- Perda do cabo: valor da tabela da categoria multiplicado por `comprimento / 100`. Exemplo: Cat6 a 45 m em 100 MHz = 20,70 × 0,45 = 9,31 dB.
- Componentes (patch cord, conector, patch panel, divisor) somam o valor fixo da tabela por frequência, independentemente do comprimento.
- Limites físicos são verificados antes de qualquer conta: canal acima de 90 m reprova; enlace total (canal + 2 m por patch cord + 0,3 m por conector) acima de 100 m reprova.
- Frequência acima da categoria retorna INVIAVEL, não REPROVADO: sinal inválido não é o mesmo que perda alta.
- Margem = limite menos orçamento. Margem negativa reprova; margem positiva abaixo de 1,5 dB vira APROVADO COM RESSALVA.
- NEXT e PS-NEXT são pisos de acoplamento, não perdas: aparecem apenas como referência no laudo, nunca somados ao orçamento de perda.
- Determinístico: mesma entrada produz sempre a mesma saída.

## Como rodar

```powershell
# 1. Instalar
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

# 2. Validar
python -m pytest tests/ -q

# 3. Executar (enlace válido: Cat6, 45 m, 100 e 250 MHz)
python -m caboclink orcamento dados/exemplo-enlace.yaml
```

Saída real:

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      14.91     20.70      5.79  APROVADO
   250      19.47     26.60      7.13  APROVADO

VEREDITO: APROVADO
```

Enlace reprovado (Cat5e a 88 m com divisor), código de saída 1:

```powershell
python -m caboclink orcamento dados/enlace-longo-cat5e.yaml
```

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      24.60     20.00     -4.60  REPROVADO

VEREDITO: REPROVADO
```

Outros comandos:

```powershell
python -m caboclink materiais                  # lista categorias e componentes
python -m caboclink inspecionar 6A             # tabela de perdas da categoria
python -m caboclink orcamento dados/exemplo-enlace.yaml --laudo exemplos/laudo-exemplo.md
python -m caboclink orcamento dados/exemplo-enlace.yaml --margem 12   # exige folga de 12 dB
```

O laudo inclui a seção "Comprovacao manual", com uma linha por frequência mostrando cabo, componentes, total, limite e margem.

## Estrutura do projeto

```
src/caboclink/
  __main__.py      ponto de entrada (`python -m caboclink`)
  cli.py           parser de argumentos e subcomandos (orcamento, materiais, inspecionar)
  cargador.py      leitura de YAML de enlace e catalogo de materiais
  perdas.py        tabelas de perda por categoria e frequencia, limites fisicos, pisos NEXT/PS-NEXT
  orcamento.py     modelos Enlace e Resultado, funcao orcar() e regras de veredito
  certificacao.py  geracao do laudo Markdown
dados/             catalogo de materiais (materiais.yaml) e enlaces de exemplo
docs/              tabela de perdas e guia de leitura de ficha tecnica
exemplos/          saidas reais geradas pela ferramenta
tests/             72 testes
pyproject.toml     configuracao do pacote (setuptools, pytest)
requirements.txt   dependencias (PyYAML, pytest, pytest-cov)
LICENSE            MIT
README.md
```

## Trade-offs e decisoes

- Perda escala linear com o comprimento: simples e previsível, aceitável em baixa frequência; acelera perto do limite da categoria, e a ferramenta não modela efeito de pele.
- Limites físicos são verificados antes de qualquer conta: não se inventa orçamento para um enlace fisicamente impossível.
- INVIAVEL separado de REPROVADO: frequência acima da categoria é sinal inválido, não perda alta; misturar os dois leva a trocar patch cord quando o problema é a categoria.
- Margem mínima de 1,5 dB por padrão: um enlace que passa raspando falha quando o ambiente esquenta. APROVADO COM RESSALVA ainda aprova, porque a obra precisa terminar.
- NEXT e PS-NEXT aparecem apenas como contexto: acoplamento depende da geometria do par, que o modelo não tem, e nunca se soma à perda de inserção (perda é teto, acoplamento é piso, direções opostas).
- A conta impressa vale mais que o veredito: quem lança o número na planilha precisa conferir cabo, componentes e soma explicitados.

## Limitacoes conhecidas

- Não calcula NEXT nem PS-NEXT; mostra apenas o piso da tabela por frequência como referência. Estimar acoplamento exigiria um modelo de ICR dependente da geometria do par, que a ferramenta não tem.
- Perda escala linear com o comprimento.
- Não corrige temperatura, curvatura, grampeamento nem emenda. Um cabo prensado em canaleta pode perder mais que um divisor inteiro, e nada aqui enxerga isso.
- É calculadora de bancada, não certificador: se o laudo reprovar, meça. Se aprovar com ressalva, meça antes de puxar o cabo.
- Os valores de componentes vêm de um catálogo interno baseado em faixas de norma, não de medições de equipamento real.

## Licenca

MIT. Ver [LICENSE](LICENSE).

## Autor

Kelvin Oliveira — [GitHub](https://github.com/KelvinOliveiraCode) · [portfolio](https://kelvinoliveiracode.github.io/portfolio/)

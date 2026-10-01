<div align="center">

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-72%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=flat-square" alt="Windows">
  <img src="https://img.shields.io/badge/deps-PyYAML%20only-blue?style=flat-square" alt="Deps">
</p>

# calculadora-enlace-cobre

**Orcamento de perda e laudo de certificacao para enlace de cabo de cobre, antes de puxar o cabo.**

</div>

---

## PT-BR

### O que e

CLI que soma a perda de insercao de um enlace de cabeamento estruturado - cabo
horizontal, patch cords, conectores, patch panel e divisor - compara o total com
o limite da categoria e emite um laudo com a conta aberta para conferencia
manual. Nao precisa de equipamento, nem de rede, nem de dinheiro.

### Por que foi feito

Perda de insercao mal calculada e a causa numero um de link instavel depois de
instalado. O limite da ISO/IEC 11801 vale para o **canal inteiro**, com os
componentes dentro - e a planilha quase sempre compara so o cabo com o limite.
O resultado e um enlace que "passa" na teoria e falha em campo, depois de
puxar 88 m de cabo e subir no teto.

Enquanto planejava infraestrutura, eu via esse calculo ser feito de memoria. O
valor do projeto nao esta na soma: esta em mostrar a conta, deixar a pessoa
conferir, e declarar o que o modelo **nao** cobre.

### Como rodar

```powershell
# 1. Instalar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Validar
python -m pytest tests/ -v

# 3. Executar
python -m caboclink orcamento dados/exemplo-enlace.yaml
```

Saida real:

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      14.91     20.70      5.79  APROVADO
   250      19.47     26.60      7.13  APROVADO

VEREDITO: APROVADO
```

Enlace reprovado (Cat5e a 88 m com divisor), codigo de saida 1:

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      24.60     20.00     -4.60  REPROVADO

VEREDITO: REPROVADO
```

Outros comandos:

```powershell
python -m caboclink materiais                  # lista categorias e componentes
python -m caboclink inspecionar 6A             # tabela de perdas de uma categoria
python -m caboclink orcamento dados/exemplo-enlace.yaml --laudo exemplos/laudo-exemplo.md
python -m caboclink orcamento dados/exemplo-enlace.yaml --margem 12   # ressalva mais dura
```

O laudo gerado inclui a conferencia manual:

```
- **100 MHz**: cabo 9.31 dB + componentes 5.60 dB = 14.91 dB, contra limite de 20.70 dB. Margem 5.79 dB.
- **250 MHz**: cabo 11.97 dB + componentes 7.50 dB = 19.47 dB, contra limite de 26.60 dB. Margem 7.13 dB.
```

### O que aprendi

- **O limite da norma e do canal, nao do cabo.** Essa distincao, sozinha, muda a
  conta inteira. Somar componentes ao cabo e o que separa um orcamento correto
  de um que aprova um enlace que vai falhar. Ver `docs/tabela-de-perdas.md`.
- **Perda e teto, NEXT e PS-NEXT sao piso.** Sinal demais e ruim; acoplamento
  demais e o oposto, tambem ruim. Confundir as duas direcoes reprova enlace
  bom. Descobri isso escrevendo o gerenciador de veredito: as duas direcoes
  cabem na mesma variavel, e o bug aparecia como "reprovou um Cat6A de 30 m".
- **Frequencia acima da categoria nao e perda alta, e sinal invalido.** Pedir
  500 MHz em Cat5e devolve `INVIAVEL`, nao `REPROVADO`. Misturar os dois faz o
  relatorio sugerir trocar patch cord quando o problema e o cabo.
- **Margem minima evita surpresa de campo.** Um enlace que passa com 0,4 dB de
  folga falha quando o ambiente esquenta. O veredito `APROVADO COM RESSALVA`
  existe para esse caso - e ele ainda aprova, porque a obra precisa terminar.
- **A conta impressa vale mais que o veredito.** Quem vai repassar o valor na
  planilha precisa poder conferir. Por isso o laudo traz cabo, componentes e
  soma explicitados, e o `docs/` traz a conta a mao do mesmo exemplo.

### Limitacoes

- **Nao calcula NEXT nem PS-NEXT.** Mostra o piso da norma por frequencia como
  contexto, mas nao estima acoplamento - isso exigiria modelo de ICR dependente
  de geometria de par que a ferramenta nao tem.
- **Perda escala linear com o comprimento.** Aceitavel em baixa frequencia,
  acelera perto do limite da categoria.
- **Nao corrige temperatura, curvatura, grampeamento nem emenda.** Cabo prensado
  em canaleta pode perder mais que um divisor inteiro, e nada aqui enxerga isso.
- **E uma calculadora de bancada, nao um certificador.** Se o laudo reprovar,
  meca. Se aprovar com ressalva, meca antes de passar o cabo.

### Licenca

MIT. Ver [LICENSE](LICENSE).

---

## EN

### What it is

A CLI that sums the insertion loss of a structured cabling link - horizontal
cable, patch cords, connectors, patch panel and splitter - compares the total
against the category limit, and emits a report with the arithmetic left open for
manual checking. No equipment, no network, no cost.

### Why it was built

Miscalculated insertion loss is the number one cause of an unstable link after
installation. The ISO/IEC 11801 limit applies to the **whole channel**, with the
components included - and a spreadsheet almost always compares the cable alone
against the limit. The result is a link that "passes" on paper and fails in the
field, after 88 m of cable is pulled and someone climbs the ceiling.

While planning infrastructure I watched that calculation get done from memory.
The value here is not the sum: it is showing the work, letting a person check
it, and stating plainly what the model does **not** cover.

### How to run

```powershell
# 1. Install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Validate
python -m pytest tests/ -v

# 3. Run
python -m caboclink orcamento dados/exemplo-enlace.yaml
```

Real output:

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      14.91     20.70      5.79  APROVADO
   250      19.47     26.60      7.13  APROVADO

VEREDITO: APROVADO
```

Failing link (Cat5e at 88 m with a splitter), exit code 1:

```
  FREQ  ORCAMENTO    LIMITE    MARGEM  SITUACAO
------ ---------- --------- ---------  ----------
   100      24.60     20.00     -4.60  REPROVADO

VEREDITO: REPROVADO
```

Other commands:

```powershell
python -m caboclink materials                 # list categories and components
python -m caboclink inspect 6A                # loss table for one category
python -m caboclink budget dados/exemplo-enlace.yaml --report examples/laudo-exemplo.md
python -m caboclink budget dados/exemplo-enlace.yaml --margin 12   # stricter warning
```

The generated report includes the manual check:

```
- **100 MHz**: cable 9.31 dB + components 5.60 dB = 14.91 dB, against a 20.70 dB limit. Margin 5.79 dB.
- **250 MHz**: cable 11.97 dB + components 7.50 dB = 19.47 dB, against a 26.60 dB limit. Margin 7.13 dB.
```

### What I learned

- **The standard limit belongs to the channel, not the cable.** That one
  distinction changes the whole calculation. Summing components into the cable is
  what separates a correct budget from one that approves a link that will fail.
  See `docs/tabela-de-perdas.md`.
- **Loss is a ceiling; NEXT and PS-NEXT are floors.** Losing signal is too
  little; bad coupling is too much. Mixing the directions makes you reject a
  good link. I hit this while writing the verdict handler: both directions fit
  in one variable, and the bug shows up as "rejected a 30 m Cat6A link".
- **A frequency above the category is not high loss, it is an invalid signal.**
  Asking for 500 MHz on Cat5e returns `INVIAVEL`, not `REPROVADO`. Merging the
  two makes the report suggest swapping a patch cord when the problem is the
  cable.
- **A minimum margin prevents field surprises.** A link passing with 0.4 dB of
  headroom fails once the room warms up. The `APROVADO COM RESSALVA` verdict
  exists for that case - and it still passes, because the job has to get done.
- **The printed arithmetic is worth more than the verdict.** Whoever forwards the
  number into the spreadsheet needs to be able to check it. So the report spells
  out cable, components and sum, and `docs/` carries the hand calculation of the
  very same example.

### Limitations

- **Does not compute NEXT or PS-NEXT.** It shows the standard floor per frequency
  as context, but it does not estimate coupling - that would need an ICR model
  depending on pair geometry this tool does not have.
- **Loss scales linearly with length.** Acceptable at low frequency, it
  accelerates near the category limit.
- **No temperature, bend, staple or splice correction.** A cable crushed in a
  trunking can lose more than a whole splitter, and nothing here sees that.
- **This is a bench calculator, not a certifier.** If the report rejects,
  measure. If it passes with a warning, measure before you pull the cable.

### License

MIT. See [LICENSE](LICENSE).

---

## Estrutura / Structure

```
src/caboclink/
  perdas.py         tabelas de perda por categoria e frequencia
  orcamento.py      soma, veredito e margens
  certificacao.py   laudo em Markdown
  cargador.py       leitura de YAML
  cli.py            interface de linha de comando
dados/              materiais.yaml e enlaces de exemplo
docs/               tabela de perdas, leitura de ficha tecnica
exemplos/           saidas reais geradas pela ferramenta
tests/              72 testes
```

## Licenca / License

MIT &mdash; [LICENSE](LICENSE)

---

<div align="center">
  <sub>Por <a href="https://github.com/KelvinOliveiraCode">Kelvin Oliveira</a> &middot;
  <a href="https://kelvinoliveiracode.github.io/portfolio/">portfolio</a></sub>
</div>
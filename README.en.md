<div align="center">

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-72%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-97%25-brightgreen?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
</p>

# calculadora-enlace-cobre

**Insertion loss budget and certification report for structured copper cabling links, built to run before pulling the cable.**

</div>

---

## Problem / Why it exists

Incorrectly calculated insertion loss is the most common cause of an unstable link after installation. The ISO/IEC 11801 limit applies to the entire channel — horizontal cable, connectors, patch panel, and patch cords — and almost every spreadsheet compares only the cable against the limit. The result is a link that "passes" on paper and fails in the field, after the cable is pulled and the ceiling is opened.

The project was born seeing this calculation done by head in infrastructure planning. The tool's value is not in the final number: it is in showing the itemized calculation so anyone can check it by hand, and in explicitly declaring what the model does not cover.

## What it does

The CLI `caboclink` reads a YAML describing the link (category, horizontal channel length, quantities of patch cords, connectors, patch panels, and optional splitter) and:

1. Sums cable loss (linear with length) with each component's loss, per frequency.
2. Compares the total with the category limit at each evaluated frequency (100 MHz, 250 MHz, and 500 MHz, depending on category).
3. Classifies: APPROVED, APPROVED WITH RESERVATION (margin below 1.5 dB), REJECTED (budget above limit or physical limits exceeded) or INFEASIBLE (frequency above category).
4. Optionally emits a Markdown report with the itemized calculation (cable + components = total, against the limit) and the category NEXT/PS-NEXT floors as reference.

Exit codes: 0 approved or reservation, 1 rejected or infeasible, 2 input error (missing or invalid file).

## Stack

- Python 3.10 or higher
- PyYAML 6.0 or higher (only runtime dependency)
- pytest and pytest-cov (dev)
- Runs offline, without network dependency or certification equipment

## How it works

- Cable loss: category table value multiplied by `length / 100`. Example: Cat6 at 45 m at 100 MHz = 20.70 × 0.45 = 9.31 dB.
- Components (patch cord, connector, patch panel, splitter) sum the fixed table value per frequency, regardless of length.
- Physical limits are checked before any calculation: channel above 90 m is rejected; total link (channel + 2 m per patch cord + 0.3 m per connector) above 100 m is rejected.
- Frequency above category returns INFEASIBLE, not REJECTED: an invalid signal is not the same as high loss.
- Margin = limit minus budget. Negative margin rejects; positive margin below 1.5 dB becomes APPROVED WITH RESERVATION.
- NEXT and PS-NEXT are coupling floors, not losses: they appear only as reference in the report, never added to the loss budget.
- Deterministic: same input always produces the same output.

## How to run

```powershell
# 1. Install
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

# 2. Validate
python -m pytest tests/ -q

# 3. Run (valid link: Cat6, 45 m, 100 and 250 MHz)
python -m caboclink orcamento dados/exemplo-enlace.yaml
```

Real output:

```
  FREQ  BUDGET    LIMIT    MARGIN  STATUS
------ ---------- --------- --------- ----------
   100     14.91     20.70      5.79  APPROVED
   250     19.47     26.60      7.13  APPROVED

VERDICT: APPROVED
```

Rejected link (Cat5e at 88 m with splitter), exit code 1:

```powershell
python -m caboclink orcamento dados/enlace-longo-cat5e.yaml
```

```
  FREQ  BUDGET    LIMIT    MARGIN  STATUS
------ ---------- --------- --------- ----------
   100     24.60     20.00     -4.60  REJECTED

VERDICT: REJECTED
```

Other commands:

```powershell
python -m caboclink materiais                  # lists categories and components
python -m caboclink inspecionar 6A             # category loss table
python -m caboclink orcamento dados/exemplo-enlace.yaml --laudo exemplos/laudo-exemplo.md
python -m caboclink orcamento dados/exemplo-enlace.yaml --margem 12   # requires 12 dB margin
```

The report includes the "Manual verification" section, with one line per frequency showing cable, components, total, limit, and margin.

## Project structure

```
src/caboclink/
  __main__.py      entry point (`python -m caboclink`)
  cli.py           argument parser and subcommands (orcamento, materiais, inspecionar)
  cargador.py      link YAML reading and materials catalog
  perdas.py        category and frequency loss tables, physical limits, NEXT/PS-NEXT floors
  orcamento.py     Link and Result models, budget() function, verdict rules
  certificacao.py  Markdown report generation
dados/             materials catalog (materiais.yaml) and example links
docs/              loss table and datasheet reading guide
exemplos/          real outputs generated by the tool
tests/             72 tests
pyproject.toml     package configuration (setuptools, pytest)
requirements.txt   dependencies (PyYAML, pytest, pytest-cov)
LICENSE            MIT
README.md
```

## Trade-offs and decisions

- Loss scales linearly with length: simple and predictable, acceptable at low frequency; it accelerates near the category limit, and the tool does not model skin effect.
- Physical limits are checked before any calculation: no budget is invented for a physically impossible link.
- INFEASIBLE separated from REJECTED: frequency above category is an invalid signal, not high loss; mixing the two leads to replacing the patch cord when the problem is the category.
- Minimum margin of 1.5 dB by default: a link that barely passes fails when the environment heats up. APPROVED WITH RESERVATION still approves because the construction needs to finish.
- NEXT and PS-NEXT appear only as context: coupling depends on pair geometry, which the model lacks, and never adds to insertion loss (loss is a ceiling, coupling is a floor, opposite directions).
- The printed calculation matters more than the verdict: whoever enters the number in the spreadsheet needs to check cable, components, and sum explicitly.

## Known limitations

- Does not calculate NEXT or PS-NEXT; shows only the table floor per frequency as reference. Estimating coupling would require a geometry-dependent model of pair behavior, which the tool lacks.
- Loss scales linearly with length.
- Does not correct for temperature, bends, stapling, or splices. A cable crushed in a tray can lose more than a whole splitter, and nothing here detects it.
- It is a desk calculator, not a certifier: if the report rejects, measure. If it approves with reservation, measure before pulling the cable.
- Component values come from an internal catalog based on norm ranges, not real equipment measurements.

## License

MIT. See [LICENSE](LICENSE).

## Author

Kelvin Oliveira — [GitHub](https://github.com/KelvinOliveiraCode) · [portfolio](https://kelvinoliveiracode.github.io/portfolio/)

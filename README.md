# finmath-br

[![CI](https://github.com/thayroncarlessi/finmath-br/actions/workflows/ci.yml/badge.svg)](https://github.com/thayroncarlessi/finmath-br/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

Deterministic Brazilian financial math primitives for Python. The library makes
calendar, compounding and day-count conventions explicit so calculations remain
auditable and reproducible.

## Scope

- B3 financial business-day calendar
- Following, modified following, preceding and modified preceding adjustments
- Business/252, Actual/365 and Actual/360 year fractions
- Effective rate conversion
- DI accumulation, percentage of CDI and CDI plus spread
- Dated cash-flow present value
- Macaulay duration, modified duration and convexity
- Deterministic yield-to-maturity solver

The package deliberately does not fetch live rates. Market observations should
enter your application as explicit inputs with their source and reference date.

## Install

```bash
uv add git+https://github.com/thayroncarlessi/finmath-br.git
```

Or with pip:

```bash
pip install git+https://github.com/thayroncarlessi/finmath-br.git
```

## Quick start

```python
from datetime import date

from finmath_br import (
    CashFlow,
    add_business_days,
    cdi_percentage_factor,
    modified_duration,
    present_value,
)

settlement = date(2026, 1, 2)
cashflows = [
    CashFlow(add_business_days(settlement, 126), 70.0),
    CashFlow(add_business_days(settlement, 252), 1_070.0),
]

price = present_value(cashflows, settlement, annual_discount_rate=0.145)
duration = modified_duration(cashflows, settlement, annual_discount_rate=0.145)
factor = cdi_percentage_factor(
    annual_cdi_rate=0.14,
    percentage=1.20,  # 120% of CDI
    business_days=252,
)
```

### Date interval convention

`business_days_between(start, end)` counts the interval `(start, end]` by
default. Boundary inclusion can be changed explicitly.

```python
from datetime import date
from finmath_br import business_days_between

business_days_between(date(2026, 1, 9), date(2026, 1, 12))  # 1
```

### CDI convention

For a percentage of CDI, the percentage is applied to each effective daily CDI
rate before accumulation. `percentage=1.20` means 120%, not 1.20%.

For CDI plus spread, the CDI and spread factors are compounded independently on
the selected Business/252 basis.

## Development

```bash
git clone https://github.com/thayroncarlessi/finmath-br.git
cd finmath-br
uv sync --dev
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv build
```

## Methodology references

- [B3 DI rate methodology](https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/di/metodologia-de-apuracao-da-taxa/): DI rates are expressed on an annualized 252-business-day basis.
- [B3 calculation system operations manual](https://www.b3.com.br/data/files/57/62/C3/37/47FA4610C2E69A46AC094EA8/Manual-de-Operacoes-CALC-20180620.pdf): Brazilian fixed-income calculation conventions.
- [BCB Resolution 2,516](https://www.bcb.gov.br/pre/normativos/res/1998/pdf/res_2516_v2_P.pdf): definition of business days for financial-market operations.
- [`holidays` B3 calendar](https://holidays.readthedocs.io/en/latest/auto_gen_docs/brasil_bolsa_balcao/): implementation source for the B3/BVMF holiday calendar.

## Precision and responsibility

The package uses Python floating-point arithmetic and does not impose product-
specific rounding rules, tax treatment, fallback provisions or contractual
calendar overrides. Validate results against the instrument documentation and
the applicable B3, ANBIMA, BCB or contractual methodology before production use.

This software is an engineering tool, not investment, accounting or legal advice.

## License

[MIT](LICENSE)

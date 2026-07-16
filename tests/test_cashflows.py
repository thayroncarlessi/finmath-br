from datetime import date

import pytest

from finmath_br.calendar import add_business_days
from finmath_br.cashflows import (
    CashFlow,
    convexity,
    macaulay_duration,
    modified_duration,
    present_value,
    yield_to_maturity,
)
from finmath_br.day_count import DayCountConvention


def test_single_cashflow_price_and_risk_measures() -> None:
    settlement = date(2026, 1, 2)
    maturity = add_business_days(settlement, 252)
    flows = [CashFlow(maturity, 1_000)]

    assert present_value(flows, settlement, 0.10) == pytest.approx(1_000 / 1.10)
    assert macaulay_duration(flows, settlement, 0.10) == pytest.approx(1)
    assert modified_duration(flows, settlement, 0.10) == pytest.approx(1 / 1.10)
    assert convexity(flows, settlement, 0.10) == pytest.approx(2 / 1.10**2)


def test_multiple_cashflow_price_with_actual_365() -> None:
    settlement = date(2026, 1, 1)
    flows = [
        CashFlow(date(2026, 7, 2), 50),
        CashFlow(date(2027, 1, 1), 1_050),
    ]

    expected = 50 / 1.10 ** (182 / 365) + 1_050 / 1.10
    assert present_value(
        flows,
        settlement,
        0.10,
        day_count=DayCountConvention.ACTUAL_365,
    ) == pytest.approx(expected)


def test_yield_solver_recovers_original_rate() -> None:
    settlement = date(2026, 1, 2)
    flows = [
        CashFlow(add_business_days(settlement, 126), 60),
        CashFlow(add_business_days(settlement, 252), 1_060),
    ]
    price = present_value(flows, settlement, 0.1375)

    assert yield_to_maturity(flows, settlement, price) == pytest.approx(0.1375, abs=1e-10)


def test_cashflow_validations() -> None:
    settlement = date(2026, 1, 2)
    future = CashFlow(date(2027, 1, 2), 100)

    with pytest.raises(ValueError, match="amount"):
        CashFlow(date(2027, 1, 2), float("inf"))
    with pytest.raises(ValueError, match="must not be empty"):
        present_value([], settlement, 0.1)
    with pytest.raises(ValueError, match="before settlement"):
        present_value([CashFlow(date(2026, 1, 1), 100)], settlement, 0.1)
    with pytest.raises(ValueError, match="annual_discount_rate"):
        present_value([future], settlement, -1)
    with pytest.raises(ValueError, match="positive present value"):
        macaulay_duration([CashFlow(date(2027, 1, 2), -100)], settlement, 0.1)
    with pytest.raises(ValueError, match="positive present value"):
        convexity([CashFlow(date(2027, 1, 2), -100)], settlement, 0.1)


@pytest.mark.parametrize(
    ("price", "flows", "kwargs", "match"),
    [
        (0, [CashFlow(date(2027, 1, 2), 100)], {}, "price"),
        (100, [CashFlow(date(2027, 1, 2), -100)], {}, "non-negative"),
        (100, [CashFlow(date(2027, 1, 2), 0)], {}, "non-negative"),
        (100, [CashFlow(date(2027, 1, 2), 100)], {"tolerance": 0}, "tolerance"),
        (100, [CashFlow(date(2027, 1, 2), 100)], {"max_iterations": 0}, "max_iterations"),
        (200, [CashFlow(date(2026, 1, 2), 100)], {}, "unique yield"),
    ],
)
def test_yield_solver_validations(price, flows, kwargs, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        yield_to_maturity(flows, date(2026, 1, 2), price, **kwargs)

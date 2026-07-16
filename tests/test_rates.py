import math

import pytest

from finmath_br.rates import (
    accumulate_daily_di,
    annual_to_periodic,
    cdi_percentage_factor,
    cdi_spread_factor,
    di_factor,
    equivalent_rate,
    periodic_to_annual,
)


def test_effective_rate_round_trip() -> None:
    monthly = annual_to_periodic(0.12, 12)

    assert periodic_to_annual(monthly, 12) == pytest.approx(0.12)
    assert equivalent_rate(monthly, 12, 252) == pytest.approx(annual_to_periodic(0.12, 252))


def test_di_factor_matches_annual_rate_at_252_days() -> None:
    assert di_factor(0.15, 0) == 1
    assert di_factor(0.15, 252) == pytest.approx(1.15)


def test_cdi_percentage_is_applied_to_daily_rate() -> None:
    daily = annual_to_periodic(0.14, 252)

    assert cdi_percentage_factor(0.14, 1.2, 10) == pytest.approx((1 + daily * 1.2) ** 10)


def test_cdi_spread_compounds_both_annual_factors() -> None:
    assert cdi_spread_factor(0.14, 0.02, 252) == pytest.approx(1.14 * 1.02)


def test_daily_di_accumulation_supports_variable_observations() -> None:
    rates = [0.10, 0.11, 0.12]
    expected = math.prod(1 + annual_to_periodic(rate, 252) for rate in rates)

    assert accumulate_daily_di(rates) == pytest.approx(expected)
    assert accumulate_daily_di([]) == 1


@pytest.mark.parametrize(
    ("call", "match"),
    [
        (lambda: annual_to_periodic(-1, 12), "annual_rate"),
        (lambda: annual_to_periodic(0.1, 0), "periods_per_year"),
        (lambda: periodic_to_annual(float("nan"), 12), "periodic_rate"),
        (lambda: di_factor(0.1, -1), "business_days"),
        (lambda: di_factor(0.1, 1, basis=0), "basis"),
        (lambda: cdi_percentage_factor(0.1, -0.1, 1), "percentage"),
        (lambda: cdi_percentage_factor(0.1, 1, -1), "business_days"),
        (lambda: cdi_percentage_factor(0.1, 1, 1, basis=0), "basis"),
        (lambda: cdi_spread_factor(0.1, -1, 1), "annual_spread"),
        (lambda: accumulate_daily_di([0.1], percentage=-1), "percentage"),
        (lambda: accumulate_daily_di([0.1], basis=0), "basis"),
        (lambda: accumulate_daily_di([-1]), "annual_di_rate"),
    ],
)
def test_invalid_rate_inputs_raise_value_error(call, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        call()

"""Rate conversion and Brazilian DI/CDI accumulation functions."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite, prod


def _validate_rate(rate: float, name: str = "rate") -> None:
    if not isfinite(rate) or rate <= -1:
        raise ValueError(f"{name} must be finite and greater than -1")


def _validate_periods(periods: float, name: str) -> None:
    if not isfinite(periods) or periods <= 0:
        raise ValueError(f"{name} must be finite and greater than zero")


def annual_to_periodic(annual_rate: float, periods_per_year: float) -> float:
    """Convert an effective annual rate to an effective periodic rate."""

    _validate_rate(annual_rate, "annual_rate")
    _validate_periods(periods_per_year, "periods_per_year")
    return (1 + annual_rate) ** (1 / periods_per_year) - 1


def periodic_to_annual(periodic_rate: float, periods_per_year: float) -> float:
    """Convert an effective periodic rate to an effective annual rate."""

    _validate_rate(periodic_rate, "periodic_rate")
    _validate_periods(periods_per_year, "periods_per_year")
    return (1 + periodic_rate) ** periods_per_year - 1


def equivalent_rate(rate: float, from_periods_per_year: float, to_periods_per_year: float) -> float:
    """Convert an effective rate from one compounding period to another."""

    annual = periodic_to_annual(rate, from_periods_per_year)
    return annual_to_periodic(annual, to_periods_per_year)


def di_factor(annual_di_rate: float, business_days: int, *, basis: int = 252) -> float:
    """Return the accumulation factor for an annualized DI rate."""

    _validate_rate(annual_di_rate, "annual_di_rate")
    if business_days < 0:
        raise ValueError("business_days must be non-negative")
    if basis <= 0:
        raise ValueError("basis must be greater than zero")
    return (1 + annual_di_rate) ** (business_days / basis)


def cdi_percentage_factor(
    annual_cdi_rate: float,
    percentage: float,
    business_days: int,
    *,
    basis: int = 252,
) -> float:
    """Accumulate a percentage of CDI using the effective daily CDI rate.

    ``percentage=1.2`` means 120% of CDI. The percentage is applied to the
    effective daily rate, not to the annual rate.
    """

    _validate_rate(annual_cdi_rate, "annual_cdi_rate")
    if not isfinite(percentage) or percentage < 0:
        raise ValueError("percentage must be finite and non-negative")
    if business_days < 0:
        raise ValueError("business_days must be non-negative")
    if basis <= 0:
        raise ValueError("basis must be greater than zero")

    daily_cdi = annual_to_periodic(annual_cdi_rate, basis)
    return (1 + daily_cdi * percentage) ** business_days


def cdi_spread_factor(
    annual_cdi_rate: float,
    annual_spread: float,
    business_days: int,
    *,
    basis: int = 252,
) -> float:
    """Accumulate CDI plus an effective annual spread."""

    _validate_rate(annual_spread, "annual_spread")
    return di_factor(annual_cdi_rate, business_days, basis=basis) * di_factor(
        annual_spread,
        business_days,
        basis=basis,
    )


def accumulate_daily_di(
    annual_di_rates: Iterable[float],
    *,
    percentage: float = 1.0,
    basis: int = 252,
) -> float:
    """Accumulate a series of annualized daily DI observations."""

    if not isfinite(percentage) or percentage < 0:
        raise ValueError("percentage must be finite and non-negative")
    if basis <= 0:
        raise ValueError("basis must be greater than zero")

    factors = []
    for rate in annual_di_rates:
        _validate_rate(rate, "annual_di_rate")
        daily_rate = annual_to_periodic(rate, basis)
        factors.append(1 + daily_rate * percentage)
    return prod(factors)

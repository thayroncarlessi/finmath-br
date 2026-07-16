"""Deterministic Brazilian financial math primitives."""

from finmath_br.calendar import (
    BusinessDayConvention,
    add_business_days,
    adjust,
    business_days_between,
    is_business_day,
)
from finmath_br.cashflows import (
    CashFlow,
    convexity,
    macaulay_duration,
    modified_duration,
    present_value,
    yield_to_maturity,
)
from finmath_br.day_count import DayCountConvention, year_fraction
from finmath_br.rates import (
    accumulate_daily_di,
    annual_to_periodic,
    cdi_percentage_factor,
    cdi_spread_factor,
    di_factor,
    equivalent_rate,
    periodic_to_annual,
)

__all__ = [
    "BusinessDayConvention",
    "CashFlow",
    "DayCountConvention",
    "accumulate_daily_di",
    "add_business_days",
    "adjust",
    "annual_to_periodic",
    "business_days_between",
    "cdi_percentage_factor",
    "cdi_spread_factor",
    "convexity",
    "di_factor",
    "equivalent_rate",
    "is_business_day",
    "macaulay_duration",
    "modified_duration",
    "periodic_to_annual",
    "present_value",
    "year_fraction",
    "yield_to_maturity",
]

__version__ = "0.1.0"

"""Cash-flow pricing and risk measures."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from math import isfinite

from finmath_br.day_count import DayCountConvention, year_fraction


@dataclass(frozen=True, slots=True)
class CashFlow:
    """A dated monetary amount."""

    payment_date: date
    amount: float

    def __post_init__(self) -> None:
        if not isfinite(self.amount):
            raise ValueError("amount must be finite")


def _validated_cashflows(cashflows: Iterable[CashFlow], settlement: date) -> tuple[CashFlow, ...]:
    flows = tuple(cashflows)
    if not flows:
        raise ValueError("cashflows must not be empty")
    if any(flow.payment_date < settlement for flow in flows):
        raise ValueError("cashflows before settlement are not supported")
    return flows


def _validate_discount_rate(annual_discount_rate: float) -> None:
    if not isfinite(annual_discount_rate) or annual_discount_rate <= -1:
        raise ValueError("annual_discount_rate must be finite and greater than -1")


def _discounted_values(
    cashflows: Iterable[CashFlow],
    settlement: date,
    annual_discount_rate: float,
    day_count: DayCountConvention | str,
) -> tuple[tuple[float, float], ...]:
    _validate_discount_rate(annual_discount_rate)
    flows = _validated_cashflows(cashflows, settlement)
    return tuple(
        (
            year_fraction(settlement, flow.payment_date, day_count),
            flow.amount
            / (1 + annual_discount_rate) ** year_fraction(settlement, flow.payment_date, day_count),
        )
        for flow in flows
    )


def present_value(
    cashflows: Iterable[CashFlow],
    settlement: date,
    annual_discount_rate: float,
    *,
    day_count: DayCountConvention | str = DayCountConvention.BUSINESS_252,
) -> float:
    """Discount dated cash flows using an effective annual rate."""

    return sum(
        discounted
        for _, discounted in _discounted_values(
            cashflows,
            settlement,
            annual_discount_rate,
            day_count,
        )
    )


def macaulay_duration(
    cashflows: Iterable[CashFlow],
    settlement: date,
    annual_discount_rate: float,
    *,
    day_count: DayCountConvention | str = DayCountConvention.BUSINESS_252,
) -> float:
    """Return Macaulay duration in years."""

    discounted = _discounted_values(cashflows, settlement, annual_discount_rate, day_count)
    price = sum(value for _, value in discounted)
    if price <= 0:
        raise ValueError("duration requires a positive present value")
    return sum(years * value for years, value in discounted) / price


def modified_duration(
    cashflows: Iterable[CashFlow],
    settlement: date,
    annual_discount_rate: float,
    *,
    day_count: DayCountConvention | str = DayCountConvention.BUSINESS_252,
) -> float:
    """Return modified duration for an effective annual yield."""

    _validate_discount_rate(annual_discount_rate)
    return macaulay_duration(
        cashflows,
        settlement,
        annual_discount_rate,
        day_count=day_count,
    ) / (1 + annual_discount_rate)


def convexity(
    cashflows: Iterable[CashFlow],
    settlement: date,
    annual_discount_rate: float,
    *,
    day_count: DayCountConvention | str = DayCountConvention.BUSINESS_252,
) -> float:
    """Return annual effective-yield convexity."""

    _validate_discount_rate(annual_discount_rate)
    discounted = _discounted_values(cashflows, settlement, annual_discount_rate, day_count)
    price = sum(value for _, value in discounted)
    if price <= 0:
        raise ValueError("convexity requires a positive present value")
    scale = (1 + annual_discount_rate) ** 2
    return sum(years * (years + 1) * value for years, value in discounted) / (price * scale)


def yield_to_maturity(
    cashflows: Iterable[CashFlow],
    settlement: date,
    price: float,
    *,
    day_count: DayCountConvention | str = DayCountConvention.BUSINESS_252,
    tolerance: float = 1e-12,
    max_iterations: int = 256,
) -> float:
    """Solve the effective annual yield of non-negative future cash flows.

    The solver uses a bracketed bisection, favoring deterministic behavior over
    speed. Mixed-sign cash flows may have multiple roots and are rejected.
    """

    if not isfinite(price) or price <= 0:
        raise ValueError("price must be finite and positive")
    if not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    flows = _validated_cashflows(cashflows, settlement)
    if any(flow.amount < 0 for flow in flows) or not any(flow.amount > 0 for flow in flows):
        raise ValueError("yield solver requires non-negative cash flows")

    def residual(rate: float) -> float:
        return present_value(flows, settlement, rate, day_count=day_count) - price

    lower = -0.999999999
    upper = 1.0
    lower_residual = residual(lower)
    upper_residual = residual(upper)
    while upper_residual > 0 and upper < 1_000_000:
        upper = upper * 2 + 1
        upper_residual = residual(upper)

    if lower_residual < 0 or upper_residual > 0:
        raise ValueError("price does not admit a unique yield in the supported domain")

    midpoint = 0.0
    for _ in range(max_iterations):
        midpoint = (lower + upper) / 2
        value = residual(midpoint)
        if abs(value) <= tolerance:
            return midpoint
        if value > 0:
            lower = midpoint
        else:
            upper = midpoint
    return midpoint

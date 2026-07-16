"""Day-count conventions used by the pricing functions."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from finmath_br.calendar import business_days_between


class DayCountConvention(StrEnum):
    """Supported year-fraction conventions."""

    BUSINESS_252 = "business/252"
    ACTUAL_365 = "actual/365"
    ACTUAL_360 = "actual/360"


def year_fraction(
    start: date,
    end: date,
    convention: DayCountConvention | str = DayCountConvention.BUSINESS_252,
) -> float:
    """Return the signed year fraction between two dates."""

    rule = DayCountConvention(convention)
    if rule is DayCountConvention.BUSINESS_252:
        return business_days_between(start, end) / 252
    if rule is DayCountConvention.ACTUAL_365:
        return (end - start).days / 365
    return (end - start).days / 360

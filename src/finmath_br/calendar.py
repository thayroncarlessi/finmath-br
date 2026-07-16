"""Brazilian financial business-day calendar utilities."""

from __future__ import annotations

from datetime import date, timedelta
from enum import StrEnum
from functools import lru_cache

from holidays.financial import BVMF


class BusinessDayConvention(StrEnum):
    """Rules for adjusting a date that is not a financial business day."""

    FOLLOWING = "following"
    MODIFIED_FOLLOWING = "modified_following"
    PRECEDING = "preceding"
    MODIFIED_PRECEDING = "modified_preceding"
    UNADJUSTED = "unadjusted"


@lru_cache(maxsize=128)
def _holidays_for_year(year: int) -> BVMF:
    return BVMF(years=year)


def is_business_day(day: date) -> bool:
    """Return whether *day* is a weekday in the B3 financial calendar."""

    return day.weekday() < 5 and day not in _holidays_for_year(day.year)


def business_days_between(
    start: date,
    end: date,
    *,
    include_start: bool = False,
    include_end: bool = True,
) -> int:
    """Count financial business days between two dates.

    The default interval is ``(start, end]``, matching the usual accumulation
    convention. Reversed intervals return a negative count.
    """

    if end < start:
        return -business_days_between(
            end,
            start,
            include_start=include_end,
            include_end=include_start,
        )

    count = 0
    current = start
    while current <= end:
        is_included = (current != start or include_start) and (current != end or include_end)
        if is_included and is_business_day(current):
            count += 1
        current += timedelta(days=1)
    return count


def add_business_days(day: date, days: int) -> date:
    """Move a date by a signed number of financial business days."""

    if days == 0:
        return day

    direction = 1 if days > 0 else -1
    remaining = abs(days)
    current = day
    while remaining:
        current += timedelta(days=direction)
        if is_business_day(current):
            remaining -= 1
    return current


def _roll(day: date, direction: int) -> date:
    current = day
    while not is_business_day(current):
        current += timedelta(days=direction)
    return current


def adjust(
    day: date,
    convention: BusinessDayConvention | str = BusinessDayConvention.FOLLOWING,
) -> date:
    """Adjust a date according to a standard business-day convention."""

    rule = BusinessDayConvention(convention)
    if rule is BusinessDayConvention.UNADJUSTED or is_business_day(day):
        return day

    if rule is BusinessDayConvention.FOLLOWING:
        return _roll(day, 1)
    if rule is BusinessDayConvention.PRECEDING:
        return _roll(day, -1)
    if rule is BusinessDayConvention.MODIFIED_FOLLOWING:
        following = _roll(day, 1)
        return following if following.month == day.month else _roll(day, -1)

    preceding = _roll(day, -1)
    return preceding if preceding.month == day.month else _roll(day, 1)

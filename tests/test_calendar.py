from datetime import date

import pytest

from finmath_br.calendar import (
    BusinessDayConvention,
    add_business_days,
    adjust,
    business_days_between,
    is_business_day,
)


def test_business_day_recognizes_weekends_and_b3_holidays() -> None:
    assert is_business_day(date(2026, 1, 2))
    assert not is_business_day(date(2026, 1, 1))
    assert not is_business_day(date(2026, 1, 3))


def test_business_days_between_uses_open_closed_interval() -> None:
    friday = date(2026, 1, 9)
    monday = date(2026, 1, 12)

    assert business_days_between(friday, monday) == 1
    assert business_days_between(friday, monday, include_start=True) == 2
    assert business_days_between(monday, friday) == -1


def test_business_days_between_same_day() -> None:
    monday = date(2026, 1, 12)

    assert business_days_between(monday, monday) == 0
    assert business_days_between(monday, monday, include_start=True, include_end=True) == 1


def test_add_business_days_supports_both_directions() -> None:
    friday = date(2026, 1, 9)

    assert add_business_days(friday, 1) == date(2026, 1, 12)
    assert add_business_days(friday, -1) == date(2026, 1, 8)
    assert add_business_days(friday, 0) == friday


@pytest.mark.parametrize(
    ("convention", "expected"),
    [
        (BusinessDayConvention.FOLLOWING, date(2026, 2, 2)),
        (BusinessDayConvention.MODIFIED_FOLLOWING, date(2026, 1, 30)),
        (BusinessDayConvention.PRECEDING, date(2026, 1, 30)),
        (BusinessDayConvention.MODIFIED_PRECEDING, date(2026, 1, 30)),
        (BusinessDayConvention.UNADJUSTED, date(2026, 1, 31)),
    ],
)
def test_adjust_business_day_conventions(
    convention: BusinessDayConvention,
    expected: date,
) -> None:
    assert adjust(date(2026, 1, 31), convention) == expected


def test_modified_preceding_does_not_cross_month() -> None:
    assert adjust(date(2026, 2, 1), BusinessDayConvention.MODIFIED_PRECEDING) == date(2026, 2, 2)


def test_adjust_accepts_string_and_rejects_unknown_rule() -> None:
    assert adjust(date(2026, 1, 3), "following") == date(2026, 1, 5)
    with pytest.raises(ValueError):
        adjust(date(2026, 1, 3), "sideways")

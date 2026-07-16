from datetime import date

from finmath_br.day_count import DayCountConvention, year_fraction


def test_actual_day_count_conventions() -> None:
    start = date(2026, 1, 1)
    end = date(2027, 1, 1)

    assert year_fraction(start, end, DayCountConvention.ACTUAL_365) == 1
    assert year_fraction(start, end, DayCountConvention.ACTUAL_360) == 365 / 360


def test_business_252_is_signed() -> None:
    friday = date(2026, 1, 9)
    monday = date(2026, 1, 12)

    assert year_fraction(friday, monday) == 1 / 252
    assert year_fraction(monday, friday) == -1 / 252


def test_day_count_accepts_string() -> None:
    assert year_fraction(date(2026, 1, 1), date(2026, 1, 31), "actual/360") == 1 / 12

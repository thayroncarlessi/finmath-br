from datetime import date

from finmath_br import (
    CashFlow,
    add_business_days,
    cdi_percentage_factor,
    modified_duration,
    present_value,
    yield_to_maturity,
)

settlement = date(2026, 1, 2)
cashflows = [
    CashFlow(add_business_days(settlement, 126), 70.0),
    CashFlow(add_business_days(settlement, 252), 1_070.0),
]

price = present_value(cashflows, settlement, 0.145)
duration = modified_duration(cashflows, settlement, 0.145)
yield_rate = yield_to_maturity(cashflows, settlement, price)
cdi_120_factor = cdi_percentage_factor(0.14, 1.20, 252)

print(f"Price: {price:,.2f}")
print(f"Yield: {yield_rate:.4%}")
print(f"Modified duration: {duration:.4f} years")
print(f"120% CDI factor: {cdi_120_factor:.8f}")

from decimal import ROUND_HALF_UP, Decimal
from math import floor


def arredmultb(number: float, digits: float) -> float:
    return round(floor(number * 100) / 100, digits)


def round_no_rounding(number: float, digits: int) -> float:
    return number


def round_half_up(value, digits=2):

    value = value if isinstance(value, Decimal) else Decimal(value)
    fmt = ".{}1".format("0" * (digits - 1))
    return float(value.quantize(Decimal(fmt), rounding=ROUND_HALF_UP))

from enum import Enum, IntEnum


class InterestRateType(Enum):
    daily = "daily"
    annual = "annual"
    semiannual = "semiannual"
    monthly = "monthly"
    quarterly = "quarterly"


class YearSizeType(IntEnum):
    banker = 360
    commercial = 365


def convert_to_daily_interest_rate(
    interest_rate_aliquot,
    interest_rate_type=InterestRateType.daily,
    year_size=YearSizeType.commercial,
):
    """ "Convert aliquots from a given rate to a daily interest rate.

    This function will convert an aliquot from a given rate (as in
    InterestRateType) to a daily interest rate, since "a day" is the default
    unit time adopted for financial modelling in this library. It is also
    important to note that the proper conversion of rates depends on the
    size of a year in days.

    Parameters
    ----------
    interest_rate_aliquot: float, required
        Aliquot to be converted to a daily interest rate aliquot.
    interest_rate_type: InterestRateType, optional
        The type of rate in which the input aliquot is capitalized
        (default: InterestRateType.daily).
    year_size: YearSizeType, optional
        A year size is necessary since monthly, quarterly and semiannual
        rates are relative to an annum (default YearSizeType.commercial).

    Returns
    -------
    float
        Aliquot as a daily interest rate.

    Raises
    ------
    TypeError
        If the interest_rate_type is none one of the enumerated in
        InterestRateType.
    """
    return convert_interest_rate(
        interest_rate_aliquot, interest_rate_type, InterestRateType.daily, year_size
    )


def convert_interest_rate(
    interest_rate_aliquot, from_rate_type, to_rate_type, year_size, month_size=None
):
    if from_rate_type == to_rate_type:
        return interest_rate_aliquot
    elif (
        from_rate_type == InterestRateType.annual
        and to_rate_type == InterestRateType.daily
    ):
        # 1 + a = (1 + d)^365 => d = (1 + a)^(1/365) - 1
        return (1 + interest_rate_aliquot) ** (1 / year_size) - 1
    elif (
        from_rate_type == InterestRateType.semiannual
        and to_rate_type == InterestRateType.daily
    ):
        # (1 + s)^2 = (1 + d)^365 => d = (1 + s)^(2/365) - 1
        return (1 + interest_rate_aliquot) ** (2 / year_size) - 1
    elif (
        from_rate_type == InterestRateType.monthly
        and to_rate_type == InterestRateType.daily
    ):
        # (1 + m)^12 = (1 + d)^365 => d = (1 + m)^(12/365) - 1
        month_size = month_size or year_size / 12
        return (1 + interest_rate_aliquot) ** (1 / month_size) - 1
    elif (
        from_rate_type == InterestRateType.quarterly
        and to_rate_type == InterestRateType.daily
    ):
        # (1 + q)^4 = (1 + d)^365 => d = (1 + q)^(4/365) - 1
        return (1 + interest_rate_aliquot) ** (4 / year_size) - 1
    elif (
        from_rate_type == InterestRateType.daily
        and to_rate_type == InterestRateType.annual
    ):
        # (1 + d)^365 = (1 + a) => a = (1 + d)^(365) - 1
        return (1 + interest_rate_aliquot) ** year_size - 1
    elif (
        from_rate_type == InterestRateType.daily
        and to_rate_type == InterestRateType.semiannual
    ):
        # (1 + d)^365 = (1 + s)^2 => s = (1 + d)^(365/2) - 1
        return (1 + interest_rate_aliquot) ** (year_size / 2) - 1
    elif (
        from_rate_type == InterestRateType.daily
        and to_rate_type == InterestRateType.monthly
    ):
        # (1 + d)^365 = (1 + m)^12 => m = (1 + d)^(365/12) - 1
        month_size = month_size or year_size / 12
        
        return (1 + interest_rate_aliquot) ** (month_size) - 1
    elif (
        from_rate_type == InterestRateType.daily
        and to_rate_type == InterestRateType.quarterly
    ):
        # (1 + d)^365 = (1 + q)^4 => q = (1 + d)^(365/4) - 1
        return (1 + interest_rate_aliquot) ** (year_size / 4) - 1
    else:
        raise TypeError(
            f"Unknown interest rate type conversion from {from_rate_type} to {to_rate_type}."
        )

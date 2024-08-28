from calendar import month
import pytest

from loan_calculator.interest_rate import (
    InterestRateType,
    convert_to_daily_interest_rate,
    convert_interest_rate,
)
from loan_calculator import YearSizeType


def test_convert_daily_interest_rate():
    assert convert_to_daily_interest_rate(
        1.2, InterestRateType.daily, YearSizeType.commercial
    ) == pytest.approx(1.2)


def test_convert_annual_interest_rate():
    assert convert_to_daily_interest_rate(
        2**YearSizeType.commercial.value - 1,
        InterestRateType.annual,
        YearSizeType.commercial,
    ) == pytest.approx(1.0)


def test_convert_semiannual_interest_rate():
    assert convert_to_daily_interest_rate(
        2 ** (YearSizeType.commercial.value / 2) - 1,
        InterestRateType.semiannual,
        YearSizeType.commercial,
    ) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "year_size_type,expected",
    [
        (
            YearSizeType.commercial,
            36.7834343,
        ),
        (
            YearSizeType.banker,
            34.9496413,
        ),
    ],
)
def test_convert_interest_rate_daily_to_annual(year_size_type, expected):
    assert convert_interest_rate(
        0.01, InterestRateType.daily, InterestRateType.annual, year_size_type
    ) == pytest.approx(expected)


@pytest.mark.parametrize(
    "month_size, year_size_type, expected",
    [
        (
            None,  # month_size is calculated as year_size / 12
            YearSizeType.commercial,
            0.3534487,
        ),
        (
            30,
            YearSizeType.commercial,
            0.3478489,
        ),
        (
            30,
            YearSizeType.banker,
            0.3478489,
        ),
        (
            None,
            YearSizeType.banker,
            0.3478489,
        ),
    ],
)
def test_convert_interest_rate_daily_to_monthly(month_size, year_size_type, expected):
    assert convert_interest_rate(
        0.01,
        InterestRateType.daily,
        InterestRateType.monthly,
        year_size_type,
        month_size,
    ) == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(
    "year_size_type,expected",
    [
        (
            YearSizeType.commercial,
            0.000261,
        ),
        (
            YearSizeType.banker,
            0.0002648,
        ),
    ],
)
def test_convert_interest_rate_annual_to_daily(year_size_type, expected):
    assert convert_interest_rate(
        0.10, InterestRateType.annual, InterestRateType.daily, year_size=year_size_type
    ) == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(
    "month_size, year_size_type, expected",
    [
        (
            None,  # month_size is calculated as year_size / 12
            YearSizeType.commercial,
            0.0031384,
        ),
        (
            30,
            YearSizeType.banker,
            0.0031821,
        ),
    ],
)
def test_convert_interest_rate_monthly_to_daily(month_size, year_size_type, expected):
    assert convert_interest_rate(
        0.10,
        InterestRateType.monthly,
        InterestRateType.daily,
        year_size=year_size_type,
        month_size=month_size,
    ) == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(
    "month_size, year_size_type, expected",
    [
        (
            None,  # month_size is calculated as year_size / 12
            YearSizeType.commercial,
            2.1384284,
        ),
        (
            30,
            YearSizeType.commercial,
            2.1384284,
        ),
        (
            30,
            YearSizeType.banker,
            2.1384284,
        ),
    ],
)
def test_convert_interest_rate_monthly_to_annual(month_size, year_size_type, expected):
    assert convert_interest_rate(
        0.10,
        InterestRateType.monthly,
        InterestRateType.annual,
        year_size=year_size_type,
        month_size=month_size,
    ) == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("year_size", [YearSizeType.banker, YearSizeType.commercial])
@pytest.mark.parametrize("month_size", [None])
@pytest.mark.parametrize(
    "from_", [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual]
)
@pytest.mark.parametrize(
    "to_", [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual]
)
def test_convert_to_and_back_again(from_, to_, month_size, year_size):

    orig = 0.10

    rate_1 = convert_interest_rate(
        orig,
        from_,
        to_,
        year_size=year_size,
        month_size=month_size,
    )
    rate_2 = convert_interest_rate(
        rate_1,
        to_,
        from_,
        year_size=year_size,
        month_size=month_size,
    )

    assert rate_2 == pytest.approx(orig)


@pytest.mark.parametrize("year_size", [YearSizeType.banker, YearSizeType.commercial])
@pytest.mark.parametrize("month_size", [None])
@pytest.mark.parametrize(
    "from_", [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual]
)
@pytest.mark.parametrize(
    "to_", [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual]
)
@pytest.mark.parametrize(
    "between_",
    [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual],
)
def test_convert_many_times(from_, to_, between_, year_size, month_size):

    orig = 0.10

    rate_1 = convert_interest_rate(
        orig,
        from_,
        between_,
        year_size=year_size,
        month_size=month_size,
    )
    rate_2 = convert_interest_rate(
        rate_1,
        between_,
        to_,
        year_size=year_size,
        month_size=month_size,
    )
    rate_3 = convert_interest_rate(
        rate_2,
        to_,
        from_,
        year_size=year_size,
        month_size=month_size,
    )

    assert rate_3 == pytest.approx(orig)


def test_convert_many_times_mimic_grosup():

    orig = 0.10
    year_size = YearSizeType.banker
    month_size = 30

    rate_1 = convert_interest_rate(
        orig,
        InterestRateType.monthly,
        InterestRateType.annual,
        year_size=year_size,
        month_size=month_size,
    )
    rate_2 = convert_interest_rate(
        rate_1,
        InterestRateType.annual,
        InterestRateType.annual,
        year_size=year_size,
        month_size=month_size,
    )
    rate_3 = convert_interest_rate(
        rate_2,
        InterestRateType.annual,
        InterestRateType.daily,
        year_size=year_size,
        month_size=month_size,
    )

    expected = convert_interest_rate(
        orig,
        InterestRateType.monthly,
        InterestRateType.daily,
        year_size=year_size,
        month_size=month_size,
    )

    assert rate_3 == pytest.approx(expected, rel=1e-5)

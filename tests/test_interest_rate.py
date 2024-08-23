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

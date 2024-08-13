import pytest

from datetime import date

from loan_calculator.loan import Loan
from loan_calculator.interest_rate import YearSizeType


args_ = (
    1000.0,
    0.5,
    date(2020, 1, 1),
    [
        date(2020, 1, 2),
        date(2020, 1, 3),
        date(2020, 1, 4),
        date(2020, 1, 5),
    ],
)


def test_grace_period_exceeds_loan_start():

    for date_ in args_[3]:

        with pytest.raises(ValueError):

            Loan(*args_, grace_period=(date_ - args_[2]).days)


def test_unknown_amortization_schedule():

    with pytest.raises(ValueError):

        Loan(*args_, amortization_schedule_type="foo")


def test_proper_interest_rate_conversion_on_loan_initialization():

    # (1 + 0.5) ** (1 / 360) - 1 ~ 0.0011269264719548922
    assert Loan(
        *args_, year_size=YearSizeType.banker
    ).daily_interest_rate == pytest.approx(
        0.0011269264719548922
    )  # noqa
    # (1 + 0.5) ** (1 / 365) - 1 ~ 0.0011114805470662237
    assert Loan(
        *args_, year_size=YearSizeType.commercial
    ).daily_interest_rate == pytest.approx(
        0.0011114805470662237
    )  # noqa


def test_loan_252():

    loan_252 = Loan(
        10053.25,
        0.2668,
        date(2024, 8, 7),
        year_size=252,
        return_dates=[date(2024, 8, 28), date(2024, 9, 28)],
        count_working_days=True,
        include_end_date=True,
        amortization_schedule_type="progressive-price-schedule",
    )

    assert loan_252.balance[0] == pytest.approx(10053.25)
    assert loan_252.balance[1] == pytest.approx(5049.99, rel=0.0001)
    assert loan_252.balance[2] == pytest.approx(0, rel=0.0001)

    assert loan_252.interest_payments[0] == pytest.approx(152.09, rel=0.0001)
    assert loan_252.interest_payments[1] == pytest.approx(105.33, rel=0.01)

    assert loan_252.balance[1] == loan_252.balance[0] - loan_252.amortizations[0]

    assert loan_252.amortizations[0] == pytest.approx(5003.25, rel=0.0001)
    assert loan_252.amortizations[1] == pytest.approx(5049.99, rel=0.0001)


@pytest.mark.parametrize("principal", range(100, 3000, 100))
@pytest.mark.parametrize("annual_interest_rate", range(5, 99))
def test_loan_252_relations(principal, annual_interest_rate):

    loan_252 = Loan(
        principal,
        annual_interest_rate / 100,
        date(2024, 8, 7),
        year_size=252,
        return_dates=[
            date(2024, 8, 28),
            date(2024, 9, 28),
            date(2024, 10, 28),
            date(2024, 11, 28),
        ],
        count_working_days=True,
        include_end_date=True,
        amortization_schedule_type="progressive-price-schedule",
    )

    assert loan_252.balance[1] == pytest.approx(
        loan_252.balance[0] - loan_252.amortizations[0], 0.0001
    )

    assert loan_252.balance[2] == pytest.approx(
        loan_252.balance[1] - loan_252.amortizations[1], 0.0001
    )
    assert loan_252.balance[3] == pytest.approx(
        loan_252.balance[2] - loan_252.amortizations[2], 0.0001
    )

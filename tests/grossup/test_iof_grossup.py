from datetime import date, timedelta
from tracemalloc import start
from more_itertools import before_and_after
import pytest
from dateutil.relativedelta import relativedelta
from loan_calculator.grossup.iof import IofGrossup
from loan_calculator.grossup.iof_tax import loan_iof
from loan_calculator.interest_rate import InterestRateType
from loan_calculator.loan import Loan
from loan_calculator.utils import count_days_between_dates


@pytest.mark.parametrize("month_size", [30, None])
@pytest.mark.parametrize("year_size", [365, 360, 256])
@pytest.mark.parametrize("principal", [1000, 10000, 100000])
def test_trivial_iof_grossup(principal, year_size, month_size):

    loan = Loan(
        principal,
        1.0,
        date(2020, 1, 1),
        year_size=year_size,
        month_size=month_size,
        return_dates=[date(2020, 1, 2), date(2020, 1, 3)],
    )

    iof_grossup = IofGrossup(
        loan,
        loan.start_date,
        daily_iof_aliquot=0.0,
        complementary_iof_aliquot=0.0,
        service_fee_aliquot=0.0,
    )

    assert iof_grossup.grossed_up_principal == pytest.approx(
        loan.principal, rel=0.01
    )  # noqa
    assert iof_grossup.irr == pytest.approx(
        iof_grossup.base_loan.daily_interest_rate, rel=0.01
    )  # noqa

    assert iof_grossup.grossed_up_loan.year_size == loan.year_size
    assert iof_grossup.grossed_up_loan.daily_interest_rate == loan.daily_interest_rate


def test_iof_grossup_252(loan_252):
    iof_grossup = IofGrossup(
        loan_252,
        loan_252.start_date,
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
        service_fee_aliquot=0.0,
    )

    assert iof_grossup.grossed_up_loan.year_size == loan_252.year_size

    assert iof_grossup.grossed_up_principal == pytest.approx(
        10053.25, rel=0.0001
    )  # noqa


def test_iof_grossup_252_analitical(loan_252):
    iof_grossup = IofGrossup(
        loan_252,
        loan_252.start_date,
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
        service_fee_aliquot=0.0,
        strategy="analytical",
    )

    assert iof_grossup.grossed_up_loan.year_size == loan_252.year_size
    assert iof_grossup.grossed_up_principal == pytest.approx(
        10053.28, rel=0.000001
    )  # noqa


def test_iof_grossup_252_analitical(loan_252):
    iof_grossup = IofGrossup(
        loan_252,
        loan_252.start_date,
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
        service_fee_aliquot=0.0,
        strategy="analytical",
    )

    assert iof_grossup.grossed_up_loan.year_size == loan_252.year_size
    assert iof_grossup.grossed_up_principal == pytest.approx(
        10053.28, rel=0.000001
    )  # noqa


@pytest.mark.parametrize(
    "principal, start_date, expected",
    [
        # (
        #     10000,
        #     date(2024, 8, 27),
        #     10098.87,
        # ),
        # (
        #     11000,
        #     date(2024, 8, 27),
        #     11108.74,
        # ),
        # (
        #     10200,
        #     date(2024, 8, 27),
        #     10300.82,
        # ),
        (
            1000000,
            date(2024, 8, 28),
            1017526.57,
        ),
    ],
)
def test_iof_grossup_presumed(principal, start_date, expected, build_loan):

    loan = build_loan(
        principal,
        0.0799,
        start_date=start_date,
        instalment_number=36,
        month_size=None,
        year_size=360,
        interest_rate_type=InterestRateType.monthly,
    )

    iof_grossup = IofGrossup(
        loan,
        loan.start_date,
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
        service_fee_aliquot=0.0,
        strategy="presumed",
    )

    assert iof_grossup.grossed_up_principal == expected


@pytest.mark.parametrize(
    "interest_rate_type",
    [InterestRateType.monthly, InterestRateType.daily, InterestRateType.annual],
)
@pytest.mark.parametrize("principal", [1000, 11000, 1000])
@pytest.mark.parametrize(
    "month_size,year_size",
    [
        (
            30,
            360,
        ),
        (None, 365),
    ],
)
@pytest.mark.parametrize("interest_rate", [1.0, 1.5, 2.0])
@pytest.mark.parametrize("instalment_number", [3, 6, 9, 12])
def test_iof_grossup_analitical(
    principal,
    interest_rate,
    instalment_number,
    year_size,
    month_size,
    interest_rate_type,
):

    interest_rate = interest_rate / 100
    start_date = date(2024, 8, 7)
    first_payment = date(2024, 8, 28)
    return_dates = [first_payment]
    for a in range(1, instalment_number):
        return_dates.append(return_dates[-1] + relativedelta(months=1))

    loan = Loan(
        principal,
        interest_rate,
        start_date,
        year_size=year_size,
        month_size=month_size,
        return_dates=return_dates,
        count_working_days=True,
        include_end_date=True,
        interest_rate_type=interest_rate_type,
    )

    iof_grossup = IofGrossup(
        loan,
        loan.start_date,
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
        service_fee_aliquot=0.0,
        strategy="analytical",
    )

    assert iof_grossup.grossed_up_loan.year_size == loan.year_size

    iof = loan_iof(
        iof_grossup.grossed_up_loan.principal,
        iof_grossup.grossed_up_loan.amortizations,
        [
            count_days_between_dates(
                iof_grossup.grossed_up_loan.capitalization_start_date, d
            )
            for d in iof_grossup.grossed_up_loan.return_dates
        ],
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
    )

    assert iof_grossup.grossed_up_loan.principal - iof == pytest.approx(
        principal, rel=0.000001
    )  # noqa

    assert iof_grossup.grossed_up_loan.annual_interest_rate == pytest.approx(
        loan.annual_interest_rate
    )
    assert iof_grossup.grossed_up_loan.daily_interest_rate == pytest.approx(
        loan.daily_interest_rate, rel=0.001
    )

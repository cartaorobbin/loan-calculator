from datetime import date, timedelta
from tracemalloc import start
from more_itertools import before_and_after
import pytest
from dateutil.relativedelta import relativedelta
from loan_calculator.grossup.iof import IofGrossup
from loan_calculator.grossup.iof_tax import loan_iof
from loan_calculator.loan import Loan
from loan_calculator.utils import count_days_between_dates


def test_trivial_iof_grossup(loan):

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


@pytest.mark.parametrize("principal", range(1000, 11000, 1000))
@pytest.mark.parametrize("annual_interest_rate", range(5, 95, 5))
@pytest.mark.parametrize("instalment_number", [3, 6, 9, 12])
def test_iof_grossup_252_5_analitical(
    principal, annual_interest_rate, instalment_number
):

    start_date = date(2024, 8, 7)
    first_payment = date(2024, 8, 28)
    return_dates = [first_payment]
    for a in range(1, instalment_number):
        return_dates.append(return_dates[-1] + relativedelta(months=1))

    loan = Loan(
        principal,
        annual_interest_rate / 100,
        start_date,
        year_size=252,
        return_dates=return_dates,
        count_working_days=True,
        include_end_date=True,
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

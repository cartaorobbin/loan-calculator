from datetime import date
from dateutil.relativedelta import relativedelta
from loan_calculator import InterestRateType
from pytest import fixture

from loan_calculator.loan import Loan, RoundStrategy


@fixture()
def loan():
    return Loan(
        100.0,
        1.0,
        date(2020, 1, 1),
        year_size=1,
        return_dates=[date(2020, 1, 2), date(2020, 1, 3)],
    )


@fixture()
def build_loan():

    def inner(
        principal=1000,
        daily_interest_rate=0.01,
        payment_day=3,
        start_date=None,
        instalment_number=3,
        year_size=365,
        month_size=None,
        round_strategy=RoundStrategy.none,
        interest_rate_type=InterestRateType.annual,
    ):

        start_date = start_date or date.today()

        first_payment = date(start_date.year, start_date.month, payment_day)

        if (first_payment - start_date).days < 15:
            first_payment = first_payment + relativedelta(months=1)

        return_dates = [first_payment]
        for a in range(1, instalment_number):
            return_dates.append(return_dates[-1] + relativedelta(months=1))

        return Loan(
            principal,
            daily_interest_rate,
            start_date,
            year_size=year_size,
            month_size=month_size,
            return_dates=return_dates,
            interest_rate_type=interest_rate_type,
            round_strategy=round_strategy,
        )

    return inner


@fixture()
def loan_252():
    return Loan(
        10000.0,
        0.2668,
        date(2024, 8, 7),
        year_size=252,
        return_dates=[date(2024, 8, 28), date(2024, 9, 28)],
        count_working_days=True,
        include_end_date=True,
    )


# @fixture()
# def build_loan():

#     def _build_loan(amortization_schedule_type):

#         return Loan(
#             100.0,
#             1.0,
#             date(2020, 1, 1),
#             year_size=1,
#             return_dates=[date(2020, 1, 2), date(2020, 1, 3)],
#             amortization_schedule_type=amortization_schedule_type,
#         )

#     return _build_loan

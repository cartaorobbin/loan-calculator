

from datetime import date
from loan_calculator.loan import Loan, RoundStrategy


def test_loan_simple_round_strategy():

    loan = Loan(
        1000,
        0.2668,
        date(2024, 8, 7),
        year_size=252,
        return_dates=[date(2024, 8, 28), date(2024, 9, 28)],
        count_working_days=True,
        include_end_date=True,
        amortization_schedule_type="progressive-price-schedule",
        round_strategy=RoundStrategy.simple
    )

    assert loan.amortizations[0] == 497.68
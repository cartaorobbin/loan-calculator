from datetime import date

from loan_calculator.loan import Loan
from loan_calculator.utils import display_summary
from loan_calculator.schedule.base import AmortizationScheduleType


def test_display_summary_shows_expected_loan_summary(capsys):
    """Asserts utils.display_summary outputs expected loan data.

    This raised AttributeError before PR #14 was merged:
    https://github.com/yanomateus/loan-calculator/pull/14

    utils.py:26-27 : display_summary(): - loan.amortizations.tolist(),...
    (AttributeError: 'list' object has no attribute 'tolist')
    """
    loan = Loan(
        principal=10000.00,  # principal
        annual_interest_rate=0.05,  # annual interest rate
        start_date=date(2020, 1, 5),  # start date
        return_dates=[
            date(2020, 2, 12),  # expected return date
            date(2020, 3, 13),  # expected return date
            date(2020, 4, 13),  # expected return date
            date(2020, 5, 12),  # expected return date
            date(2020, 6, 12),  # expected return date
            date(2020, 7, 14),  # expected return date
            date(2020, 8, 15),  # expected return date
        ],
        year_size=365,  # used to convert between annual and daily interest rates # noqa
        grace_period=0,  # number of days for which the principal is not affected by the interest rate  # noqa
        amortization_schedule_type=AmortizationScheduleType.progressive_price_schedule,  # noqa
        # determines how the principal is amortized
    )
    display_summary(loan)

    assert capsys.readouterr().out == (
        "+------------+----------+--------------+--------------+--------------+--------------+\n"  # noqa
        "|    dates   |    days  |    balance   | amortization |   interest   |    payment   |\n"  # noqa
        "+------------+----------+--------------+--------------+--------------+--------------+\n"  # noqa
        "| 2020-01-05 |        0 |     10000.00 |              |              |              |\n"  # noqa
        "| 2020-02-12 |       38 |      8597.47 |      1402.53 |        50.92 |      1453.45 |\n"  # noqa
        "| 2020-03-13 |       68 |      7178.56 |      1418.91 |        34.55 |      1453.45 |\n"  # noqa
        "| 2020-04-13 |       99 |      5754.92 |      1423.64 |        29.81 |      1453.45 |\n"  # noqa
        "| 2020-05-12 |      128 |      4323.82 |      1431.10 |        22.35 |      1453.45 |\n"  # noqa
        "| 2020-06-12 |      159 |      2888.32 |      1435.50 |        17.95 |      1453.45 |\n"  # noqa
        "| 2020-07-14 |      191 |      1447.25 |      1441.07 |        12.38 |      1453.45 |\n"  # noqa
        "| 2020-08-15 |      223 |         0.00 |      1447.25 |         6.20 |      1453.45 |\n"  # noqa
        "+------------+----------+--------------+--------------+--------------+--------------+\n"  # noqa
        "|            |          |              |     10000.00 |       174.17 |     10174.17 |\n"  # noqa
        "+------------+----------+--------------+--------------+--------------+--------------+\n"  # noqa
    )

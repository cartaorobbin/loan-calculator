from datetime import timedelta
import decimal
from enum import Enum
from decimal import Decimal, ROUND_05UP, ROUND_HALF_UP
from loan_calculator.rounds import round_half_up
from loan_calculator.schedule import SCHEDULE_TYPE_CLASS_MAP
from loan_calculator.schedule.base import AmortizationScheduleType
from loan_calculator.interest_rate import (
    convert_interest_rate,
    convert_to_daily_interest_rate,
    InterestRateType,
    YearSizeType,
)
from loan_calculator.utils import count_days_between_dates


class RoundStrategy(Enum):
    none = None
    simple = "simple"
    by_diference = "by_diference"


class Loan(object):
    """Loan.

    Attributes
    ----------
    principal : float, required
        The loan's principal.
    annual_interest_rate : float, required
        The loan's annual interest rate.
    start_date : date, required
        The loan's reference date. This date is usually the one when the
        borrower signed the loan's contract.
    return_dates : list, required
        List of date objects with the expected return dates. These dates
        are usually contractually agreed.
    year_size : int, optional
        The reference year size for converting from annual to daily
        interest rates. (default 365)
    grace_period : int, optional
        The number of days for which the principal is not affected by the
        capitalization process. (default 0)
    amortization_schedule_type : str, optional
        A discriminator string indicating the amortization schedule to be
        adopted. The available schedules are progressive_price_schedule,
        regressive_price_schedule, constant_amortization_schedule.
        (default AmortizationScheduleType.progressive_price_schedule.value).
    """

    def __init__(
        self,
        principal,
        interest_rate,
        start_date,
        return_dates,
        year_size=YearSizeType.commercial,
        grace_period=0,
        amortization_schedule_type=(
            AmortizationScheduleType.progressive_price_schedule.value
        ),
        count_working_days=False,
        include_end_date=False,
        interest_rate_type=InterestRateType.annual,
        month_size=None,
        round_strategy=RoundStrategy.none,
    ):
        """Initialize loan."""

        self.principal = principal

        self.annual_interest_rate = convert_interest_rate(
            interest_rate,
            interest_rate_type,
            InterestRateType.annual,
            year_size,
            month_size,
        )

        self.daily_interest_rate = convert_interest_rate(
            interest_rate,
            interest_rate_type,
            InterestRateType.daily,
            year_size,
            month_size,
        )

        self.start_date = start_date
        self.capitalization_start_date = start_date + timedelta(grace_period)

        self.return_dates = return_dates

        self.year_size = year_size
        self.month_size = month_size
        self.grace_period = grace_period
        self.round_strategy = round_strategy

        self.amortization_schedule_type = AmortizationScheduleType(
            amortization_schedule_type
        )

        self.amortization_schedule_cls = SCHEDULE_TYPE_CLASS_MAP[
            self.amortization_schedule_type
        ]

        if any(
            self.capitalization_start_date >= r_date for r_date in self.return_dates
        ):
            raise ValueError("Grace period can not exceed loan start.")

        self.amortization_schedule = self.amortization_schedule_cls(
            principal,
            self.daily_interest_rate,
            [
                count_days_between_dates(
                    self.capitalization_start_date,
                    r_date,
                    count_working_days=count_working_days,
                    include_end_date=include_end_date,
                )
                for r_date in return_dates
            ],
        )

        self.count_working_days = count_working_days
        self.include_end_date = include_end_date

    @property
    def amortization_function(self):

        def f_(principal, daily_interest_rate, return_days):

            return self.amortization_schedule_cls(
                principal, daily_interest_rate, return_days
            ).amortizations

        return f_

    @property
    def return_days(self):
        return self.amortization_schedule.return_days  # pragma: no cover

    @property
    def balance(self):
        return self.amortization_schedule.balance  # pragma: no cover

    @property
    def due_payments(self):
        return self.amortization_schedule.due_payments  # pragma: no cover

    @property
    def interest_payments(self):
        return self.amortization_schedule.interest_payments  # pragma: no cover

    @property
    def amortizations(self):
        if self.round_strategy == RoundStrategy.simple:
            return [
                round_half_up(amortization, 2)
                for amortization in self.amortization_schedule.amortizations
            ]
        return self.amortization_schedule.amortizations  # pragma: no cover

    @property
    def total_amortization(self):
        return self.amortization_schedule.total_amortization  # pragma: no cover

    @property
    def total_interest(self):
        return self.amortization_schedule.total_interest  # pragma: no cover

    @property
    def total_paid(self):
        return self.amortization_schedule.total_paid  # pragma: no cover



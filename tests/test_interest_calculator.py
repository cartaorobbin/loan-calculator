from datetime import date, timedelta
from loan_calculator import InterestRateType, YearSizeType
import pytest

from loan_calculator.loan import Loan, AmortizationScheduleType
from loan_calculator.interest_calculator import calculate_interest_rate, calculate_iof_grossup_interest_rate
from loan_calculator.grossup.iof import IofGrossup
from loan_calculator.schedule.base import AmortizationScheduleType
from dateutil.relativedelta import relativedelta


def test_calculate_interest_rate_from_excel():
    """Test that calculate_interest_rate returns correct rate for given instalment."""
    # Test case parameters
    principal = 10000.0

    start_date = date(2024, 8, 7)
    first_due_date = date(2024, 8, 25)
    term = 3
    fixed_rate = 0.04
    iof_strategy = "presumed"

    instalment = (principal * (1 + fixed_rate)) / term

    due_dates = []
    for i in range(term):
        due_dates.append(first_due_date + relativedelta(months=i))

    # Calculate interest rate
    rate = calculate_iof_grossup_interest_rate(principal, instalment, start_date, due_dates,
                                               strategy=iof_strategy, daily_iof_aliquot=0.000041,
                                               )

    # Create a loan with the calculated rate to verify
    base_loan = Loan(
        principal=principal,
        interest_rate=rate,
        start_date=start_date,
        return_dates=due_dates,
        amortization_schedule_type=AmortizationScheduleType.progressive_price_schedule,
    )

    grossup = IofGrossup(
        base_loan=base_loan,
        reference_date=start_date,
        daily_iof_aliquot=0.000041,
        strategy=iof_strategy,
    )

    loan = grossup.grossed_up_loan

    # The first instalment should match our target instalment
    calculated_instalment = float(loan.due_payments[0])
    assert abs(calculated_instalment - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {calculated_instalment} "
        f"with rate {rate:.2%}"
    )
    assert due_dates == [date(2024, 8, 25), date(
        2024, 9, 25), date(2024, 10, 25)]
    assert loan.return_days == [18, 49, 79]
    assert round(loan.due_payments[0], 2) == 3466.67
    assert rate == 0.2676


@pytest.mark.parametrize("instalment", [1500, 1600, 1700, 1800])
def test_calculate_interest_rate(instalment):
    """Test that calculate_interest_rate returns correct rate for given instalment."""
    # Test case parameters
    principal = 10000.0
    start_date = date(2020, 1, 5)  # Start date before first payment
    due_dates = [
        date(2020, 2, 12),
        date(2020, 3, 13),
        date(2020, 4, 13),
        date(2020, 5, 12),
        date(2020, 6, 12),
        date(2020, 7, 14),
        date(2020, 8, 15),
    ]

    # Calculate interest rate
    rate = calculate_interest_rate(
        principal, instalment, start_date, due_dates)

    # Create a loan with the calculated rate to verify
    loan = Loan(
        principal=principal,
        interest_rate=rate,
        start_date=start_date,
        return_dates=due_dates,
        amortization_schedule_type=AmortizationScheduleType.progressive_price_schedule,
    )

    # The first instalment should match our target instalment
    calculated_instalment = float(loan.due_payments[0])
    assert abs(calculated_instalment - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {calculated_instalment} "
        f"with rate {rate:.2%}"
    )


@pytest.mark.parametrize("instalment", [1500, 1600, 1700, 1800])
@pytest.mark.parametrize("year_size", [YearSizeType.banker, YearSizeType.commercial])
@pytest.mark.parametrize("interest_type", [InterestRateType.annual, InterestRateType.monthly])
@pytest.mark.parametrize("amortization_schedule_type", [
    AmortizationScheduleType.progressive_price_schedule,
    AmortizationScheduleType.constant_amortization_schedule,
    AmortizationScheduleType.progressive_price_schedule,
    AmortizationScheduleType.regressive_price_schedule,
    AmortizationScheduleType.constant_amortization_schedule,
]
)
def test_calculate_interest_rate_different_year_sizes_and_interest_type(instalment, year_size, interest_type, amortization_schedule_type):
    """Test that calculate_interest_rate returns correct rate for given instalment."""
    # Test case parameters
    principal = 10000.0
    start_date = date(2020, 1, 5)  # Start date before first payment
    due_dates = [
        date(2020, 2, 12),
        date(2020, 3, 13),
        date(2020, 4, 13),
        date(2020, 5, 12),
        date(2020, 6, 12),
        date(2020, 7, 14),
        date(2020, 8, 15),
    ]

    # Calculate interest rate
    rate = calculate_interest_rate(
        principal,
        instalment,
        start_date,
        due_dates,
        year_size=year_size,
        interest_rate_type=interest_type,
        amortization_schedule_type=amortization_schedule_type,
    )

    # Create a loan with the calculated rate to verify
    loan = Loan(
        principal=principal,
        interest_rate=rate,
        start_date=start_date,
        return_dates=due_dates,
        amortization_schedule_type=amortization_schedule_type,
        year_size=year_size,
        interest_rate_type=interest_type,
    )

    # The first instalment should match our target instalment
    calculated_instalment = float(loan.due_payments[0])
    assert abs(calculated_instalment - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {calculated_instalment} "
        f"with rate {rate:.2%}"
    )


@pytest.mark.parametrize("strategy", ["presumed", "numerical"])
@pytest.mark.parametrize("daily_iof_aliquot", [0.000041, 0.000082])
@pytest.mark.parametrize("instalment", [1500, 1600, 1700, 1800])
@pytest.mark.parametrize("net_principal", [15000.0])
def test_calculate_iof_grossup_interest_rate(strategy, daily_iof_aliquot, instalment, net_principal):
    """Test that calculate_iof_grossup_interest_rate returns correct rate for given instalment."""
    # Test case parameters
    start_date = date(2020, 1, 5)  # Start date before first payment
    due_dates = [
        date(2020, 2, 12),
        date(2020, 3, 13),
        date(2020, 4, 13),
        date(2020, 5, 12),
        date(2020, 6, 12),
        date(2020, 7, 14),
        date(2020, 8, 15),
    ]

    # Calculate interest rate with IOF grossup
    rate = calculate_iof_grossup_interest_rate(
        net_principal=net_principal,
        instalment_value=instalment,
        start_date=start_date,
        due_dates=due_dates,
        daily_iof_aliquot=daily_iof_aliquot,
        strategy=strategy
    )

    # Create a base loan with the calculated rate
    base_loan = Loan(
        principal=net_principal,
        interest_rate=rate,
        start_date=start_date,
        return_dates=due_dates,
        amortization_schedule_type=AmortizationScheduleType.progressive_price_schedule,

    )

    # Apply IOF grossup
    grossup = IofGrossup(
        base_loan=base_loan,
        reference_date=start_date,
        daily_iof_aliquot=daily_iof_aliquot,
        strategy=strategy,
    )

    # Get the grossed up loan
    grossed_up_loan = grossup.grossed_up_loan

    # Verify that the first instalment matches the target value
    assert abs(grossed_up_loan.due_payments[0] - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {grossed_up_loan.due_payments[0]} "
        f"with rate {rate:.2%}"
    )


@pytest.mark.parametrize("instalment_number", range(2, 20))
@pytest.mark.parametrize("rate", range(1, 15))
@pytest.mark.parametrize("net_principal", range(1000, 100000, 3000))
def test_calculate_iof_grossup_interest_rate_fixed_rate(rate, net_principal, instalment_number):
    """Test that calculate_iof_grossup_interest_rate returns correct rate for given instalment."""
    # Test case parameters
    start_date = date(2020, 1, 5)  # Start date before first payment
    due_dates = []
    rate = rate / 100

    instalment = (net_principal * (1 + rate)) / instalment_number

    for i in range(instalment_number):
        due_dates.append(start_date + timedelta(days=i+1 * 30))

    # Calculate interest rate with IOF grossup
    new_rate = calculate_iof_grossup_interest_rate(
        net_principal=net_principal,
        instalment_value=instalment,
        start_date=start_date,
        due_dates=due_dates
    )

    # Create a base loan with the calculated rate
    base_loan = Loan(
        principal=net_principal,
        interest_rate=new_rate,
        start_date=start_date,
        return_dates=due_dates,
        amortization_schedule_type=AmortizationScheduleType.progressive_price_schedule,
    )

    # Apply IOF grossup
    grossup = IofGrossup(
        base_loan=base_loan,
        reference_date=start_date
    )

    # Get the grossed up loan
    grossed_up_loan = grossup.grossed_up_loan

    # breakpoint()
    # Verify that the first instalment matches the target value
    assert abs(grossed_up_loan.due_payments[0] - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {grossed_up_loan.due_payments[0]} "
        f"with rate {rate:.2%}"
    )

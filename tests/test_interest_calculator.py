from datetime import date, timedelta
import pytest

from loan_calculator.loan import Loan, AmortizationScheduleType
from loan_calculator.interest_calculator import calculate_interest_rate, calculate_iof_grossup_interest_rate
from loan_calculator.grossup.iof import IofGrossup
from loan_calculator.schedule.base import AmortizationScheduleType


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
    rate = calculate_interest_rate(principal, instalment, start_date, due_dates)

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
@pytest.mark.parametrize("net_principal", [15000.0])
def test_calculate_iof_grossup_interest_rate(instalment, net_principal):
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
        due_dates=due_dates
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
        reference_date=start_date
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
    rate = calculate_iof_grossup_interest_rate(
        net_principal=net_principal,
        instalment_value=instalment,
        start_date=start_date,
        due_dates=due_dates
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
        reference_date=start_date
    )

    # Get the grossed up loan
    grossed_up_loan = grossup.grossed_up_loan

    # Verify that the first instalment matches the target value
    assert abs(grossed_up_loan.due_payments[0] - instalment) < 0.01, (
        f"Expected instalment {instalment}, but got {grossed_up_loan.due_payments[0]} "
        f"with rate {rate:.2%}"
    )

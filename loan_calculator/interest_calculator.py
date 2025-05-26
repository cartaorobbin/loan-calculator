from datetime import date
from scipy.optimize import fsolve
from loan_calculator.loan import Loan, AmortizationScheduleType
from loan_calculator.interest_rate import InterestRateType, YearSizeType
from loan_calculator.grossup.iof import IofGrossup


def calculate_interest_rate(
    principal: float,
    instalment_value: float,
    start_date: date,
    due_dates: list,
    interest_rate_type: InterestRateType = InterestRateType.annual,
    year_size: YearSizeType = YearSizeType.commercial,
    amortization_schedule_type: AmortizationScheduleType = AmortizationScheduleType.progressive_price_schedule,
) -> float:
    """
    Calculate the interest rate that will generate a loan with given parameters.

    Parameters
    ----------
    principal : float, required
        The initial loan amount
    instalment_value : float
        The fixed instalment value to be paid
    due_dates : list
        List of datetime.date objects representing payment dates
    start_date : date
        The date the loan starts
    interest_rate_type : InterestRateType, optional
        The type of interest rate (default is annual)
    year_size : YearSizeType, optional
        The year size type (default is commercial)
    amortization_schedule_type : AmortizationScheduleType, optional
        The amortization schedule type (default is progressive price schedule)

    Returns
    -------
    float
        The calculated annual interest rate as a decimal (e.g., 0.12 for 12%)
    """
    def objective(rate):
        # Create a loan with the current rate guess
        loan = Loan(
            principal=principal,
            interest_rate=float(rate[0]),
            start_date=start_date,
            return_dates=due_dates,
            interest_rate_type=interest_rate_type,
            year_size=year_size,
            amortization_schedule_type=amortization_schedule_type.value
        )

        # Get the calculated instalment value from the loan
        calculated_instalment = loan.due_payments[0]

        # Return the difference between calculated and target instalment
        return [float(calculated_instalment - instalment_value)]

    # Initial guess for annual interest rate (10%)
    initial_guess = [0.10]

    # Solve for the interest rate
    result = fsolve(objective, initial_guess)

    return float(result[0])


def calculate_iof_grossup_interest_rate(
    net_principal: float,
    instalment_value: float,
    start_date: date,
    due_dates: list,
    daily_iof_aliquot: float = 0.000082,
    complementary_iof_aliquot: float = 0.0038,
    service_fee_aliquot: float = 0.0,
    year_size: YearSizeType = YearSizeType.commercial,
    month_size: int = 30,
    amortization_schedule_type: AmortizationScheduleType = AmortizationScheduleType.progressive_price_schedule,
    strategy: str = "numerical",
) -> float:
    """
    Calculate the interest rate for a loan with IOF tax grossup that will generate
    the desired instalment value.

    Parameters
    ----------
    net_principal : float, required
        The net principal amount (before IOF grossup)
    instalment_value : float
        The fixed instalment value to be paid
    start_date : date
        The date the loan starts
    due_dates : list
        List of datetime.date objects representing payment dates
    daily_iof_aliquot : float, optional
        Daily IOF tax aliquot (default 0.000082)
    complementary_iof_aliquot : float, optional
        Complementary IOF tax aliquot (default 0.0038)
    service_fee_aliquot : float, optional
        Service fee aliquot (default 0.0)

    Returns
    -------
    float
        The calculated annual interest rate as a decimal (e.g., 0.12 for 12%)
    """
    def objective(rate):
        # Create a base loan with the current rate guess
        base_loan = Loan(
            principal=net_principal,
            interest_rate=float(rate[0]),
            start_date=start_date,
            return_dates=due_dates,
            interest_rate_type=InterestRateType.annual,
            year_size=year_size,
            amortization_schedule_type=amortization_schedule_type
        )

        # Apply IOF grossup
        grossup = IofGrossup(
            base_loan=base_loan,
            reference_date=start_date,
            daily_iof_aliquot=daily_iof_aliquot,
            complementary_iof_aliquot=complementary_iof_aliquot,
            service_fee_aliquot=service_fee_aliquot,
            strategy=strategy
        )

        # Get the grossed up loan
        grossed_up_loan = grossup.grossed_up_loan

        # Get the calculated instalment value from the loan
        calculated_instalment = grossed_up_loan.due_payments[0]

        # Return the difference between calculated and target instalment
        return [float(calculated_instalment - instalment_value)]

    # Initial guess for annual interest rate (10%)
    initial_guess = [0.10]

    # Solve for the interest rate
    result = fsolve(objective, initial_guess)

    return float(result[0])

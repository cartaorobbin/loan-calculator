from decimal import Decimal, ROUND_HALF_UP
import datetime


def display_summary(loan, reference_date=None):
    """Display a legible summary of a loan.

    Parameters
    ----------
    loan : Loan, required
        Loan to be displayed.
    reference_date : date, optional
        Date object with the date to consider as reference when calculating
        the values of the column `day` in the function's output. (default None)
    """

    reference_date = reference_date or loan.start_date

    dates = [reference_date] + loan.return_dates

    lines = list(
        zip(
            dates,
            map(lambda d: (d - reference_date).days, dates),
            loan.balance,
            [""] + loan.amortizations,
            [""] + loan.interest_payments,
            [""] + loan.due_payments,
        )
    )

    separator = (
        "+------------+----------+--------------"
        "+--------------+--------------+--------------+"
    )

    header = (
        "|    dates   |    days  |    balance   "
        "| amortization |   interest   |    payment   |"
    )

    trailing_line = (
        "| {:>8} | {:>8d} | {:>12.2f} |              "
        "|              |              |".format(
            *[lines[0][0].isoformat()] + list(lines[0][1:3])
        )
    )

    body_line = "| {:>8} | {:>8d} | {:>12.2f} " "| {:>12.2f} | {:>12.2f} | {:>12.2f} |"

    footer_line = (
        "|            |          |              "
        "| {:>12.2f} | {:>12.2f} | {:>12.2f} |".format(
            loan.total_amortization, loan.total_interest, loan.total_paid
        )
    )

    summary = "\n".join(
        [
            separator,
            header,
            separator,
            trailing_line,
        ]
        + [
            body_line.format(
                line[0].isoformat(),
                line[1],
                *list(
                    map(
                        lambda n: Decimal(n).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        ),
                        line[2:],
                    )
                )
            )
            for line in lines[1:]
        ]
        + [
            separator,
            footer_line,
            separator,
        ]
    )

    print(summary)


def count_days_between_dates(
    start_date: datetime.date,
    end_date: datetime.date,
    count_working_days: bool = False,
    exclude_holidays: bool = False,
    include_end_date: bool = False,
    country: str = "US",
) -> int:
    """
    Count the number of days between two dates.

    Args:
    start_date (datetime.date): The start date.
    end_date (datetime.date): The end date.
    count_working_days (bool): If True, count only working days. Defaults to False.
    exclude_holidays (bool): If True, exclude public holidays from working days. Defaults to False.
    country (str): Country code for public holidays. Used only if exclude_holidays is True. Defaults to 'US'.

    Returns:
    int: The number of days between the two dates, based on the specified parameters.
    """
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    # Initialize a counter
    day_count = 0

    # If counting working days
    if count_working_days:
        # Generate the list of public holidays if needed
        if exclude_holidays:
            import holidays

            country_holidays = holidays.CountryHoliday(country)
        else:
            country_holidays = set()

        # Iterate through each date in the range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a working day (weekday)
            if current_date.weekday() < 5 and current_date not in country_holidays:
                day_count += 1
            current_date += datetime.timedelta(days=1)

    # If counting all days
    else:
        day_count = (end_date - start_date).days  # +1 to include the end_date itself
        if include_end_date:
            day_count += 1

    return day_count


# Example usage:
# start_date = datetime.date(2024, 8, 1)
# end_date = datetime.date(2024, 8, 10)
# print(count_days_between_dates(start_date, end_date, count_working_days=True, exclude_holidays=True))

"""Provide functions implementation of different grossup cases.

The grossup of a net principal is an augmented principal value whose net
value corresponds to the given net principal. The net value of a principal
is the one obtained after subtracting due taxes and service fees according
to very specific mathematical rule.
"""

from copy import copy
from loan_calculator.grossup.iof_tax import loan_iof
from loan_calculator.loan import Loan
from loan_calculator.utils import count_days_between_dates


def br_iof_regressive_price_grossup(
    net_principal,
    daily_interest_rate,
    daily_iof_fee,
    complementary_iof_fee,
    return_days,
    service_fee,
    **kwargs,
):
    """Calculate the grossup of the given principal.

    This function implements a grossup for which
    - the principal is amortized according to a regressive Price schedule,
    - the principal and the payments are taxed by IOF,
    - a fee is calculated over the principal.

    If :math:`s` is the principal, :math:`d` is the daily interest rate,
    :math:`I^*` is the daily IOF fee, :math:`I^{**}` is the complementary IOF
    fee, :math:`g` is the service fee and :math:`(n_1,n_2,\\ldots,n_k)` is the
    vector with the return dates, then the grossup is given by

    .. math::

        \\mathrm{GROSSUP}\\ (s, d, I^*, I^{**}, (n_1,\\ldots,n_k), g)
        =\\frac{s}{1 - \\alpha - I^{**} - g},

    where

    .. math::

        \\alpha := \\frac{
        \\displaystyle\\sum_{j=1}^k\\frac{\\min(n_{k-j+1}\\ I^*, 0.015)}
        {(1+d)^{n_j}}} {\\displaystyle\\sum_{j=1}^k\\frac{1}{(1+d)^{n_j}}}.

    Parameters
    ----------
    net_principal : float, required
        The principal to be "grossed up".
    daily_interest_rate : float, required
        The rate at which the principal grows over time.
    daily_iof_fee : float, required
        Daily tax due to brazilian tax IOF.
    complementary_iof_fee : float, required
        Complementary tax due to brazilian tax IOF.
    return_days : list, required
        List containing the number of days since the start reference date.
    service_fee : float, optional
        Eventual service fee. It is assumed to be an aliquot
        applied on the principal


    Returns
    -------
    The grossed up principal.
    """

    # variables are renamed in order to make the math more explicit
    p = net_principal
    d = daily_interest_rate
    d_iof = daily_iof_fee
    c_iof = complementary_iof_fee
    s_fee = service_fee
    pmt_days = return_days

    # TODO:think of a better name for this coefficient
    # transport coefficient
    transport_coef = sum(1.0 / (1 + d) ** n for n in pmt_days)

    # iof coefficient
    iof_coef = sum(float(min(n * d_iof, 0.015)) / (1 + d) ** n for n in pmt_days)

    return p / (1 - (iof_coef / transport_coef) - c_iof - s_fee)


def br_iof_progressive_price_grossup(
    net_principal,
    daily_interest_rate,
    daily_iof_fee,
    complementary_iof_fee,
    return_days,
    service_fee,
    **kwargs,
):
    """Calculate the grossup of the principal for the given parameters.

    This implements a grossup for which

    - the principal is amortized according to a progressive Price schedule,
    - the principal is taxed, as well as its payments, by IOF
    - a fee is applied over the principal

    If :math:`s` is the principal, :math:`d` is the daily interest rate,
    :math:`I^*` is the daily IOF fee, :math:`I^{**}` is the complementary IOF
    fee, :math:`g` is the service fee and :math:`(n_1,n_2,\\ldots,n_k)` is the
    vector with the return dates, then the grossup is given by

    .. math::
        \\mathrm{GROSSUP}(s, d, I^*, I^{**}, (n_1,\\ldots,n_k), g) =
        \\frac{s}{1 - \\alpha - I^{**} - g },

    where

    .. math::
        \\alpha :=
        \\frac
        {
        \\displaystyle
        \\sum_{j=1}^k\\frac{\\min(n_j\\ I^*, 0.015)}{(1+d)^{n_j}}}
        {
        \\displaystyle\\sum_{j=1}^k\\frac{1}{(1+d)^{n_j}}}.


    Parameters
    ----------
    net_principal : float, required
        The principal to be "grossed up".
    daily_interest_rate : float, required
        The rate at which the principal grows over time.
    daily_iof_fee : float, required
        Daily tax due to brazilian tax IOF.
    complementary_iof_fee : float, required
        Complementary tax due to brazilian tax IOF.
    return_days : list, required
        List containing the number of days since the start reference date.
    service_fee : float, optional
        Eventual service fee. It is assumed to be an aliquot
        applied on the principal

    Returns
    -------
    The grossed up principal.
    """

    # variables are renamed in order to make the math more explicit
    p = net_principal
    d = daily_interest_rate
    d_iof = daily_iof_fee
    c_iof = complementary_iof_fee
    s_fee = service_fee
    pmt_days = return_days

    # TODO:think of a better name for this coefficient
    # transport coefficient
    transport_coef = sum(1.0 / (1 + d) ** n for n in pmt_days)

    # iof coefficient
    iof_coef = sum(float(min(n * d_iof, 0.015)) / (1 + d) ** n for n in pmt_days[::-1])

    return p / (1 - (iof_coef / transport_coef) - c_iof - s_fee)


def br_iof_constant_amortization_grossup(
    net_principal,
    daily_interest_rate,
    daily_iof_fee,
    complementary_iof_fee,
    return_days,
    service_fee,
    **kwargs,
):
    """Calculate the grossup of the principal and given parameters.

    This implements a grossup for which

    - the principal is amortized according to a constant amortization
      schedule
    - the principal and the payments are taxed with IOF,
    - a service fee is applied over the principal.

    If :math:`s` is the principal, :math:`d` is the daily interest rate,
    :math:`I^*` is the daily IOF fee, :math:`I^{**}` is the complementary IOF
    fee, :math:`g` is the service fee and :math:`(n_1,n_2,\\ldots,n_k)` is the
    vector with the return dates, then the grossup is given by

    .. math::

        \\mathrm{GROSSUP}(s, d, I^*, I^{**}, (n_1,\\ldots,n_k), g) =
        \\frac{s} {1 - \\alpha - I^{**} - g},

    where

    .. math::

        \\alpha :=
        \\frac{1}{k}
        \\frac{\\displaystyle\\sum_{j=1}^k \\min(n_j\\ I^*, 0.015)}
              {\\displaystyle\\sum_{j=1}^k\\frac{1}{(1+d)^{n_j}}}.
    """

    # variables are renamed to make the math more explicit
    p = net_principal
    d = daily_interest_rate
    d_iof = daily_iof_fee
    c_iof = complementary_iof_fee
    s_fee = service_fee
    pmt_days = return_days

    # TODO:think of a better name for this coefficient
    # transport coefficient
    transport_coef = sum(1.0 / (1 + d) ** n for n in pmt_days)

    # iof coefficient
    iof_coef = sum(float(min(n * d_iof, 0.015)) / len(pmt_days) for n in pmt_days)

    return p / (1 - (iof_coef / transport_coef) - c_iof - s_fee)


def br_iof_progressive_price_grossup_analytical(
    net_principal,
    daily_interest_rate,
    daily_iof_fee,
    complementary_iof_fee,
    return_days,
    service_fee,
    return_dates,
    amortizations,
    capitalization_start_date,
    annual_interest_rate,
    year_size,
    count_working_days,
    include_end_date,
    **kwargs,
):

    from scipy.optimize import fsolve

    def _inner(
        net_principal,
        target_principal,
        daily_interest_rate,
        daily_iof_fee,
        complementary_iof_fee,
        return_days,
        service_fee,
        return_dates,
        amortizations,
        capitalization_start_date,
        annual_interest_rate,
        year_size,
        count_working_days,
        include_end_date,
    ):

        loan = Loan(
            principal=net_principal[0],
            interest_rate=annual_interest_rate,
            return_dates=return_dates,
            start_date=capitalization_start_date,
            year_size=year_size,
            count_working_days=count_working_days,
            include_end_date=include_end_date,
        )

        iof = loan_iof(
            loan.principal,
            loan.amortizations,
            [
                count_days_between_dates(loan.capitalization_start_date, d)
                for d in loan.return_dates
            ],
            daily_iof_aliquot=daily_iof_fee,
            complementary_iof_aliquot=complementary_iof_fee,
        )

        return loan.principal - iof - target_principal

    iof = loan_iof(
        net_principal,
        amortizations,
        [count_days_between_dates(capitalization_start_date, d) for d in return_dates],
        daily_iof_aliquot=0.000041,
        complementary_iof_aliquot=0.0038,
    )

    principal = fsolve(
        _inner,
        net_principal + iof,
        args=(
            net_principal,
            daily_interest_rate,
            daily_iof_fee,
            complementary_iof_fee,
            return_days,
            service_fee,
            return_dates,
            amortizations,
            capitalization_start_date,
            annual_interest_rate,
            year_size,
            count_working_days,
            include_end_date,
        ),
    )

    return float(principal[0])

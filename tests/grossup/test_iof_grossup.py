import pytest

from loan_calculator.grossup.iof import IofGrossup


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
    assert iof_grossup.grossed_up_loan.total_interest == pytest.approx(
        257.34, rel=0.01
    )  # noqa
    assert iof_grossup.grossed_up_loan.due_payments[0] == pytest.approx(
        5155.32, rel=0.01
    )  # noqa
    assert iof_grossup.grossed_up_loan.total_amortization == pytest.approx(
        10053.67, rel=0.01
    )  # noqa
    assert iof_grossup.grossed_up_loan.total_paid == pytest.approx(
        10310.64, rel=0.01
    )  # noqa

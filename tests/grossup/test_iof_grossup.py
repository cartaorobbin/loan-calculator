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

    assert iof_grossup.grossed_up_principal == pytest.approx(10053.25, rel=0.0001)  # noqa


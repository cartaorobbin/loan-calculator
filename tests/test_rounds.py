from loan_calculator.rounds import arredmultb


def test_arredmultb():

    assert arredmultb(16.1057755, 2) == 16.10
    assert arredmultb(9.2902503, 2) == 9.29
    assert arredmultb(11.6071394, 2) == 11.60

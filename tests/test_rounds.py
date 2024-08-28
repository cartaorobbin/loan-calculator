from loan_calculator.rounds import arredmultb


def test_arredmultb():

    assert arredmultb(16.1057755, 0.01) == 16.10
    assert arredmultb(9.2902503, 0.01) == 9.29
    assert arredmultb(11.6071394, 0.01) == 11.60

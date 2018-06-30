import pytest

import program
from safe_eval import safe_eval


def test_safe_eval_allowed_arithmetic():
    assert safe_eval("1+1") == 2
    assert safe_eval("9 * 10") == 90
    assert safe_eval("2 + (-5)") == -3
    assert safe_eval("3-2") == 1


def test_safe_eval_allowed_logic():
    assert safe_eval("1>0")
    assert safe_eval("0<1")
    assert safe_eval("-1<0")
    assert safe_eval("0>-1")
    assert safe_eval("5<=5")
    assert safe_eval("5>=5")

    assert not safe_eval("1<0")
    assert not safe_eval("0>1")
    assert not safe_eval("-10>1")
    assert not safe_eval("2>=3")
    assert not safe_eval("5<=-2")


def test_disallowed_arithmetic():
    with pytest.raises(TypeError):
        safe_eval("10/2")


def test_disallowed_logic():
    with pytest.raises(TypeError):
        safe_eval("5==2")


def test_get_address():
    definition = program.Definition(2, [16, 64], 6144)
    indices = ["{i} + 1", "{i} * 4"]
    expression = program.Expression(definition, indices)
    assert expression.get_address({"i": 1}) == 6408
    assert expression.get_address({"i": 5}) == 6952

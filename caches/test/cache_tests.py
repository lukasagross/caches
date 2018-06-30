import pytest

from caches import cache
from caches import program
from caches.safe_eval import safe_eval


def test_allowed_arithmetic():
    assert safe_eval("1+1") == 2
    assert safe_eval("9 * 10") == 90
    assert safe_eval("2 + (-5)") == -3
    assert safe_eval("3-2") == 1


def test_allowed_logic():
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


def test_simple_program():
    double_def = program.Definition(8, [32, 32], 0)

    expressions = [
        program.Expression(double_def, ["{i}", "{j}"]),
        program.Expression(double_def, ["{i}", "{j}+1"]),
        program.Expression(double_def, ["{i}", "{j}+2"]),
        program.Expression(double_def, ["{i}", "{j}+3"])
    ]

    statements = [program.Statement(expression) for expression in expressions]

    body = program.Body(statements)
    inner_loop = program.Loop("j", 0, "{j}<29", "{j}+4", body)
    outer_loop = program.Loop("i", 0, "{i}<32", "{i}+1", inner_loop)
    prog = program.Body()
    prog.add_statement(outer_loop)
    prog_cache = cache.Cache(32, 1, 64)

    prog.run(prog_cache)

    assert prog_cache.accesses == 1024
    assert prog_cache.misses == 128
    assert prog_cache.write_misses == 128


def test_simple_program2():
    double_def = program.Definition(8, [32, 32], 0)
    short_def = program.Definition(2, [32, 128], double_def.end_address)

    expressions = [
        program.Expression(double_def, ["{i}", "{j}"]),
        program.Expression(double_def, ["{i}", "{j}+1"]),
        program.Expression(double_def, ["{i}", "{j}+2"]),
        program.Expression(double_def, ["{i}", "{j}+3"]),
        program.Expression(short_def, ["{i}", "{j}"]),
        program.Expression(short_def, ["{i}", "{j}+3"])
    ]

    statements = [program.Statement(expression) for expression in expressions]

    body = program.Body(statements)
    inner_loop = program.Loop("j", 0, "{j}<29", "{j}+4", body)
    outer_loop = program.Loop("i", 0, "{i}<32", "{i}+1", inner_loop)
    prog = program.Body()
    prog.add_statement(outer_loop)
    prog_cashe = cache.Cache(32, 1, 64)

    prog.run(prog_cashe)

    assert prog_cashe.accesses == 1536
    assert prog_cashe.misses == 224
    assert prog_cashe.write_misses == 224

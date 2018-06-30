import unittest

import cache
import program
from safe_eval import safe_eval


class TestSafeEval(unittest.TestCase):
    def test_allowed_arithmetic(self):
        self.assertEqual(safe_eval("1+1"), 2)
        self.assertEqual(safe_eval("9 * 10"), 90)
        self.assertEqual(safe_eval("2 + (-5)"), -3)
        self.assertEqual(safe_eval("3-2"), 1)

    def test_allowed_logic(self):
        self.assertTrue(safe_eval("1>0"))
        self.assertTrue(safe_eval("0<1"))
        self.assertTrue(safe_eval("-1<0"))
        self.assertTrue(safe_eval("0>-1"))
        self.assertTrue(safe_eval("5<=5"))
        self.assertTrue(safe_eval("5>=5"))

        self.assertFalse(safe_eval("1<0"))
        self.assertFalse(safe_eval("0>1"))
        self.assertFalse(safe_eval("-10>1"))
        self.assertFalse(safe_eval("2>=3"))
        self.assertFalse(safe_eval("5<=-2"))

    def test_disallowed_arithmetic(self):
        with self.assertRaises(TypeError):
            safe_eval("10/2")

    def test_disallowed_logic(self):
        with self.assertRaises(TypeError):
            safe_eval("5==2")


class TestExpression(unittest.TestCase):
    def setUp(self):
        definition = program.Definition(2, [16, 64], 6144)
        indices = ["{i} + 1", "{i} * 4"]
        self.expression = program.Expression(definition, indices)

    def test_get_address(self):
        self.assertEqual(self.expression.get_address({"i": 1}), 6408)
        self.assertEqual(self.expression.get_address({"i": 5}), 6952)

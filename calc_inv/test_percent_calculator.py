import unittest

from percent_calculator import CalculatorModel


class CalculatorPercentTests(unittest.TestCase):
    def calculate(self, left: str, operator: str, right: str, percent: bool) -> str:
        model = CalculatorModel()
        for digit in left:
            model.input_digit(digit)
        model.set_operator(operator)
        for digit in right:
            model.input_digit(digit)
        if percent:
            model.apply_percent()
        model.equals()
        return model.display

    def test_addition_uses_percent_of_left_operand(self) -> None:
        self.assertEqual(self.calculate("200", "+", "10", percent=True), "220")

    def test_multiplication_uses_percent_as_fraction(self) -> None:
        self.assertEqual(self.calculate("200", "×", "10", percent=True), "20")

    def test_subtraction_uses_percent_of_left_operand(self) -> None:
        self.assertEqual(self.calculate("200", "-", "10", percent=True), "180")

    def test_division_uses_percent_as_fraction(self) -> None:
        self.assertEqual(self.calculate("200", "÷", "10", percent=True), "2000")

    def test_addition_without_percent_is_unchanged(self) -> None:
        self.assertEqual(self.calculate("200", "+", "10", percent=False), "210")

    def test_subtraction_without_percent_is_unchanged(self) -> None:
        self.assertEqual(self.calculate("200", "-", "10", percent=False), "190")

    def test_multiplication_without_percent_is_unchanged(self) -> None:
        self.assertEqual(self.calculate("200", "×", "10", percent=False), "2000")

    def test_division_without_percent_is_unchanged(self) -> None:
        self.assertEqual(self.calculate("200", "÷", "10", percent=False), "20")

    def test_percent_requires_a_second_operand_after_an_operator(self) -> None:
        model = CalculatorModel()
        model.input_digit("2")
        model.set_operator("+")

        with self.assertRaises(ValueError):
            model.apply_percent()

    def test_division_by_zero_raises(self) -> None:
        model = CalculatorModel()
        model.input_digit("8")
        model.set_operator("÷")
        model.input_digit("0")

        with self.assertRaises(ZeroDivisionError):
            model.equals()


if __name__ == "__main__":
    unittest.main()

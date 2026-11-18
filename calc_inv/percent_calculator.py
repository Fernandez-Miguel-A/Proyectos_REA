from decimal import Decimal
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CalculatorModel:
    OPERATORS = {"+", "-", "×", "÷"}

    def __init__(self) -> None:
        self.clear()

    @property
    def display(self) -> str:
        return self._entry

    @property
    def can_apply_percent(self) -> bool:
        return self._operator is None or not self._awaiting_operand

    def clear(self) -> None:
        self._entry = "0"
        self._accumulator: Decimal | None = None
        self._operator: str | None = None
        self._awaiting_operand = False

    def input_digit(self, digit: str) -> None:
        if digit not in "0123456789":
            raise ValueError("digit must be a single decimal digit")

        if self._awaiting_operand:
            self._entry = digit
            self._awaiting_operand = False
        elif self._entry == "0":
            self._entry = digit
        else:
            self._entry += digit

    def input_decimal(self) -> None:
        if self._awaiting_operand:
            self._entry = "0."
            self._awaiting_operand = False
        elif "." not in self._entry:
            self._entry += "."

    def set_operator(self, operator: str) -> None:
        if operator not in self.OPERATORS:
            raise ValueError(f"unsupported operator: {operator}")

        if self._operator is not None and not self._awaiting_operand:
            self._evaluate_pending()

        self._accumulator = self._current_value()
        self._operator = operator
        self._awaiting_operand = True

    def apply_percent(self) -> None:
        if not self.can_apply_percent:
            raise ValueError("enter a value before applying percent")

        value = self._current_value() / Decimal(100)
        if self._operator in {"+", "-"} and self._accumulator is not None:
            value *= self._accumulator
        self._entry = self._format(value)
        self._awaiting_operand = False

    def equals(self) -> None:
        if self._operator is None or self._awaiting_operand:
            return

        self._evaluate_pending()
        self._operator = None
        self._accumulator = None
        self._awaiting_operand = True

    def _evaluate_pending(self) -> None:
        if self._accumulator is None or self._operator is None:
            return

        right = self._current_value()
        if self._operator == "+":
            result = self._accumulator + right
        elif self._operator == "-":
            result = self._accumulator - right
        elif self._operator == "×":
            result = self._accumulator * right
        else:
            if right == 0:
                raise ZeroDivisionError("division by zero")
            result = self._accumulator / right

        self._entry = self._format(result)
        self._accumulator = result

    def _current_value(self) -> Decimal:
        return Decimal(self._entry)

    @staticmethod
    def _format(value: Decimal) -> str:
        if value == 0:
            return "0"
        text = format(value.normalize(), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text


class PercentCalculator(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = CalculatorModel()
        self.setWindowTitle("Percent Calculator")
        self.setFixedSize(300, 410)

        layout = QVBoxLayout(self)
        hint = QLabel(
            "+ and - use a percent of the first number; × and ÷ use a fraction."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.display = QLineEdit(self.model.display)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setMinimumHeight(52)
        self.display.setFont(QFont("", 22))
        layout.addWidget(self.display)

        grid = QGridLayout()
        layout.addLayout(grid)
        keys = (
            ("C", "%", "÷", "×"),
            ("7", "8", "9", "-"),
            ("4", "5", "6", "+"),
            ("1", "2", "3", "="),
            ("0", "", ".", ""),
        )
        [print("keys:", k, ord(k)) for row in keys for k in row if k]
        self.percent_button: QPushButton | None = None
        for row, labels in enumerate(keys):
            for column, label in enumerate(labels):
                if not label:
                    continue
                button = QPushButton(label)
                button.setMinimumSize(54, 48)
                if label == "%":
                    self.percent_button = button
                button.clicked.connect(
                    lambda checked=False, value=label: self._press(value)
                )
                column_span = 2 if label == "0" else 1
                grid.addWidget(button, row, column, 1, column_span)
        self._refresh_display()

    def _press(self, key: str) -> None:
        try:
            if key.isdigit():
                self.model.input_digit(key)
            elif key == ".":
                self.model.input_decimal()
            elif key in CalculatorModel.OPERATORS:
                self.model.set_operator(key)
            elif key == "%":
                self.model.apply_percent()
            elif key == "=":
                self.model.equals()
            elif key == "C":
                self.model.clear()
        except ZeroDivisionError:
            self.model.clear()
            self.display.setText("Cannot divide by zero")
            return

        self._refresh_display()

    def _refresh_display(self) -> None:
        self.display.setText(self.model.display)
        if self.percent_button is not None:
            self.percent_button.setEnabled(self.model.can_apply_percent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PercentCalculator()
    window.show()
    sys.exit(app.exec())

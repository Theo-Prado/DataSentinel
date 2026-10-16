import unittest
from decimal import Decimal

from src.datasentinel.models import SaleRecord
from src.datasentinel.rules import (
    DUPLICATE,
    PRICE_INVALID,
    QUANTITY_INVALID,
    REQUIRED_FIELD_MISSING,
    flag_duplicates,
    validate_record,
)


def make_record(line_number: int, product: str, price: str, quantity: str) -> SaleRecord:
    return SaleRecord(
        line_number=line_number,
        original={
            "produto": product,
            "preco": price,
            "quantidade": quantity,
        },
        product=product,
        price_raw=price,
        quantity_raw=quantity,
    )


class ValidationRulesTests(unittest.TestCase):
    def test_accepts_valid_sale(self) -> None:
        record = make_record(2, "Mouse", "100.00", "2")

        validate_record(record)

        self.assertTrue(record.approved)
        self.assertEqual(record.price, Decimal("100.00"))
        self.assertEqual(record.quantity, Decimal("2"))

    def test_rejects_negative_price(self) -> None:
        record = make_record(2, "Monitor", "-900", "1")

        validate_record(record)

        self.assertFalse(record.approved)
        self.assertEqual(record.validation_issues, [PRICE_INVALID])

    def test_rejects_zero_quantity(self) -> None:
        record = make_record(2, "Teclado", "150", "0")

        validate_record(record)

        self.assertFalse(record.approved)
        self.assertEqual(record.validation_issues, [QUANTITY_INVALID])

    def test_rejects_missing_required_field(self) -> None:
        record = make_record(2, "Teclado", "", "1")

        validate_record(record)

        self.assertFalse(record.approved)
        self.assertEqual(record.validation_issues, [REQUIRED_FIELD_MISSING])

    def test_rejects_non_numeric_price(self) -> None:
        record = make_record(2, "Monitor", "indisponivel", "1")

        validate_record(record)

        self.assertFalse(record.approved)
        self.assertEqual(record.validation_issues, [PRICE_INVALID])

    def test_identifies_duplicate_without_rejecting_it(self) -> None:
        first = make_record(2, "Mouse", "100", "2")
        second = make_record(3, "Mouse", "100", "2")
        validate_record(first)
        validate_record(second)

        flag_duplicates([first, second])

        self.assertTrue(second.approved)
        self.assertEqual(second.quality_flags, [DUPLICATE])
        self.assertEqual(second.duplicate_reference_line, 2)

    def test_different_quantity_is_not_duplicate(self) -> None:
        first = make_record(2, "Mouse", "100", "2")
        second = make_record(3, "Mouse", "100", "3")

        flag_duplicates([first, second])

        self.assertEqual(first.quality_flags, [])
        self.assertEqual(second.quality_flags, [])



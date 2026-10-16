import unittest
from decimal import Decimal

from src.datasentinel.analysis import analyze_sales, count_problem_categories
from src.datasentinel.models import SaleRecord
from src.datasentinel.rules import DUPLICATE, PRICE_INVALID, QUANTITY_INVALID


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


class AnalysisTests(unittest.TestCase):
    def test_calculates_revenue_from_approved_records_only(self) -> None:
        records = [
            make_record(2, "Mouse", "100", "2"),
            make_record(3, "Mouse", "100", "2"),
            make_record(4, "Monitor", "-900", "1"),
            make_record(5, "Teclado", "150", "0"),
        ]

        result = analyze_sales(records)
        categories = count_problem_categories(result)

        self.assertEqual(result.received_count, 4)
        self.assertEqual(len(result.approved_records), 2)
        self.assertEqual(len(result.rejected_records), 2)
        self.assertEqual(result.revenue, Decimal("400"))
        self.assertEqual(categories[DUPLICATE], 1)
        self.assertEqual(categories[PRICE_INVALID], 1)
        self.assertEqual(categories[QUANTITY_INVALID], 1)



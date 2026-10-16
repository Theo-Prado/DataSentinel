import unittest
from decimal import Decimal

from src.datasentinel.analysis import analyze_sales
from src.datasentinel.models import SaleRecord
from src.datasentinel.report import format_brl, format_report


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


class ReportTests(unittest.TestCase):
    def test_formats_brazilian_currency(self) -> None:
        self.assertEqual(format_brl(Decimal("8250")), "8.250,00")

    def test_report_totals_match_analysis(self) -> None:
        result = analyze_sales(
            [
                make_record(2, "Notebook", "4500", "1"),
                make_record(3, "Mouse", "100", "2"),
                make_record(4, "Monitor", "-900", "1"),
            ]
        )

        report = format_report(result)

        self.assertIn("Registros recebidos: 3", report)
        self.assertIn("Registros aprovados: 2", report)
        self.assertIn("Registros rejeitados: 1", report)
        self.assertIn("Faturamento válido: R$ 4.700,00", report)
        self.assertIn("Status da análise: CONCLUÍDA", report)



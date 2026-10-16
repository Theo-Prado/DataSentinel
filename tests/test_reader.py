import tempfile
import unittest
from pathlib import Path

from src.datasentinel.reader import InputDataError, load_sales


class ReaderTests(unittest.TestCase):
    def test_loads_csv_and_preserves_original_values(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "work") as directory:
            path = Path(directory) / "vendas.csv"
            path.write_text(
                "produto,preco,quantidade\nMouse,100.00,2\n",
                encoding="utf-8",
            )

            records = load_sales(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].original["preco"], "100.00")
        self.assertEqual(records[0].line_number, 2)

    def test_rejects_missing_file(self) -> None:
        with self.assertRaises(InputDataError):
            load_sales(Path("arquivo-que-nao-existe.csv"))

    def test_rejects_empty_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "work") as directory:
            path = Path(directory) / "vazio.csv"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(InputDataError, "cabeçalho"):
                load_sales(path)

    def test_rejects_header_without_required_columns(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "work") as directory:
            path = Path(directory) / "invalido.csv"
            path.write_text("produto,valor\nMouse,100\n", encoding="utf-8")

            with self.assertRaisesRegex(InputDataError, "quantidade"):
                load_sales(path)

    def test_rejects_row_with_more_fields_than_header(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "work") as directory:
            path = Path(directory) / "malformado.csv"
            path.write_text(
                "produto,preco,quantidade\nMouse,100,2,extra\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(InputDataError, "mais campos"):
                load_sales(path)



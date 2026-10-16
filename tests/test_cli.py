import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from main import run


class CliTests(unittest.TestCase):
    def test_successful_run_can_save_report(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "work") as directory:
            input_path = Path(directory) / "vendas.csv"
            output_path = Path(directory) / "relatorio.txt"
            input_path.write_text(
                "produto,preco,quantidade\nMouse,100,2\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = run(input_path, output_path)

            saved_report = output_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("Status da análise: CONCLUÍDA", stdout.getvalue())
        self.assertEqual(saved_report, stdout.getvalue().split("Relatório salvo em:")[0].rstrip() + "\n")

    def test_missing_file_returns_controlled_error(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = run(Path("arquivo-inexistente.csv"))

        self.assertEqual(exit_code, 2)
        self.assertIn("INTERROMPIDA POR ERRO", stderr.getvalue())



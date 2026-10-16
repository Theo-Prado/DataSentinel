"""Interface de linha de comando do DataSentinel."""

import argparse
import sys
from pathlib import Path

from src.datasentinel.analysis import analyze_sales
from src.datasentinel.reader import InputDataError, load_sales
from src.datasentinel.report import format_report, save_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Investiga a qualidade de dados e o faturamento de vendas."
    )
    parser.add_argument(
        "--input",
        required=True,
        dest="input_path",
        help="caminho do arquivo CSV de vendas",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        help="caminho opcional para salvar uma cópia do relatório",
    )
    return parser


def run(input_path: str | Path, output_path: str | Path | None = None) -> int:
    """Executa o pipeline e retorna um código de saída de processo."""

    try:
        records = load_sales(input_path)
        result = analyze_sales(records)
        report = format_report(result)
        print(report)
        if output_path is not None:
            save_report(output_path, report)
            print(f"Relatório salvo em: {Path(output_path)}")
    except InputDataError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        print("Status da análise: INTERROMPIDA POR ERRO", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERRO: não foi possível salvar o relatório: {exc}", file=sys.stderr)
        print("Status da análise: INTERROMPIDA POR ERRO", file=sys.stderr)
        return 3
    return 0


def main() -> int:
    args = build_parser().parse_args()
    return run(args.input_path, args.output_path)


if __name__ == "__main__":
    raise SystemExit(main())



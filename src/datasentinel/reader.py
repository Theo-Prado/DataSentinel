"""Leitura e validação estrutural dos arquivos CSV de vendas."""

import csv
from pathlib import Path

from .models import SaleRecord

REQUIRED_COLUMNS = ("produto", "preco", "quantidade")


class InputDataError(ValueError):
    """Erro controlado causado por uma entrada que não pode ser analisada."""


def _normalise_header(field: str | None) -> str:
    return "" if field is None else field.strip().lower()


def load_sales(path: str | Path) -> list[SaleRecord]:
    """Carrega vendas de um CSV e preserva os valores originais das células.

    O arquivo deve possuir as colunas obrigatórias ``produto``, ``preco`` e
    ``quantidade``. Colunas adicionais são aceitas, mas não participam das
    regras financeiras da primeira versão.
    """

    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            csv_reader = csv.DictReader(csv_file, strict=True)
            if csv_reader.fieldnames is None:
                raise InputDataError("o arquivo não possui cabeçalho")

            headers = [_normalise_header(field) for field in csv_reader.fieldnames]
            if len(headers) != len(set(headers)):
                raise InputDataError("o cabeçalho possui colunas duplicadas")

            missing_columns = [column for column in REQUIRED_COLUMNS if column not in headers]
            if missing_columns:
                missing = ", ".join(missing_columns)
                raise InputDataError(f"colunas obrigatórias ausentes: {missing}")

            records: list[SaleRecord] = []
            for line_number, row in enumerate(csv_reader, start=2):
                if None in row:
                    raise InputDataError(
                        f"linha {line_number} possui mais campos do que o cabeçalho"
                    )

                normalised_row = {
                    _normalise_header(key): (value if value is not None else "")
                    for key, value in row.items()
                    if key is not None
                }
                records.append(
                    SaleRecord(
                        line_number=line_number,
                        original=normalised_row,
                        product=normalised_row.get("produto", ""),
                        price_raw=normalised_row.get("preco", ""),
                        quantity_raw=normalised_row.get("quantidade", ""),
                    )
                )

            if not records:
                raise InputDataError("o arquivo não contém registros de vendas")
            return records
    except FileNotFoundError as exc:
        raise InputDataError(f"arquivo não encontrado: {file_path}") from exc
    except PermissionError as exc:
        raise InputDataError(f"sem permissão para ler o arquivo: {file_path}") from exc
    except UnicodeDecodeError as exc:
        raise InputDataError("não foi possível decodificar o arquivo como UTF-8") from exc
    except csv.Error as exc:
        raise InputDataError(f"CSV inválido: {exc}") from exc
    except OSError as exc:
        raise InputDataError(f"erro ao ler o arquivo: {exc}") from exc



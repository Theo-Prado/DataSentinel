"""Regras de negócio do DataSentinel."""

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation

from .models import SaleRecord

PRICE_INVALID = "preco_invalido"
QUANTITY_INVALID = "quantidade_invalida"
REQUIRED_FIELD_MISSING = "campo_obrigatorio_ausente"
DUPLICATE = "duplicata"


def _parse_positive_number(raw_value: str) -> Decimal | None:
    try:
        value = Decimal(raw_value.strip())
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite() or value <= 0:
        return None
    return value


def validate_record(record: SaleRecord) -> SaleRecord:
    """Aplica as regras obrigatórias de produto, preço e quantidade."""

    record.validation_issues.clear()
    record.price = None
    record.quantity = None

    if not record.product.strip():
        record.validation_issues.append(REQUIRED_FIELD_MISSING)

    if not record.price_raw.strip():
        record.validation_issues.append(REQUIRED_FIELD_MISSING)
    else:
        record.price = _parse_positive_number(record.price_raw)
        if record.price is None:
            record.validation_issues.append(PRICE_INVALID)

    if not record.quantity_raw.strip():
        record.validation_issues.append(REQUIRED_FIELD_MISSING)
    else:
        record.quantity = _parse_positive_number(record.quantity_raw)
        if record.quantity is None:
            record.validation_issues.append(QUANTITY_INVALID)

    return record


def _duplicate_key(record: SaleRecord) -> tuple[str, str, str] | None:
    values = (
        record.original.get("produto", "").strip(),
        record.original.get("preco", "").strip(),
        record.original.get("quantidade", "").strip(),
    )
    if not any(values):
        return None
    return values


def flag_duplicates(records: Iterable[SaleRecord]) -> None:
    """Sinaliza ocorrências posteriores de linhas inteiramente repetidas.

    A primeira ocorrência de cada chave funciona como referência. As demais
    são sinalizadas, mas permanecem aprovadas caso não tenham outro problema.
    """

    first_occurrence: dict[tuple[str, str, str], SaleRecord] = {}
    for record in records:
        record.quality_flags.clear()
        record.duplicate_reference_line = None
        key = _duplicate_key(record)
        if key is None:
            continue
        reference = first_occurrence.get(key)
        if reference is None:
            first_occurrence[key] = record
            continue
        record.quality_flags.append(DUPLICATE)
        record.duplicate_reference_line = reference.line_number



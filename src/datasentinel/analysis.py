"""Orquestração das regras e cálculo dos indicadores."""

from collections import Counter
from collections.abc import Iterable
from decimal import Decimal

from .models import AnalysisResult, SaleRecord
from .rules import flag_duplicates, validate_record


def analyze_sales(records: Iterable[SaleRecord]) -> AnalysisResult:
    """Valida, investiga duplicatas e calcula o faturamento aprovado."""

    materialized_records = list(records)
    for record in materialized_records:
        validate_record(record)
    flag_duplicates(materialized_records)

    revenue = sum(
        (record.revenue for record in materialized_records if record.approved),
        Decimal("0"),
    )
    return AnalysisResult(records=materialized_records, revenue=revenue)


def count_problem_categories(result: AnalysisResult) -> Counter[str]:
    """Conta ocorrências de problemas, permitindo múltiplos por registro."""

    return Counter(
        problem_code
        for record in result.records
        for problem_code in record.problem_codes
    )



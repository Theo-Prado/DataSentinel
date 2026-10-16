"""Geração do relatório textual da análise."""

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from . import __version__
from .analysis import count_problem_categories
from .models import AnalysisResult
from .rules import (
    DUPLICATE,
    PRICE_INVALID,
    QUANTITY_INVALID,
    REQUIRED_FIELD_MISSING,
)

PROBLEM_LABELS = {
    DUPLICATE: "possível venda duplicada",
    PRICE_INVALID: "preço inválido",
    QUANTITY_INVALID: "quantidade inválida",
    REQUIRED_FIELD_MISSING: "campo obrigatório ausente",
}


def format_brl(value: Decimal) -> str:
    """Formata um valor Decimal como moeda brasileira."""

    rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    formatted = f"{rounded:,.2f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_report(result: AnalysisResult) -> str:
    """Monta o relatório de uma análise concluída."""

    categories = count_problem_categories(result)
    duplicate_count = categories.get(DUPLICATE, 0)

    lines = [
        "====================================",
        f"DATASENTINEL v{__version__}",
        "RELATÓRIO DE VENDAS",
        "====================================",
        "",
        f"Registros recebidos: {result.received_count}",
        f"Registros aprovados: {len(result.approved_records)}",
        f"Registros rejeitados: {len(result.rejected_records)}",
        f"Possíveis duplicatas identificadas: {duplicate_count}",
        "",
        "Ocorrências por categoria de problema:",
    ]

    if categories:
        ordered_codes = [
            DUPLICATE,
            PRICE_INVALID,
            QUANTITY_INVALID,
            REQUIRED_FIELD_MISSING,
        ]
        ordered_codes.extend(
            code for code in categories if code not in ordered_codes
        )
        for code in ordered_codes:
            if code in categories:
                label = PROBLEM_LABELS.get(code, code)
                lines.append(f"- {label}: {categories[code]}")
    else:
        lines.append("- Nenhum problema identificado")

    lines.extend(
        [
            "",
            f"Faturamento válido: R$ {format_brl(result.revenue)}",
            "Política de duplicidade: registros sinalizados foram preservados e incluídos no faturamento.",
            "",
            "Status da análise: CONCLUÍDA",
            "====================================",
        ]
    )
    return "\n".join(lines)


def save_report(path: str | Path, report: str) -> None:
    """Salva o relatório em UTF-8, criando a pasta de destino se necessário."""

    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(f"{report}\n", encoding="utf-8")



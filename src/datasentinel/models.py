"""Modelos de dados usados pelo pipeline do DataSentinel."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class SaleRecord:
    """Representa uma linha de venda preservando os valores de entrada."""

    line_number: int
    original: dict[str, str]
    product: str
    price_raw: str
    quantity_raw: str
    price: Decimal | None = None
    quantity: Decimal | None = None
    validation_issues: list[str] = field(default_factory=list)
    quality_flags: list[str] = field(default_factory=list)
    duplicate_reference_line: int | None = None

    @property
    def approved(self) -> bool:
        """Indica se o registro passou pelas regras obrigatórias."""

        return not self.validation_issues

    @property
    def revenue(self) -> Decimal:
        """Calcula o faturamento da linha quando os valores são válidos."""

        if self.price is None or self.quantity is None:
            return Decimal("0")
        return self.price * self.quantity

    @property
    def problem_codes(self) -> list[str]:
        """Retorna todos os problemas, incluindo sinalizações de qualidade."""

        return [*self.validation_issues, *self.quality_flags]


@dataclass
class AnalysisResult:
    """Resultado consolidado de uma execução bem-sucedida."""

    records: list[SaleRecord]
    revenue: Decimal

    @property
    def received_count(self) -> int:
        return len(self.records)

    @property
    def approved_records(self) -> list[SaleRecord]:
        return [record for record in self.records if record.approved]

    @property
    def rejected_records(self) -> list[SaleRecord]:
        return [record for record in self.records if not record.approved]



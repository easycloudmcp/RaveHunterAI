from dataclasses import dataclass


@dataclass(slots=True)
class Pricing:
    minimum: float | None = None
    maximum: float | None = None
    currency: str = "EUR"
    ticket_url: str | None = None
    sold_out: bool = False
    door_sales: bool = False
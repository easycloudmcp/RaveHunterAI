from dataclasses import dataclass


@dataclass(slots=True)
class Confidence:
    value: float
    reason: str = ""
    source: str = "ai"

    def is_high(self) -> bool:
        return self.value >= 0.90

    def is_medium(self) -> bool:
        return 0.70 <= self.value < 0.90

    def is_low(self) -> bool:
        return self.value < 0.70
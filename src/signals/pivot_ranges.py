from dataclasses import dataclass


@dataclass
class PivotLevels:
    pivot: float
    r1: float
    r2: float
    r3: float
    s1: float
    s2: float
    s3: float


class PivotCalculator:
    @staticmethod
    def calculate(high: float, low: float, close: float) -> PivotLevels:
        """Calculate pivot points and support/resistance levels"""
        pivot = (high + low + close) / 3

        # Calculate resistance levels
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)

        # Calculate support levels
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)

        return PivotLevels(
            pivot=pivot,
            r1=r1,
            r2=r2,
            r3=r3,
            s1=s1,
            s2=s2,
            s3=s3
        )

    @staticmethod
    def is_price_near_level(price: float, level: float, threshold: float = 0.001) -> bool:
        """Check if price is near a pivot level"""
        return abs(price - level) / level < threshold
from dataclasses import dataclass


@dataclass
class CPRLevels:
    pivot: float
    bc: float
    tc: float


class CPRCalculator:
    @staticmethod
    def calculate(high: float, low: float, close: float) -> CPRLevels:
        """Calculate CPR levels for the given price data"""
        pivot = (high + low + close) / 3
        bc = (high + low) / 2
        tc = (pivot - bc) + pivot

        return CPRLevels(pivot=pivot, bc=bc, tc=tc)

    @staticmethod
    def is_price_above_tc(price: float, cpr: CPRLevels) -> bool:
        """Check if price is above TC level"""
        return price > cpr.tc

from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    symbol: str
    price: float
    highest: float
    lowest: float
    average: float
    percent_change: float
    capacity_lot: float
    capacity_tl: float

    @property
    def commission(self) -> float:
        """Calculate commission (example: 0.2%)"""
        return self.price * 2 / 1000

@dataclass
class PlayerModel:
    id: int
    money: float

@dataclass
class PortfolioItem:
    symbol: str
    quantity: int
    average_cost: float
    current_price: Optional[float] = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return self.market_value - (self.quantity * self.average_cost)

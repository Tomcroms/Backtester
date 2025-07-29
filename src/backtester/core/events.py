from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import pandas as pd

@dataclass(slots=True)
class MarketEvent:
    symbol: str
    timestamp: pd.Timestamp
    data: dict[str, Any]

@dataclass(slots=True)
class SignalEvent:
    symbol: str
    timestamp: pd.Timestamp
    direction: int  # +1 long, -1 short, 0 flat
    size: float
    meta: dict[str, Any] | None = None

@dataclass(slots=True)
class OrderEvent:
    symbol: str
    timestamp: pd.Timestamp
    direction: int
    size: float
    order_type: str = "market"
    limit_price: float | None = None

@dataclass(slots=True)
class FillEvent:
    symbol: str
    timestamp: pd.Timestamp
    direction: int # +1 long, -1 short, 0 flat
    fill_price: float
    size: float
    commission: float = 0.0
    slippage: float = 0.0
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from src.backtester.core.interfaces import Strategy
from src.backtester.core.events import MarketEvent, SignalEvent

@dataclass
class StrategyParams:
    """Container simple pour les hyperparamètres de stratégie."""
    # TODO
    threshold_entry: float = 0.05
    threshold_exit: float = 0.01

class BaseStrategy(Strategy):
    def __init__(self, params: StrategyParams):
        self.params = params

    def on_market_event(self, events: list[MarketEvent]) -> list[SignalEvent]:
        raise NotImplementedError
from src.backtester.strategy.base import BaseStrategy, StrategyParams
from src.backtester.core.events import MarketEvent, SignalEvent
from dataclasses import dataclass
import pandas as pd 

@dataclass
class PEParams(StrategyParams):
    hi: float = 25.0
    lo: float = 15.0
    pct: float = 0.05

class PERatioStrategy(BaseStrategy):
    def __init__(self, params: PEParams, initial_amount: float):
        super().__init__(params)
        self.initial_amount = initial_amount
    
    def on_market_event(self, events: list[MarketEvent]) -> list[SignalEvent]:
        current_event = events[0]
        pe_ratio = current_event.data["pe"]
        signals: list[SignalEvent] = []

        if pe_ratio > self.params.hi:
            signals.append(SignalEvent(
                symbol=current_event.symbol,
                timestamp=current_event.timestamp,
                direction=-1,
                size=self.params.pct * self.initial_amount,
                meta={"reason": "pe_ratio > 25"}
            ))

        elif pe_ratio < self.params.lo:
            signals.append(SignalEvent(
                symbol=current_event.symbol,
                timestamp=current_event.timestamp,
                direction=1,
                size=self.params.pct * self.initial_amount,
                meta={"reason": "pe_ratio < 15"}
            ))

        return signals
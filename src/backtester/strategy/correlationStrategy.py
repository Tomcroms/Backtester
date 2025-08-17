from src.backtester.strategy.base import BaseStrategy, StrategyParams
from src.backtester.core.events import MarketEvent, SignalEvent
from dataclasses import dataclass
import pandas as pd 

@dataclass
class CorrelParams(StrategyParams):
    pct = 0.05 #base pct allowed to each trade

class CorrelStrategy(BaseStrategy):
    def __init__(self, params: CorrelParams, initial_amount: float):
        super().__init__(params)
        self.initial_amount = initial_amount
    
    def on_market_event(self, market_events: list[MarketEvent]) -> list[SignalEvent]:
        ...
    
    def is_new_signal(self, market_event: MarketEvent) -> bool:
        is_new_signal = False
        if(market_event.data["correlatedMA50"] > market_event.data["symbolMA50"]):
            is_new_signal = True
        return is_new_signal

    def get_signal_size(self, market_event: MarketEvent) -> float:
        ...
    
    def get_direction(self, market_event: MarketEvent) -> int:
        ...
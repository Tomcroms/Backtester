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
        signals: list[SignalEvent] = []

        for market_event in market_events:
            if(self.is_new_signal(market_event)):
                signals.append(SignalEvent(
                    symbol=market_event.symbol,
                    timestamp=market_event.timestamp,
                    direction=self.get_direction(market_event),
                    size=self.get_signal_size(market_event),
                    meta={"To do later"}
                ))

        return signals
    
    def is_new_signal(self, market_event: MarketEvent) -> bool:
        is_new_signal = False
        if(market_event.data["correlatedMA50"] > market_event.data["symbolMA50"]):
            is_new_signal = True
        return is_new_signal

    def get_signal_size(self, market_event: MarketEvent) -> float:
        dollar_allocation = self.params.pct * self.initial_amount
        shares = dollar_allocation / market_event.data["close"]
        return shares
    
    def get_direction(self, market_event: MarketEvent) -> int:
        direction = 0
        if int(market_event.data["pe"]) > 25:
            direction = -1
        elif int(market_event.data["pe"]) < 15:
            direction = 1
        return direction
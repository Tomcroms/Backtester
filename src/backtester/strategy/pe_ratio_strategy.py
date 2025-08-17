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
    
    def on_market_event(self, market_events: list[MarketEvent]) -> list[SignalEvent]:
        market_event = market_events[0]                     # we only have one market event at a time for this strategy
        pe = market_event.data["pe"]
        px = market_event.data["close"]
        qty = (self.params.pct * self.initial_amount) / px  # convert into symbol units 
        
        signals: list[SignalEvent] = []
        if pe > self.params.hi:
            signals.append(
                SignalEvent(
                    market_event.symbol,
                    market_event.timestamp,
                    direction=-1,
                    qty=qty,
                    meta={"reason": "pe_ratio > hi"}
                )
            )
        elif pe < self.params.lo:
            signals.append(
                SignalEvent(
                    symbol=market_event.symbol,
                    timestamp=market_event.timestamp,
                    direction=1,
                    qty=qty,
                    meta={"reason": "pe_ratio < lo"}
                )
            )
            
        return signals
    
    def new_signal(self, market_event: MarketEvent) -> bool:
        new_signal = True
        if(15 < int(market_event.data["pe"]) < 25):
            new_signal = False
        return new_signal

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
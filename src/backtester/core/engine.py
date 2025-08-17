from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from .interfaces import DataHandler, Strategy, Broker, Clock, Portfolio
from .events import MarketEvent, SignalEvent, OrderEvent, FillEvent

@dataclass
class EngineConfig:
    verbose: bool = False

class BacktestEngine:
    def __init__(
        self,
        data: DataHandler,
        strategy: Strategy,
        portfolio: Portfolio,
        broker: Broker,
        clock: Clock = None,
        config: EngineConfig | None = None,
    ) -> None:
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.broker = broker
        self.clock = clock
        self.config = config or EngineConfig()

    def run(self) -> None:
        iterator = self.clock if self.clock else iter(int, 1)
        for _ in iterator:
            if not self.data.has_next():
                break
            market_events = self.data.get_next()
            signals = self.strategy.on_market_event(market_events)
            orders = self.portfolio.generate_orders(signals, market_events)
            fills = self.broker.execute(orders, market_events)
            self.portfolio.update_on_fill(fills, market_events)
            if self.config.verbose:
                print(f"At {market_events[0].timestamp}:")
                print(self.portfolio)
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
        self.current_pnl = 0

    def run(self) -> None:
        if self.clock:
            self.run_with_clock()
        else:
            self.run_without_clock()

    def run_without_clock(self):
        while self.data.has_next():
            market_events: list[MarketEvent] = self.data.get_next()
            signals: list[SignalEvent] = self.strategy.on_market_event(market_events)
            orders: list[OrderEvent] = self.portfolio.generate_orders(signals)
            fills: list[FillEvent] = self.broker.execute(orders, market_events)
            self.portfolio.update_on_fill(fills, market_events)
            print(f"At {market_events[0].timestamp}:")
            print(self.portfolio)

    def run_with_clock(self):
        for _ in self.clock:
            if not self.data.has_next():
                break
            market_events: list[MarketEvent] = self.data.get_next()
            signals: list[SignalEvent] = self.strategy.on_market_event(market_events)
            orders: list[OrderEvent] = self.portfolio.generate_orders(signals)
            fills: list[FillEvent] = self.broker.execute(orders, market_events)
            self.portfolio.update_on_fill(fills)
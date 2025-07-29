import pandas as pd
from src.backtester.core.engine import BacktestEngine, EngineConfig
from src.backtester.core.events import MarketEvent, SignalEvent
from src.backtester.core.interfaces import DataHandler, Strategy, Portfolio, Broker, Clock

class DummyData(DataHandler):
    def __init__(self):
        self.idx = 0
        self.events = [
            [MarketEvent("VIX", pd.Timestamp("2020-01-01"), {"close": 12.0})],
            [MarketEvent("VIX", pd.Timestamp("2020-01-02"), {"close": 13.0})],
        ]

    def get_next(self):
        e = self.events[self.idx]
        self.idx += 1
        return e

    def has_next(self):
        return self.idx < len(self.events)

class DummyStrategy(Strategy):
    def on_market_event(self, events):
        e = events[0]
        return [SignalEvent(e.symbol, e.timestamp, direction=1, size=1)]

class DummyPortfolio(Portfolio):
    def generate_orders(self, signals):
        from src.backtester.core.events import OrderEvent
        return [OrderEvent(s.symbol, s.timestamp, s.direction, s.size) for s in signals]

    def update_on_fill(self, fills):
        pass

class DummyBroker(Broker):
    def execute(self, orders, market_events):
        from src.backtester.core.events import FillEvent
        price = market_events[0].data["close"]
        return [FillEvent(o.symbol, o.timestamp, price, o.size) for o in orders]

class DummyClock(Clock):
    def __iter__(self):
        yield from range(2)


def test_engine_runs():
    eng = BacktestEngine(
        data=DummyData(),
        strategy=DummyStrategy(),
        portfolio=DummyPortfolio(),
        broker=DummyBroker(),
        clock=DummyClock(),
        config=EngineConfig(verbose=True),
    )
    eng.run()
from __future__ import annotations
from src.backtester.core.interfaces import Broker
from src.backtester.core.events import OrderEvent, FillEvent, MarketEvent

class SimulatedBroker(Broker):
    def __init__(self, commission_per_trade: float = 0.0, slippage_bp: float = 0.0):
        self.commission = commission_per_trade
        self.slippage_bp = slippage_bp

    def execute(self, orders: list[OrderEvent], market_events: list[MarketEvent]) -> list[FillEvent]:
        price_map = {market_event.symbol: market_event.data.get("close") for market_event in market_events}
        fills: list[FillEvent] = []
        for order in orders:
            price = price_map[order.symbol]
            slip = price * self.slippage_bp     #TODO
            fills.append(
                FillEvent(
                    symbol=order.symbol,
                    timestamp=order.timestamp,
                    direction=order.direction,
                    fill_price=price + slip * (1 if order.direction > 0 else -1),
                    size=order.size,
                    commission=self.commission,
                    slippage=abs(slip * order.size),
                )
            )
        return fills
from __future__ import annotations
from dataclasses import dataclass, field
from src.backtester.core.interfaces import Portfolio
from src.backtester.core.events import SignalEvent, OrderEvent, FillEvent, MarketEvent

@dataclass
class Position:
    symbol: str
    qty: float = 0.0
    avg_price: float = 0.0
    current_value: float = 0.0

@dataclass
class SimplePortfolio(Portfolio):
    cash: float
    positions_value: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    equity_curve: list[float] = field(default_factory=list)

    def generate_orders(self, signals: list[SignalEvent]) -> list[OrderEvent]:
        orders: list[OrderEvent] = []
        for signal in signals:
            if (signal.direction == 1 and self.cash >= signal.size) or (signal.direction == -1 and self.positions_value >= signal.size):
                #we have enough cash to buy more asset or we have enough asset to buy cash
                orders.append(
                    OrderEvent(
                        symbol=signal.symbol,
                        timestamp=signal.timestamp,
                        direction=signal.direction,
                        size=signal.size,
                    )
                )
        return orders

    def update_on_fill(self, fills: list[FillEvent], market_events: list[MarketEvent]) -> None:
        for fill in fills:
            pos = self.positions.setdefault(fill.symbol, Position(symbol=fill.symbol))
            # update avg price (simplified)
            new_qty = pos.qty + fill.size / fill.fill_price
            pos.avg_price = 0 #TODO: update avg_price of each particular position
            pos.qty = new_qty

            self.cash -= fill.size*fill.direction - fill.commission - fill.slippage
        self.refresh_mark_to_market(market_events)
        self.refresh_positions_value()
        # TODO: update equity_curve

    def refresh_mark_to_market(self, market_events: list[MarketEvent]) -> None:        
        for market_event in market_events:
            if market_event.symbol in self.positions:
                self.positions[market_event.symbol].current_value = self.positions[market_event.symbol].qty * market_event.data.get("close")

    def refresh_positions_value(self) -> None:
        positions_value = 0.0
        for _, position in self.positions.items():
            positions_value += position.current_value
        self.positions_value = positions_value
    
    def get_positions_current_prices(self) -> dict:
        positions_prices = {}
        for _, position in self.positions.items():
            positions_prices[position.symbol] = position.current_value / position.qty
        return positions_prices
    
    def __str__(self):
        return f"Current cash is: {self.cash}\nCurrent positions value is: {self.positions_value}\nCurrent total value: {self.cash+self.positions_value}\nPositions prices: {self.get_positions_current_prices()}\n\n"

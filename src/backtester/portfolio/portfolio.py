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
    net_liquidation_value: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    equity_curve: list[float] = field(default_factory=list)

    def generate_orders(self, signals: list[SignalEvent], market_events: list[MarketEvent]) -> list[OrderEvent]:
        price_map = {market_event.symbol: market_event.data["close"] for market_event in market_events}
        orders: list[OrderEvent] = []
        for signal in signals:
            px = price_map[signal.symbol]

            if signal.direction == 1:
                if self.cash >= signal.qty * px:
                    orders.append(
                        OrderEvent(
                            signal.symbol,
                            signal.timestamp,
                            signal.direction,
                            signal.qty
                        )
                    )

            elif signal.direction == -1:
                if self.positions.get(signal.symbol) >= signal.qty:
                    orders.append(
                        OrderEvent(
                            signal.symbol,
                            signal.timestamp,
                            signal.direction,
                            signal.qty
                        )
                    )

        return orders

    def update_on_fill(self, fills: list[FillEvent], market_events: list[MarketEvent]) -> None:
        for fill in fills:
            position = self.positions.setdefault(fill.symbol, Position(symbol=fill.symbol))
            qty_change = fill.qty * fill.direction

            if qty_change > 0:  #buy
                new_qty = position.qty + qty_change
                position.avg_price = (
                    0.0 if new_qty == 0 else 
                    (position.avg_price * position.qty + fill.fill_price * qty_change) / new_qty
                )
                position.qty = new_qty
                self.cash -= fill.fill_price * fill.qty + fill.commission + fill.slippage

            else:               #sell           
                position.qty = max(0.0, position.qty + qty_change)
                self.cash += fill.fill_price * fill.qty - fill.commission - fill.slippage
                if position.qty == 0:
                    position.avg_price = 0.0
            
            self.cash -= fill.fill_price * fill.direction - fill.commission - fill.slippage
        
        self.refresh_mark_to_market(market_events)

    def refresh_mark_to_market(self, market_events: list[MarketEvent]) -> None:
        net_liq = 0
        price_map = {e.symbol: e.data["close"] for e in market_events}
        
        for symbol, position in self.positions.items():
            if symbol in price_map:
                position.current_value = position.qty * price_map[symbol]
                net_liq += position.current_value

        self.net_liquidation_value = net_liq
    
    def get_positions_current_prices(self) -> dict:
        positions_prices = {}
        for symbol, position in self.positions.items():
            if position.qty != 0:
                positions_prices[symbol] = position.current_value / position.qty
            else:
                positions_prices[symbol] = None
        return positions_prices
    
    def __str__(self):
        return f"Current cash is: {self.cash}\nCurrent positions value is: {self.net_liquidation_value}\nCurrent total value: {self.cash+self.net_liquidation_value}\nPositions prices: {self.get_positions_current_prices()}\n\n"

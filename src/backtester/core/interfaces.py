from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from .events import MarketEvent, SignalEvent, OrderEvent, FillEvent

class DataHandler(ABC):
    """Port d'accès aux données de marché."""

    @abstractmethod
    def get_next(self) -> list[MarketEvent]:
        """Retourne les events de marché pour le timestamp courant (ou suivant)."""
        ...

    @abstractmethod
    def has_next(self) -> bool:
        ...

class Strategy(ABC):
    @abstractmethod
    def on_market_event(self, events: list[MarketEvent]) -> list[SignalEvent]:
        ...

class Portfolio(ABC):
    @abstractmethod
    def update_on_fill(self, fills: list[FillEvent], market_events: list[MarketEvent]) -> None:
        ...

    @abstractmethod
    def generate_orders(self, signals: list[SignalEvent], market_events: list[MarketEvent]) -> list[OrderEvent]:
        ...

class Broker(ABC):
    @abstractmethod
    def execute(self, orders: list[OrderEvent], market_events: list[MarketEvent]) -> list[FillEvent]:
        ...

class Clock(ABC):
    @abstractmethod
    def __iter__(self):
        ...
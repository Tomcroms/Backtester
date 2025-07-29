from __future__ import annotations
import pandas as pd
from typing import Iterator

class TradingClock:
    """Itérateur sur les timestamps de trading.

    Peut être alimenté par un DatetimeIndex filtré (jours ouvrés, horaires spécifiques).
    """

    def __init__(self, timestamps: pd.DatetimeIndex):
        self._ts = timestamps

    def __iter__(self) -> Iterator[pd.Timestamp]:
        for ts in self._ts:
            yield ts
from __future__ import annotations
from typing import Protocol
import pandas as pd

class DataStore(Protocol):
    def get_series(self, symbol: str) -> pd.DataFrame:
        ...
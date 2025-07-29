from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd

class BaseLoader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> pd.DataFrame:
        ...
from src.backtester.core.interfaces import DataHandler
from src.backtester.data.loaders.csv_loader import CSVLoader
from src.backtester.core.events import MarketEvent

class PERatioSingleCSVDataHandler(DataHandler):
    def __init__(self, loader: CSVLoader, symbol: str):
        df = loader.load()
        self._symbol = symbol
        self._df = df
        self._iter = iter(df.itertuples())
        self._next_row = None

    def has_next(self) -> bool:
        if self._next_row is not None:
            return True
        try:
            self._next_row = next(self._iter)
            return True
        except StopIteration:
            return False
    
    def get_next(self) -> list[MarketEvent]:
        row = self._next_row
        self._next_row = None
        return [
            MarketEvent(
                symbol=self._symbol,
                timestamp=row.Index,
                data={"pe": row.pe_ratio_value, "close": row.close}
            )
        ]
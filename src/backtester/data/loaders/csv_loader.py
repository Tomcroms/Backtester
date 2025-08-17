import pandas as pd
from src.backtester.data.loaders.base_loader import BaseLoader

class CSVLoader(BaseLoader):
    def __init__(self, path: str):
        self.path = path
    
    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, parse_dates=["Date"])
        df = df.drop(columns=[column for column in df.columns if column.startswith("Unnamed")])
        return df.set_index("Date").sort_index()
        
        #tell pandas to parse "date" as a datetime object
        #force column "date" to be the index of the dataframe
        #because index is now of type datetime which makes a the dataframe a time series
        #this allow the use of time series pandas function
from src.backtester.core.engine import BacktestEngine
from src.backtester.data.csv_handler import PERatioSingleCSVDataHandler
from src.backtester.data.loaders.csv_loader import CSVLoader
from src.backtester.strategy.pe_ratio_strategy import PERatioStrategy, PEParams
from src.backtester.portfolio.portfolio import SimplePortfolio
from src.backtester.execution.broker_sim import SimulatedBroker
from src.backtester.core.clock import TradingClock
import pandas as pd


PATH = "./src/backtester/data/csv/pe_ratio_full_sp500.csv"
INITIAL_AMOUNT = 1_000_000

engine = BacktestEngine(
    
    data=PERatioSingleCSVDataHandler(CSVLoader(PATH), "S&P"),
    strategy=PERatioStrategy(PEParams(), INITIAL_AMOUNT),
    portfolio=SimplePortfolio(INITIAL_AMOUNT),
    broker=SimulatedBroker()
)

engine.run()
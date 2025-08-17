# api/main.py
from __future__ import annotations
from typing import Any, Dict, List, Callable
from datetime import datetime
from dataclasses import asdict

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import uvicorn

# ---- your backtester bits
from src.backtester.core.engine import BacktestEngine, EngineConfig
from src.backtester.core.clock import TradingClock
from src.backtester.core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from src.backtester.data.loaders.csv_loader import CSVLoader
from src.backtester.data.csv_handler import (
    PERatioSingleCSVDataHandler,
    MultipleAssetsSingleSymbolCSVHandler,
)
from src.backtester.strategy.pe_ratio_strategy import PERatioStrategy, PEParams
from src.backtester.portfolio.portfolio import SimplePortfolio
from src.backtester.execution.broker_sim import SimulatedBroker

# ---------- tiny helpers ----------
def to_iso(ts) -> str:
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    if isinstance(ts, datetime):
        return ts.isoformat()
    return str(ts)

def serialize_market_events(events: List[MarketEvent]) -> List[Dict[str, Any]]:
    return [{"symbol": e.symbol, "timestamp": to_iso(e.timestamp), "data": e.data} for e in events]

def serialize_signals(signals: List[SignalEvent]) -> List[Dict[str, Any]]:
    out = []
    for s in signals:
        d = asdict(s)
        d["timestamp"] = to_iso(s.timestamp)
        out.append(d)
    return out

def serialize_orders(orders: List[OrderEvent]) -> List[Dict[str, Any]]:
    out = []
    for o in orders:
        d = asdict(o)
        d["timestamp"] = to_iso(o.timestamp)
        out.append(d)
    return out

def serialize_fills(fills: List[FillEvent]) -> List[Dict[str, Any]]:
    out = []
    for f in fills:
        d = asdict(f)
        d["timestamp"] = to_iso(f.timestamp)
        out.append(d)
    return out

def snapshot_portfolio(ts: datetime, p: SimplePortfolio) -> Dict[str, Any]:
    return {
        "timestamp": to_iso(ts),
        "cash": p.cash,
        "net_liquidation_value": p.net_liquidation_value,
        "total_value": p.cash + p.net_liquidation_value,
        "positions": [
            {
                "symbol": sym,
                "qty": pos.qty,
                "avg_price": pos.avg_price,
                "current_value": pos.current_value,
            }
            for sym, pos in p.positions.items()
        ],
    }

# ---------- factories (whitelist for safety) ----------
STRATEGIES: Dict[str, Callable[[float], Any]] = {
    "PERatioStrategy": lambda initial_cash: PERatioStrategy(PEParams(), initial_cash),
}

LOADERS: Dict[str, Callable[..., Any]] = {
    # For now only CSV
    "CSVLoader": lambda csv_path, **_: CSVLoader(csv_path),
}

HANDLERS: Dict[str, Callable[..., Any]] = {
    # Handler needs (loader, symbol)
    "PERatioSingleCSVDataHandler": lambda loader, symbol, **_: PERatioSingleCSVDataHandler(loader, symbol),
    "MultipleAssetsSingleSymbolCSVHandler": lambda loader, symbol, **_: MultipleAssetsSingleSymbolCSVHandler(loader, symbol),
}

def build_engine(
    symbol: str,
    strategy_name: str,
    loader_name: str,
    handler_name: str,
    initial_cash: float,
    csv_path: str,
) -> BacktestEngine:
    if strategy_name not in STRATEGIES:
        raise HTTPException(400, f"Unknown strategy '{strategy_name}'")
    if loader_name not in LOADERS:
        raise HTTPException(400, f"Unknown loader '{loader_name}'")
    if handler_name not in HANDLERS:
        raise HTTPException(400, f"Unknown handler '{handler_name}'")

    loader = LOADERS[loader_name](csv_path=csv_path)
    data = HANDLERS[handler_name](loader=loader, symbol=symbol)
    clock = TradingClock(data._df.index)  # drive by CSV index
    strategy = STRATEGIES[strategy_name](initial_cash)
    broker = SimulatedBroker(commission_per_trade=0.0, slippage_bp=0.0)
    portfolio = SimplePortfolio(cash=initial_cash)
    return BacktestEngine(data, strategy, portfolio, broker, clock, EngineConfig(verbose=False))

def run_and_collect(engine: BacktestEngine) -> List[Dict[str, Any]]:
    frames: List[Dict[str, Any]] = []
    iterator = engine.clock if engine.clock else iter(int, 1)
    for i, _ in enumerate(iterator):
        if not engine.data.has_next():
            break
        market_events: List[MarketEvent] = engine.data.get_next()
        signals: List[SignalEvent] = engine.strategy.on_market_event(market_events)
        orders: List[OrderEvent] = engine.portfolio.generate_orders(signals, market_events)
        fills: List[FillEvent] = engine.broker.execute(orders, market_events)
        engine.portfolio.update_on_fill(fills, market_events)

        ts = market_events[0].timestamp
        frames.append({
            "idx": i,
            "t": to_iso(ts),
            "market_events": serialize_market_events(market_events),
            "signals": serialize_signals(signals),
            "orders": serialize_orders(orders),
            "fills": serialize_fills(fills),
            "portfolio": snapshot_portfolio(ts, engine.portfolio),
        })
    return frames

# ---------- FastAPI app ----------
app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/replay-all")
def replay_all(
    symbol: str = Query(...),
    strategy: str = Query("PERatioStrategy"),
    loader: str = Query("CSVLoader"),
    handler: str = Query("PERatioSingleCSVDataHandler"),
    initial_cash: float = Query(100_000.0),
    csv_path: str = Query("src/backtester/data/csv/pe_ratio_full_sp500.csv"),
):
    """
    Example:
      GET /replay-all?symbol=SP500&strategy=PERatioStrategy&loader=CSVLoader&handler=PERatioSingleCSVDataHandler
    """
    engine = build_engine(symbol, strategy, loader, handler, initial_cash, csv_path)
    frames = run_and_collect(engine)
    return {
        "spec": {
            "symbol": symbol,
            "strategy": strategy,
            "loader": loader,
            "handler": handler,
            "initial_cash": initial_cash,
            "csv_path": csv_path,
        },
        "frames": frames,
        "final": True,
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

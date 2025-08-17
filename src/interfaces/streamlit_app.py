# ui/streamlit_app.py
import streamlit as st
from backtester.core.engine import BacktestEngine
# from my_project.setup import engine  # suppose que tu crées l'engine ici

class engine:
    def __init__(self):
        return True
    
# État global Streamlit
if "equity" not in st.session_state:
    st.session_state.equity_series = []

def on_tick(**payload):
    st.session_state.equity_series.append(payload["equity"])

engine.add_listener(on_tick)

col1, col2, col3 = st.columns(3)
if col1.button("▶ Play"):
    st.session_state.running = True
if col2.button("❚❚ Pause"):
    st.session_state.running = False
if col3.button("Step »"):
    engine.step()

# Boucle play
if st.session_state.get("running"):
    engine.step()

st.line_chart(st.session_state.equity_series[-200:])

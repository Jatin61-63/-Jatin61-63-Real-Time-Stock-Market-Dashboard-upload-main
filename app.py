import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Real-Time Stock Market Dashboard", page_icon="📈", layout="wide")

st.markdown("""
<style>
.stApp {background: #071326; color: #edf4ff;}
[data-testid="stSidebar"] {background: #0b1930;}
.metric-card {background:#0d203b;border:1px solid #203b5d;border-radius:12px;padding:14px 18px;}
h1,h2,h3 {color:#f2f6ff;}
</style>
""", unsafe_allow_html=True)

st.title("📈 Real-Time Stock Market Dashboard")
st.caption("Live market data • Interactive charts • Financial insights")
st.sidebar.header("Dashboard Controls")

WATCHLIST = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "ITC.NS": "ITC",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
}
symbol = st.sidebar.selectbox("Select stock", list(WATCHLIST), format_func=lambda x: f"{x} — {WATCHLIST[x]}")
period = st.sidebar.selectbox("History period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"], index=2)
interval_options = {"1d": ["1m", "5m", "15m", "30m", "60m"], "5d": ["5m", "15m", "30m", "60m"], "1mo": ["30m", "60m", "1d"], "3mo": ["1d"], "6mo": ["1d"], "1y": ["1d", "1wk"], "5y": ["1wk", "1mo"]}
interval = st.sidebar.selectbox("Chart interval", interval_options[period])
refresh = st.sidebar.button("🔄 Refresh data", use_container_width=True)
auto_refresh = st.sidebar.checkbox("Auto-refresh every 60 seconds", value=False)
st.sidebar.caption("Data provided by Yahoo Finance via yfinance. Quotes may be delayed.")

@st.cache_data(ttl=60)
def load_data(ticker, selected_period, selected_interval):
    hist = yf.Ticker(ticker).history(period=selected_period, interval=selected_interval, auto_adjust=False)
    info = {}
    try:
        info = yf.Ticker(ticker).get_info()
    except Exception:
        pass
    return hist, info

if refresh:
    load_data.clear()

try:
    with st.spinner("Loading market data…"):
        hist, info = load_data(symbol, period, interval)
except Exception as exc:
    st.error(f"Could not load market data: {exc}")
    st.info("Check your internet connection and try again.")
    st.stop()

if hist is None or hist.empty:
    st.warning("No data returned for this ticker/period. Try another symbol or interval.")
    st.stop()

hist = hist.dropna(subset=["Close"])
latest = hist.iloc[-1]
price = float(latest["Close"])
previous = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else float(latest.get("Open", price))
change = price - previous
pct = (change / previous * 100) if previous else 0
currency = info.get("currency", "USD" if symbol in ["AAPL", "MSFT", "GOOGL", "TSLA"] else "INR")
currency_symbol = "$" if currency == "USD" else "₹"
company = WATCHLIST[symbol]
st.caption(f"Selected: **{company} ({symbol})** · Last data point: {hist.index[-1].strftime('%d %b %Y, %H:%M') if hasattr(hist.index[-1], 'strftime') else hist.index[-1]}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Price", f"{currency_symbol}{price:,.2f}", f"{change:+,.2f} ({pct:+.2f}%)")
c2.metric("Day / Period High", f"{currency_symbol}{float(hist['High'].max()):,.2f}")
c3.metric("Day / Period Low", f"{currency_symbol}{float(hist['Low'].min()):,.2f}")
c4.metric("Volume", f"{float(latest['Volume']):,.0f}" if pd.notna(latest.get("Volume")) else "N/A")

left, right = st.columns([2.1, 1])
with left:
    st.subheader("Price & Volume")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"],
        name="Price", increasing_line_color="#00d6a0", decreasing_line_color="#ff5263"
    ))
    fig.update_layout(
        template="plotly_dark", height=500, margin=dict(l=10,r=10,t=25,b=10),
        paper_bgcolor="#0b1930", plot_bgcolor="#0b1930",
        xaxis_rangeslider_visible=False, legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    volume_fig = go.Figure(go.Bar(x=hist.index, y=hist["Volume"], marker_color="#3182f6", name="Volume"))
    volume_fig.update_layout(template="plotly_dark", height=180, margin=dict(l=10,r=10,t=10,b=10),
                             paper_bgcolor="#0b1930", plot_bgcolor="#0b1930")
    st.plotly_chart(volume_fig, use_container_width=True)

with right:
    st.subheader("Watchlist")
    rows = []
    for ticker, label in WATCHLIST.items():
        try:
            d = yf.Ticker(ticker).history(period="5d", interval="1d")
            if len(d) >= 2:
                p0, p1 = float(d["Close"].iloc[-2]), float(d["Close"].iloc[-1])
                rows.append({"Symbol": ticker.replace(".NS", ""), "Company": label,
                             "Last Price": p1, "Change (%)": ((p1-p0)/p0*100) if p0 else 0})
        except Exception:
            continue
    if rows:
        wl = pd.DataFrame(rows)
        st.dataframe(wl.style.format({"Last Price": "{:,.2f}", "Change (%)": "{:+.2f}%"}), use_container_width=True, hide_index=True)
    else:
        st.info("Watchlist quotes are temporarily unavailable.")

st.subheader("Historical Data")
show_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in hist.columns]
st.dataframe(hist[show_cols].sort_index(ascending=False), use_container_width=True)

with st.expander("Financial indicators"):
    a, b, c = st.columns(3)
    a.metric("Market Capitalization", f"{info.get('marketCap', 0):,}" if info.get("marketCap") else "N/A")
    b.metric("P/E Ratio", f"{info.get('trailingPE'):.2f}" if isinstance(info.get("trailingPE"), (int, float)) else "N/A")
    c.metric("52-week High", f"{currency_symbol}{info.get('fiftyTwoWeekHigh'):,.2f}" if isinstance(info.get("fiftyTwoWeekHigh"), (int, float)) else "N/A")

st.divider()
st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y, %H:%M:%S')} · Educational project only; not investment advice.")
if auto_refresh:
    st.info("Auto-refresh is enabled. Streamlit will refresh when the app reruns; use Refresh data for a manual update.")

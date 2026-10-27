# Real-Time Stock Market Dashboard

A Streamlit dashboard for exploring stock prices, candlestick charts, volume, a watchlist, and basic financial indicators.

## Tech stack
- Python
- Streamlit
- Pandas
- Plotly
- yfinance (market data source)

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (optional but recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL printed in the terminal (usually http://localhost:8501).

## Notes
- Uses Yahoo Finance data through `yfinance`; availability, intervals, and quote delays are controlled by the data provider.
- NSE symbols commonly end in `.NS` (e.g. `RELIANCE.NS`). US symbols are included too.
- This is an educational dashboard, not financial advice.
- For production use, use a licensed market-data provider and review its API terms.

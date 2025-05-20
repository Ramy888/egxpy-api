from fastapi import FastAPI
from datetime import datetime, date, timedelta
import pandas as pd
from tvDatafeed import TvDatafeedLive, Interval
from retry import retry

from egxpy.download import get_EGX_intraday_data

app = FastAPI()

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        # Define the interval and date range
        interval = '1 Minute'
        end = datetime.now()
        start = end - timedelta(days=1)

        # Fetch the intraday data
        df = get_EGX_intraday_data([ticker], interval, start, end)

        # Extract the latest price
        latest_price = df[ticker].dropna().iloc[-1]

        return {"success": True, "ticker": ticker, "price": latest_price}
    except Exception as e:
        return {"success": False, "error": str(e)}

@retry((Exception), tries=20, delay=0.5, backoff=0)
def _get_intraday_close_price_data(symbol, exchange, interval, n_bars):
    interval_dic = {
        '1 Minute': Interval.in_1_minute,
        '5 Minute': Interval.in_5_minute,
        '30 Minute': Interval.in_30_minute
    }

    tv = TvDatafeedLive()
    response = tv.get_hist(
        symbol=symbol,
        exchange=exchange,
        interval=interval_dic[interval],
        n_bars=n_bars,
        timeout=-1
    )['close']
    return response


@app.get("/intraday/{ticker}")
def get_intraday_price(
    ticker: str,
    interval: str = "5 Minute",
    n_bars: int = 50
):
    try:
        close_data = _get_intraday_close_price_data(
            symbol=ticker,
            exchange="EGX",
            interval=interval,
            n_bars=n_bars
        )

        df = close_data.reset_index()
        df.columns = ["datetime", "close"]
        df["datetime"] = df["datetime"].astype(str)
        return {
            "success": True,
            "ticker": ticker,
            "interval": interval,
            "n_bars": n_bars,
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

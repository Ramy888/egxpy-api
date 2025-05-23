from fastapi import FastAPI, Body
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List
import pytz
from egxpy.download import get_EGX_intraday_data
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/stocks/last7days")
def get_multiple_stocks_last7days(tickers: List[str] = Body(..., embed=True)):
    try:
        interval = '1 Minute'
        now = datetime.now(pytz.timezone("Africa/Cairo"))
        start = (now - timedelta(days=7)).replace(tzinfo=None)
        end = now.replace(tzinfo=None)

        data = {}
        df = get_EGX_intraday_data(tickers, interval, start, end)

        for ticker in tickers:
            if isinstance(df.columns, pd.MultiIndex):
                if ticker in df.columns.levels[0]:
                    stock_df = df[ticker].dropna().reset_index()
                    stock_df["datetime"] = stock_df["datetime"].astype(str)
                    data[ticker] = stock_df.to_dict(orient="records")
                else:
                    data[ticker] = "No data found"
            else:
                # Flat column case (single ticker)
                stock_df = df.dropna().reset_index()
                stock_df["datetime"] = stock_df["datetime"].astype(str)
                data[ticker] = stock_df.to_dict(orient="records")

        return {
            "success": True,
            "interval": interval,
            "start": str(start),
            "end": str(end),
            "data": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


class StockQuery(BaseModel):
    tickers: List[str]
    start: datetime
    end: datetime


@app.post("/stocks/customrange")
def get_multiple_stocks_custom_range(query: StockQuery):
    try:
        interval = '1 Minute'

        # Ensure timezone-aware datetimes (Cairo)
        tz = pytz.timezone("Africa/Cairo")
        start = query.start.astimezone(tz)
        end = query.end.astimezone(tz)

        data = {}
        df = get_EGX_intraday_data(query.tickers, interval, start, end)
        for ticker in query.tickers:
            if ticker in df.columns.levels[0]:
                stock_df = df[ticker].dropna().reset_index()
                stock_df["datetime"] = stock_df["datetime"].astype(str)
                data[ticker] = stock_df.to_dict(orient="records")
            else:
                data[ticker] = "No data found"

        return {
            "success": True,
            "interval": interval,
            "start": str(start),
            "end": str(end),
            "data": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}



@app.post("/stocks/today")
def get_today_intraday_data(tickers: List[str] = Body(..., embed=True)):
    try:
        interval = '1 Minute'
        cairo_tz = pytz.timezone("Africa/Cairo")
        now = datetime.now(cairo_tz)

        # Set start time to today at 9:00 AM Cairo time
        start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        # Set end time to today at 2:00 PM Cairo time
        end = now.replace(hour=14, minute=0, second=0, microsecond=0)

        df = get_EGX_intraday_data(tickers, interval, start, end)

        result = {}
        for ticker in tickers:
            if ticker in df.columns.levels[0]:
                stock_df = df[ticker].dropna().reset_index()
                stock_df["datetime"] = stock_df["datetime"].astype(str)
                result[ticker] = stock_df.to_dict(orient="records")
            else:
                result[ticker] = "No data found"

        return {
            "success": True,
            "interval": interval,
            "start": str(start),
            "end": str(end),
            "data": result
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
        

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        interval = "15min"
        today = datetime.today().strftime("%Y-%m-%d")
        
        data = get_EGX_intraday_data(ticker, interval, today, today)

        # Convert to list of dicts for JSON response if data is a DataFrame
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}



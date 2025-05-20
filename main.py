from fastapi import FastAPI
from egxpy.download import get_EGX_intraday_data
from datetime import datetime

app = FastAPI()

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        interval = "15min"
        today = datetime.today().strftime("%Y-%m-%d")
        
        data = get_EGX_intraday_data(ticker=ticker, interval=interval, start=today, end=today)

        # Convert to list of dicts for JSON response if data is a DataFrame
        return {"success": True, "data": data.to_dict(orient="records")}
    except Exception as e:
        return {"success": False, "error": str(e)}

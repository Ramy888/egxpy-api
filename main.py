from fastapi import FastAPI
from egxpy.stock_data import StockData  # or whatever you need

app = FastAPI()

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        data = stock_data.get_stock_summary(ticker)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

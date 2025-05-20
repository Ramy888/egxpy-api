from fastapi import FastAPI
from egxpy.download import get_EGX_intraday_data

app = FastAPI()

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        data = get_EGX_intraday_data(ticker)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

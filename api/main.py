from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()

engine = create_engine(
    "postgresql://nikhilsinghrathaur@localhost/stat_arb"
)

@app.get("/")
def home():
    return {
        "message":
        "Statistical Arbitrage API Running"
    }

@app.get("/prices")
def get_prices():

    query = """
    SELECT *
    FROM market_prices
    LIMIT 20
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(
        orient="records"
    )

@app.get("/signals")
def get_signals():

    return {
        "signal":
        "LONG_SPREAD"
    }
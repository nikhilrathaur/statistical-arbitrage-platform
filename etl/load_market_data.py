import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://nikhilsinghrathaur@localhost/stat_arb"
)

tickers = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "META",
    "GOOGL"
]

all_data = []

for ticker in tickers:

    df = yf.download(
        ticker,
        period="2y"
    )

    df.reset_index(inplace=True)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df.columns = [
        str(col).lower()
        for col in df.columns
    ]

    df['ticker'] = ticker

    df = df[['date', 'ticker', 'close']]

    all_data.append(df)

final_df = pd.concat(all_data)

final_df.to_sql(
    "market_prices",
    engine,
    if_exists="replace",
    index=False
)

print(final_df.head())

print("Market data loaded successfully!")
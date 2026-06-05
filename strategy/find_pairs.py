import pandas as pd
from sqlalchemy import create_engine
from statsmodels.tsa.stattools import coint

engine = create_engine(
    "postgresql://nikhilsinghrathaur@localhost/stat_arb"
)

query = "SELECT * FROM market_prices"

df = pd.read_sql(query, engine)

pivot_df = df.pivot(
    index='date',
    columns='ticker',
    values='close'
)

tickers = pivot_df.columns

pairs = []

for i in range(len(tickers)):

    for j in range(i + 1, len(tickers)):

        stock1 = pivot_df[tickers[i]]
        stock2 = pivot_df[tickers[j]]

        score, pvalue, _ = coint(
            stock1,
            stock2
        )

        if pvalue < 0.05:

            pairs.append(
                (
                    tickers[i],
                    tickers[j],
                    pvalue
                )
            )

print("\nCointegrated Pairs:\n")

for pair in pairs:
    print(pair)
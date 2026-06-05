import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://nikhilsinghrathaur@localhost/stat_arb"
)

query = """
SELECT *
FROM market_prices
WHERE ticker IN ('AAPL', 'MSFT')
"""

df = pd.read_sql(query, engine)

pivot_df = df.pivot(
    index='date',
    columns='ticker',
    values='close'
)

pivot_df['spread'] = (
    pivot_df['AAPL']
    - pivot_df['MSFT']
)

mean = pivot_df['spread'].mean()

std = pivot_df['spread'].std()

pivot_df['zscore'] = (
    (pivot_df['spread'] - mean)
    / std
)

pivot_df['signal'] = np.where(
    pivot_df['zscore'] > 2,
    'SHORT_SPREAD',
    np.where(
        pivot_df['zscore'] < -2,
        'LONG_SPREAD',
        'HOLD'
    )
)

print(
    pivot_df[
        ['spread', 'zscore', 'signal']
    ].tail(20)
)
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.graph_objects as go
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Quant Statistical Arbitrage Platform",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL APP
===================================================== */

html, body, [class*="css"]  {
    background-color: #0E1117;
    color: #FAFAFA;
    font-family: -apple-system, BlinkMacSystemFont,
                 "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Main app background */

.stApp {
    background-color: #0E1117;
    color: #FAFAFA;
}

/* =====================================================
TEXT FIXES
===================================================== */

/* ALL TEXT */

p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: #F9FAFB !important;
}

/* Markdown text */

.stMarkdown {
    color: #F9FAFB !important;
}

/* Captions */

.stCaption {
    color: #D1D5DB !important;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background-color: #151821;
    border-right: 1px solid #2A2F3A;
}

section[data-testid="stSidebar"] * {
    color: #F9FAFB !important;
}

/* =====================================================
INPUT BOXES
===================================================== */

/* Selectbox */

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #1B1F2A !important;
    color: white !important;
    border: 1px solid #374151 !important;
}

/* Dropdown menu */

div[role="listbox"] {
    background-color: #1B1F2A !important;
    color: white !important;
}

/* Slider */

.stSlider * {
    color: white !important;
}

/* =====================================================
METRIC CARDS
===================================================== */

.metric-card {
    background-color: #161B22;
    border: 1px solid #2D333B;
    border-radius: 8px;
    padding: 18px;
    height: 110px;
}

.metric-title {
    font-size: 12px;
    font-weight: 600;
    color: #9CA3AF !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #FFFFFF !important;
}

/* =====================================================
HEADINGS
===================================================== */

.dashboard-title {
    font-size: 36px;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 6px;
}

.dashboard-subtitle {
    font-size: 15px;
    color: #D1D5DB !important;
    margin-bottom: 30px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-top: 26px;
    margin-bottom: 12px;
}

/* =====================================================
DATAFRAMES
===================================================== */

[data-testid="stDataFrame"] {
    border: 1px solid #374151;
    border-radius: 8px;
}

/* Table text */

[data-testid="stDataFrame"] * {
    color: white !important;
}

/* =====================================================
EXPANDER
===================================================== */

.streamlit-expanderHeader {
    color: white !important;
}

/* =====================================================
BUTTONS
===================================================== */

.stButton button {
    background-color: #1F2937;
    color: white !important;
    border: 1px solid #374151;
}

/* =====================================================
BLOCK CONTAINER
===================================================== */

.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1500px;
}

/* Remove top white header */

header {
    visibility: hidden;
    height: 0px;
}

[data-testid="stHeader"] {
    background: #0E1117;
}

[data-testid="stToolbar"] {
    right: 2rem;
}

.main .block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE CONNECTION
# =====================================================

engine = create_engine(
    "postgresql://nikhilsinghrathaur@localhost/stat_arb"
)

# =====================================================
# LOAD DATA
# =====================================================

query = """
SELECT *
FROM market_prices
"""

df = pd.read_sql(query, engine)

df['date'] = pd.to_datetime(df['date'])

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Strategy Controls")

tickers = sorted(df['ticker'].unique())

ticker1 = st.sidebar.selectbox(
    "First Asset",
    tickers,
    index=0
)

ticker2 = st.sidebar.selectbox(
    "Second Asset",
    tickers,
    index=1
)

z_threshold = st.sidebar.slider(
    "Z-Score Threshold",
    1.0,
    3.0,
    2.0,
    0.1
)

rolling_window = st.sidebar.slider(
    "Rolling Window",
    10,
    60,
    30
)

# =====================================================
# TITLE
# =====================================================

st.markdown("""
<div class='dashboard-title'>
Quant Statistical Arbitrage Platform
</div>

<div class='dashboard-subtitle'>
Cointegration, spread analysis, z-score modelling and systematic signal generation.
</div>
""", unsafe_allow_html=True)

# =====================================================
# DATA PREP
# =====================================================

pair_df = df[
    df['ticker'].isin([ticker1, ticker2])
]

pivot_df = pair_df.pivot(
    index='date',
    columns='ticker',
    values='close'
)

pivot_df.dropna(inplace=True)

# =====================================================
# SPREAD MODEL
# =====================================================

pivot_df['spread'] = (
    pivot_df[ticker1]
    - pivot_df[ticker2]
)

pivot_df['rolling_mean'] = (
    pivot_df['spread']
    .rolling(rolling_window)
    .mean()
)

pivot_df['rolling_std'] = (
    pivot_df['spread']
    .rolling(rolling_window)
    .std()
)

pivot_df['zscore'] = (
    (pivot_df['spread']
     - pivot_df['rolling_mean'])
    / pivot_df['rolling_std']
)

# =====================================================
# SIGNALS
# =====================================================

pivot_df['signal'] = np.where(
    pivot_df['zscore'] > z_threshold,
    "SHORT_SPREAD",
    np.where(
        pivot_df['zscore'] < -z_threshold,
        "LONG_SPREAD",
        "HOLD"
    )
)

# =====================================================
# RETURNS
# =====================================================

pivot_df['position'] = np.where(
    pivot_df['zscore'] > z_threshold,
    -1,
    np.where(
        pivot_df['zscore'] < -z_threshold,
        1,
        0
    )
)

pivot_df['spread_returns'] = (
    pivot_df['spread'].pct_change()
)

pivot_df['strategy_returns'] = (
    pivot_df['position'].shift(1)
    * pivot_df['spread_returns']
)

pivot_df['cumulative_returns'] = (
    1 + pivot_df['strategy_returns'].fillna(0)
).cumprod()

# =====================================================
# KPI METRICS
# =====================================================

latest_spread = round(
    pivot_df['spread'].iloc[-1],
    2
)

latest_z = round(
    pivot_df['zscore'].iloc[-1],
    2
)

spread_vol = round(
    pivot_df['spread'].std(),
    2
)

signal = pivot_df['signal'].iloc[-1]

total_return = round(
    (
        pivot_df['cumulative_returns'].iloc[-1]
        - 1
    ) * 100,
    2
)

col1, col2, col3, col4, col5 = st.columns(5)

metrics = [
    ("Current Spread", latest_spread),
    ("Current Z-Score", latest_z),
    ("Spread Volatility", spread_vol),
    ("Signal", signal),
    ("Return %", total_return)
]

for col, metric in zip(
    [col1, col2, col3, col4, col5],
    metrics
):

    title, value = metric

    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>{title}</div>
            <div class='metric-value'>{value}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# COMMON CHART STYLE
# =====================================================

chart_layout = dict(
    template="plotly_dark",

    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",

    font=dict(
        family="Arial",
        size=14,
        color="#FFFFFF"
    ),

    title_font=dict(
        color="#FFFFFF",
        size=20
    ),

    xaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="#2D333B",
        zerolinecolor="#2D333B"
    ),

    yaxis=dict(
        title_font=dict(color="#FFFFFF"),
        tickfont=dict(color="#FFFFFF"),
        gridcolor="#2D333B",
        zerolinecolor="#2D333B"
    ),

    legend=dict(
        font=dict(
            color="#FFFFFF"
        )
    )
)

# =====================================================
# PRICE CHART
# =====================================================

st.markdown("""
<div class='section-title'>
Asset Price Comparison
</div>
""", unsafe_allow_html=True)

fig_prices = go.Figure()

fig_prices.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df[ticker1],
        mode='lines',
        name=ticker1
    )
)

fig_prices.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df[ticker2],
        mode='lines',
        name=ticker2
    )
)

fig_prices.update_layout(
    height=500,
    xaxis_title="Date",
    yaxis_title="Price",
    **chart_layout
)

st.plotly_chart(
    fig_prices,
    use_container_width=True
)

# =====================================================
# SPREAD CHART
# =====================================================

st.markdown("""
<div class='section-title'>
Spread Dynamics
</div>
""", unsafe_allow_html=True)

fig_spread = go.Figure()

fig_spread.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df['spread'],
        mode='lines',
        name='Spread'
    )
)

fig_spread.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df['rolling_mean'],
        mode='lines',
        name='Rolling Mean'
    )
)

fig_spread.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="Spread",
    **chart_layout
)

st.plotly_chart(
    fig_spread,
    use_container_width=True
)

# =====================================================
# Z-SCORE CHART
# =====================================================

st.markdown("""
<div class='section-title'>
Z-Score Signal Model
</div>
""", unsafe_allow_html=True)

fig_z = go.Figure()

fig_z.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df['zscore'],
        mode='lines',
        name='Z-Score'
    )
)

fig_z.add_hline(
    y=z_threshold,
    line_dash="dash"
)

fig_z.add_hline(
    y=-z_threshold,
    line_dash="dash"
)

fig_z.add_hline(
    y=0,
    line_dash="dash"
)

fig_z.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="Z-Score",
    **chart_layout
)

st.plotly_chart(
    fig_z,
    use_container_width=True
)

# =====================================================
# PERFORMANCE
# =====================================================

st.markdown("""
<div class='section-title'>
Strategy Performance
</div>
""", unsafe_allow_html=True)

fig_perf = go.Figure()

fig_perf.add_trace(
    go.Scatter(
        x=pivot_df.index,
        y=pivot_df['cumulative_returns'],
        mode='lines',
        name='Cumulative Returns'
    )
)

fig_perf.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="Portfolio Value",
    **chart_layout
)

st.plotly_chart(
    fig_perf,
    use_container_width=True
)

# =====================================================
# LOWER PANELS
# =====================================================

left, right = st.columns(2)

# =====================================================
# SIGNAL DISTRIBUTION
# =====================================================

with left:

    st.markdown("""
    <div class='section-title'>
    Signal Distribution
    </div>
    """, unsafe_allow_html=True)

    signal_counts = (
        pivot_df['signal']
        .value_counts()
        .reset_index()
    )

    signal_counts.columns = [
        'Signal',
        'Count'
    ]

    fig_bar = px.bar(
        signal_counts,
        x='Signal',
        y='Count',
        template='plotly_dark'
    )

    fig_bar.update_layout(
        template="plotly_dark",

        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",

        font=dict(
            family="Arial",
            size=14,
            color="#FFFFFF"
        ),

        xaxis=dict(
            tickfont=dict(color="#FFFFFF"),
            title_font=dict(color="#FFFFFF")
        ),

        yaxis=dict(
            tickfont=dict(color="#FFFFFF"),
            title_font=dict(color="#FFFFFF")
        )
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# =====================================================
# LATEST SIGNALS TABLE
# =====================================================

with right:

    st.markdown("""
    <div class='section-title'>
    Latest Trading Signals
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        pivot_df[
            ['spread', 'zscore', 'signal']
        ].tail(15),
        use_container_width=True
    )

# =====================================================
# RAW DATA
# =====================================================

with st.expander("Raw Market Data"):

    st.dataframe(
        df.tail(50),
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Statistical Arbitrage Research Infrastructure"
)
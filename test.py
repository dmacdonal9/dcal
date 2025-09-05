import pandas as pd
from datetime import datetime, timedelta
import pandas_market_calendars as mcal

from ib_async import FuturesOption

from ibstrat.ib_instance import connect_to_ib, ib
from ibstrat.adaptive import close_at_time

# Connect to TWS or IB Gateway
#connect_to_ib('127.0.0.1',7500,33,1)

# Define and qualify the individual legs
short_put = FuturesOption(
    symbol='ES',
    lastTradeDateOrContractMonth='20250714',
    strike=6000,
    right='P',
    multiplier='50',
    exchange='CME',
    currency='USD'
)

long_put = FuturesOption(
    symbol='ES',
    lastTradeDateOrContractMonth='20250714',
    strike=5900,
    right='P',
    multiplier='50',
    exchange='CME',
    currency='USD'
)

# NYSE calendar (covers US stock market holidays)
nyse = mcal.get_calendar("NYSE")


from ib_async import *
from math import isnan

from ib_async import FuturesOption

from ibstrat.ib_instance import connect_to_ib, ib
from ibstrat.adaptive import close_at_time

# Connect to TWS or IB Gateway
connect_to_ib('127.0.0.1',7500,33,1)

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

ib.qualifyContracts(short_put, long_put)

# Request market data for the individual legs
short_ticker = ib.reqMktData(short_put)
long_ticker = ib.reqMktData(long_put)
ib.sleep(2)
print(short_ticker)
print(long_ticker)
# Wait for market data to populate

order = close_at_time(short_put,'BUY',1,False,'test.py','20250714 14:00:00', False,'GTC')
print(order)
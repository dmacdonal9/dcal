from ib_async import *
from math import isnan

from ibstrat.ib_instance import connect_to_ib, ib
from ibstrat.adaptive import close_at_time

# Connect to TWS or IB Gateway
connect_to_ib('dte',7500,33,1)

# Define and qualify the individual legs
short_put = Option(
    symbol='SPX',
    lastTradeDateOrContractMonth='20250604',
    strike=6000,
    right='P',
    multiplier='100',
    exchange='CBOE',
    currency='USD'
)

long_put = Option(
    symbol='SPX',
    lastTradeDateOrContractMonth='20250604',
    strike=5900,
    right='P',
    multiplier='100',
    exchange='CBOE',
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

order = close_at_time(short_put,'BUY',1,False,'testadaptive','15:00:00', False,'GTC')
print(order)
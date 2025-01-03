from ib_async import *
from math import isnan

from ibstrat.ib_instance import connect_to_ib, ib
from ibstrat.market_data import get_combo_pricesv2, get_combo_prices

def round_to_tick(price, tick_size):
    if price is not None and tick_size is not None and not (isinstance(price, float) and isnan(price)):
        return round(price / tick_size) * tick_size
    return None

# Connect to TWS or IB Gateway
connect_to_ib('127.0.0.1',7500,33,1)

# Define and qualify the individual legs
short_put = FuturesOption(
    symbol='ES',
    lastTradeDateOrContractMonth='20250103',
    strike=5800,
    right='P',
    multiplier='50',
    exchange='CME',
    currency='USD'
)

long_put = FuturesOption(
    symbol='ES',
    lastTradeDateOrContractMonth='20250103',
    strike=5600,
    right='P',
    multiplier='50',
    exchange='CME',
    currency='USD'
)

ib.qualifyContracts(short_put, long_put)

# Request market data for the individual legs
short_ticker = ib.reqMktData(short_put)
long_ticker = ib.reqMktData(long_put)
print(short_ticker)
print(long_ticker)
# Wait for market data to populate
ib.sleep(2)

legs = [
    (short_put, "SELL", 1),  # Selling one 5900 put
    (long_put, "BUY", 1)     # Buying one 5800 put
]

# Pass legs as expected by get_combo_pricesv2
combo_bid, combo_mid, combo_ask = get_combo_pricesv2(legs)


# Display calculated combo prices
print(f"Combo Price:")
print(f"  Bid = {combo_bid if combo_bid is not None else 'Unavailable'}")
print(f"  Mid = {combo_mid if combo_mid is not None else 'Unavailable'}")
print(f"  Ask = {combo_ask if combo_ask is not None else 'Unavailable'}")

combo_bid, combo_mid, combo_ask = get_combo_prices(legs)


# Display calculated combo prices
print(f"Combo Price:")
print(f"  Bid = {combo_bid if combo_bid is not None else 'Unavailable'}")
print(f"  Mid = {combo_mid if combo_mid is not None else 'Unavailable'}")
print(f"  Ask = {combo_ask if combo_ask is not None else 'Unavailable'}")
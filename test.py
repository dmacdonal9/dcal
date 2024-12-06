from ib_insync import IB, Contract

# Connect to IB
ib = IB()
ib.connect('127.0.0.1', 7500, clientId=1)

def test_option_chain(symbol, secType, exchange, conId):
    """
    Test fetching option chain details for a given symbol.
    """
    try:
        print(f"Testing option chain for {symbol}...")
        option_chain = ib.reqSecDefOptParams(symbol, exchange, secType, conId)
        if option_chain:
            print(f"Option chain for {symbol}: {option_chain}")
        else:
            print(f"No option chain data returned for {symbol}.")
    except Exception as e:
        print(f"Error fetching option chain for {symbol}: {e}")

# Test SPX
test_option_chain(symbol='SPX', secType='IND', exchange='', conId=416904)

# Test NDX
test_option_chain(symbol='NDX', secType='IND', exchange='', conId=416843)

ib.disconnect()
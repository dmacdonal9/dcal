# Default configuration (live trading)
myStrategyTag = 'DC'
symbol = 'SPX'
exchange = 'CBOE'
quantity = 1
target_put_delta = 25
target_call_delta = 15
short_expiry_days = 1
long_expiry_days = 7

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 1  # Client ID for live trading

# Testing configuration
test_ib_host = '127.0.0.1'
test_ib_port = 7500  # Port for test TWS
test_ib_clientid = 2  # Client ID for test TWS

time_to_close = '09:34:00'  # The time to close the position (HH:MM:SS format) in EST

myStrategyTag = 'DC'

symbol = 'SPX'

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7497  # Port should be an integer
ib_clientid = 1  # Client ID should also be an integer

short_expiry_days = 1
long_expiry_days = 7

quantity = 1

target_put_delta = 25
target_call_delta = 15

time_to_close = '09:35:00'  # The time to close the position (HH:MM:SS format)

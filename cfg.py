myStrategyTag = 'DC'

symbol = 'SPX'
exchange='CBOE'
quantity = 1
target_put_delta = 25
target_call_delta = 15
short_expiry_days = 1
long_expiry_days = 7

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Port should be an integer
ib_clientid = 1  # Client ID should also be an integer

time_to_close = '09:34:00'  # The time to close the position (HH:MM:SS format) in EST

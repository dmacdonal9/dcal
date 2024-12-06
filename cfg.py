myStrategyTag = 'DC'

symbol_list = ['SPX','NDX','RUT']
symbol_list = ['SPX','NDX']

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7500  # Port should be an integer
ib_clientid = 1  # Client ID should also be an integer

# Double Calendar Parameters for Instruments
dc_param = {
    'SPX': {
        "conid": 416904,
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "mult": '1',
        "long_delta": 20,
        "short_delta": 20,
        "short_expiry_days": 5,       # Short leg expiration (in days)
        "long_expiry_days": 7,       # Long leg expiration (in days)
    },
    'RUT': {
        "conid": 416888,
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'RUSSELL',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "mult": '1',
        "long_delta": 20,
        "short_delta": 20,
        "short_expiry_days": 5,       # Short leg expiration (in days)
        "long_expiry_days": 21,       # Long leg expiration (in days)
    },
    'NDX': {
        "conid": 416843,
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "mult": '1',
        "long_delta": 20,
        "short_delta": 20,
        "short_expiry_days": 5,       # Short leg expiration (in days)
        "long_expiry_days": 7,       # Long leg expiration (in days)
    },
    'SPY': {
        "conid": 756733,
        "quantity": 1,
        "min_tick": 0.01,
        "live_order": False,
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "mult": '1',
        "long_delta": 20,
        "short_delta": 20,
        "short_expiry_days": 5,  # Short leg expiration (in days)
        "long_expiry_days": 7,  # Long leg expiration (in days)
    },
    'QQQ': {
        "conid": 320227571,
        "quantity": 1,
        "min_tick": 0.01,
        "live_order": False,
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "mult": '1',
        "long_delta": 20,
        "short_delta": 20,
        "short_expiry_days": 5,  # Short leg expiration (in days)
        "long_expiry_days": 7,  # Long leg expiration (in days)
    }
}

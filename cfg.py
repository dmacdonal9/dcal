# Default configuration (live trading)
weekly_dcal_tag = 'WDC'
weekly_dc_symbols = ['SPX','NDX','RUT']

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 1  # Client ID for live trading

# Testing configuration
test_ib_host = '127.0.0.1'
test_ib_port = 7500  # Port for test TWS
test_ib_clientid = 2  # Client ID for test TWS

time_to_close = '09:34:00'  # The time to close the position (HH:MM:SS format) in EST

dc_params = {
    'IWM':
        {
        "quantity": 1,
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "trading_class": '',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 3,
        "long_expiry_days": 7,
        },
    'NDX':
        {
        "quantity": 1,
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "target_put_delta": 25,
        "target_call_delta": 15,
        "short_expiry_days": 3,
        "long_expiry_days": 7,
        },
    'RUT':
        {
        "quantity": 1,
        "exchange": 'RUSSELL',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'RUTW',
        "mult": '100',
        "target_put_delta": 25,
        "target_call_delta": 15,
        "short_expiry_days": 5,
        "long_expiry_days": 21,
        },
    'SPX':
        {
        "quantity": 1,
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "target_put_delta": 25,
        "target_call_delta": 15,
        "short_expiry_days": 3,
        "long_expiry_days": 7,
        },
    }


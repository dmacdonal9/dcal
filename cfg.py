# Default configuration (live trading)
daily_dcal_tag = 'DDC'
weekly_dcal_tag = 'WDC'

daily_dc_symbols = ['SPX','NDX','RUT']
daily_dc_symbols = ['SPX']
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

daily_dc_params = {
    'ES':
        {
        "quantity": 1,
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "mult": '50',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 1,
        "long_expiry_days": 7,
        },
    'NDX':
        {
        "quantity": 1,
        "exchange": 'NASDAQ',
        "opt_exchange": 'SMART',
        "sec_type": 'IND',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 1,
        "long_expiry_days": 7,
        },
    'RUT':
        {
        "quantity": 1,
        "exchange": 'RUSSELL',
        "opt_exchange": 'SMART',
        "sec_type": 'IND',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 1,
        "long_expiry_days": 7,
        },
    'SPX':
        {
        "quantity": 1,
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 1,
        "long_expiry_days": 7,
        },
    }

weekly_dc_params = {
    'ES':
        {
        "quantity": 1,
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "mult": '50',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_expiry_days": 5,
        "long_expiry_days": 9,
        },
    'NDX':
        {
        "quantity": 1,
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "mult": '100',
        "target_put_delta": 25,
        "target_call_delta": 15,
        "short_expiry_days": 5,
        "long_expiry_days": 7,
        },
    'RUT':
        {
        "quantity": 1,
        "exchange": 'RUSSELL',
        "opt_exchange": 'SMART',
        "sec_type": 'IND',
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
        "mult": '100',
        "target_put_delta": 25,
        "target_call_delta": 15,
        "short_expiry_days": 5,
        "long_expiry_days": 7,
        },
    }


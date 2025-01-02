# Default configuration (live trading)
fri_dcal_tag = 'FDC'
fri_dc_symbols = ['SPX','NDX','RUT']
mon_dcal_tag = 'MDC'
mon_dc_symbols = ['SPX','NDX']

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 1  # Client ID for live trading

# Testing configuration
test_ib_host = '127.0.0.1'
test_ib_port = 7500  # Port for test TWS
test_ib_clientid = 2  # Client ID for test TWS

mon_dc_params = {
    'NDX':
        {
        "quantity": 1,
        "strategy_tag": 'MDC',
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 2,
        "short_call_expiry_days": 4,
        "long_put_expiry_days": 2,
        "long_call_expiry_days": 7,
        },
    'SPX':
        {
        "quantity": 1,
        "strategy_tag": 'MDC',
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 2,
        "short_call_expiry_days": 4,
        "long_put_expiry_days": 2,
        "long_call_expiry_days": 7,
        },
    }


fri_dc_params = {
    'IWM':
        {
        "quantity": 1,
        "strategy_tag": 'FDC',
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "trading_class": '',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 21,
        "long_call_expiry_days": 21,
        },
    'NDX':
        {
        "quantity": 1,
        "strategy_tag": 'FDC',
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        },
    'RUT':
        {
        "quantity": 1,
        "strategy_tag": 'FDC',
        "exchange": 'RUSSELL',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'RUTW',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 21,
        "long_call_expiry_days": 21,
        },
    'SPX':
        {
        "quantity": 1,
        "strategy_tag": 'FDC',
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        },
    }


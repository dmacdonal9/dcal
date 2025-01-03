# Default configuration (live trading)
fri_dc_symbols = ['SPX', 'NDX', 'RUT']
mon_dc_symbols = ['SPX', 'NDX']

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 1  # Client ID for live trading

# Testing configuration
test_ib_host = '127.0.0.1'
test_ib_port = 7500  # Port for test TWS
test_ib_clientid = 2  # Client ID for test TWS

# Friday Double Calendar Parameters
fri_dc_params = {
    'SPX': [
        {
            "quantity": 1,
            "strategy_tag": 'FDC57',
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
        {
            "quantity": 1,
            "strategy_tag": 'FDC37',
            "exchange": 'CBOE',
            "opt_exchange": 'CBOE',
            "sec_type": 'IND',
            "trading_class": 'SPXW',
            "mult": '100',
            "target_put_delta": 25,
            "target_call_delta": 15,
            "short_put_expiry_days": 3,
            "short_call_expiry_days": 3,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
        },
    ],
    'NDX': [
        {
            "quantity": 1,
            "strategy_tag": 'FDC57',
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
        {
            "quantity": 1,
            "strategy_tag": 'FDC37',
            "exchange": 'NASDAQ',
            "opt_exchange": 'ISE',
            "sec_type": 'IND',
            "trading_class": 'NDXP',
            "mult": '100',
            "target_put_delta": 18,
            "target_call_delta": 12,
            "short_put_expiry_days": 3,
            "short_call_expiry_days": 3,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
        },
    ],
    'RUT': [
        {
            "quantity": 1,
            "strategy_tag": 'FDC521',
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
    ],
    'ES': [
        {
            "quantity": 1,
            "strategy_tag": 'FDC37',
            "exchange": 'CME',
            "opt_exchange": 'CME',
            "sec_type": 'FUT',
            "trading_class": '',
            "mult": '50',
            "target_put_delta": 20,
            "target_call_delta": 20,
            "short_put_expiry_days": 3,
            "short_call_expiry_days": 3,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
        },
    ],
}

# Monday Double Calendar Parameters (unchanged)
mon_dc_params = {
    'NDX': {
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "strategy_tag": 'MDC2427',
        "target_put_delta": 20,
        "quantity": 1,
        "target_call_delta": 18,
        "short_put_expiry_days": 2,
        "short_call_expiry_days": 4,
        "long_put_expiry_days": 2,
        "long_call_expiry_days": 7,
    },
    'SPX': {
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "quantity": 1,
        "strategy_tag": 'MDC2427',
        "target_put_delta": 20,
        "target_call_delta": 18,
        "short_put_expiry_days": 2,
        "short_call_expiry_days": 4,
        "long_put_expiry_days": 2,
        "long_call_expiry_days": 7,
    },
}
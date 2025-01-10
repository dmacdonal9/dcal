# Default configuration (live trading)
fri_dc_symbols = ['SPX', 'NDX']
fri_dc_symbols = ['NDX']
mon_dc_symbols = ['SPX', 'NDX']
wed_dc_symbols = ['SPX', 'NDX']


dcal_close_time = '16:00:00'

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
            "submit_auto_close": True,
        },
        {
            "quantity": 1,
            "strategy_tag": 'FDC37',
            "exchange": 'CBOE',
            "opt_exchange": 'CBOE',
            "sec_type": 'IND',
            "trading_class": 'SPXW',
            "mult": '100',
            "target_put_delta": 45,
            "target_call_delta": 25,
            "short_put_expiry_days": 3,
            "short_call_expiry_days": 3,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
            "submit_auto_close": True,
        },
    ],
    'NDX': [
        {
            "quantity": 1,
            "strategy_tag": 'FDC57',
            "exchange": 'NASDAQ',
            "opt_exchange": 'CBOE',
            "sec_type": 'IND',
            "trading_class": 'NDXP',
            "mult": '100',
            "target_put_delta": 20,
            "target_call_delta": 20,
            "short_put_expiry_days": 5,
            "short_call_expiry_days": 5,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
            "submit_auto_close": True,
        },
        {
            "quantity": 1,
            "strategy_tag": 'FDC37',
            "exchange": 'NASDAQ',
            "opt_exchange": 'CBOE',
            "sec_type": 'IND',
            "trading_class": 'NDXP',
            "mult": '100',
            "target_put_delta": 25,
            "target_call_delta": 20,
            "short_put_expiry_days": 3,
            "short_call_expiry_days": 3,
            "long_put_expiry_days": 7,
            "long_call_expiry_days": 7,
            "submit_auto_close": True,
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
            "submit_auto_close": True,
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
    'NDX': [
        {
            "exchange": 'NASDAQ',
            "opt_exchange": 'ISE',
            "sec_type": 'IND',
            "trading_class": 'NDXP',
            "mult": '100',
            "quantity": 1,
            "strategy_tag": 'MDC2427',
            "target_put_delta": 20,
            "target_call_delta": 18,
            "short_put_expiry_days": 2,
            "short_call_expiry_days": 2,
            "long_put_expiry_days": 4,
            "long_call_expiry_days": 7,
            "submit_auto_close": True,
        }
    ],
    'SPX': [
        {
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
            "short_call_expiry_days": 2,
            "long_put_expiry_days": 4,
            "long_call_expiry_days": 7,
            "submit_auto_close": True,
        }
    ],
}

wed_dc_params = {
    'NDX': [
        {
            "exchange": 'NASDAQ',
            "opt_exchange": 'ISE',
            "sec_type": 'IND',
            "trading_class": 'NDXP',
            "mult": '100',
            "strategy_tag": 'WDC78',
            "quantity": 1,
            "target_put_delta": 50,
            "target_call_delta": 12,
            "short_put_expiry_days": 7,
            "short_call_expiry_days": 7,
            "long_put_expiry_days": 8,
            "long_call_expiry_days": 8,
            "submit_auto_close": True,
        }
    ],
    'SPX': [
        {
            "exchange": 'CBOE',
            "opt_exchange": 'CBOE',
            "sec_type": 'IND',
            "trading_class": 'SPXW',
            "mult": '100',
            "quantity": 1,
            "strategy_tag": 'WDC78',
            "target_put_delta": 50,
            "target_call_delta": 12,
            "short_put_expiry_days": 7,
            "short_call_expiry_days": 7,
            "long_put_expiry_days": 8,
            "long_call_expiry_days": 8,
            "submit_auto_close": True,
        }
    ],
}
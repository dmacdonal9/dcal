# Default configuration (live trading)
fri_dc_symbols = ['SPX', 'NQ']
mon_dc_symbols = ['SPX', 'QQQ']
wed_dc_symbols = ['SPX', 'QQQ']

dcal_close_time = '16:00:00'
adaptive_priority = 'Patient'
trade_log_sheet_id = "1KnYcYCizbkLP3GHQfsdmoXoulOcwyw_FRWGedQpfflI"

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 3  # Client ID for live trading

# Testing configuration
test_ib_host = '127.0.0.1'
test_ib_port = 7500  # Port for test TWS
test_ib_clientid = 3  # Client ID for test TWS

# Friday Double Calendar Parameters (primary)
fri_57dc_params = {
    'SPX': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "target_put_delta": 15,
        "target_call_delta": 15,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "submit_auto_close": False,
    },
    'QQQ': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "trading_class": '',
        "mult": '100',
        "target_put_delta": 15,
        "target_call_delta": 15,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "submit_auto_close": False,
    },
    'NQ': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "trading_class": '',
        "mult": '20',
        "target_put_delta": 15,
        "target_call_delta": 15,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "submit_auto_close": False,
    },
    'NDX': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'NASDAQ',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "target_put_delta": 15,
        "target_call_delta": 15,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "submit_auto_close": True,
    },
    'RUT': {
        "quantity": 1,
        "strategy_tag": 'FDC521',
        "exchange": 'RUSSELL',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'RUTW',
        "mult": '100',
        "target_put_delta": 15,
        "target_call_delta": 15,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 21,
        "long_call_expiry_days": 21,
        "submit_auto_close": True,
    },
    # ES has only one config, treating it as primary
    'ES': {
        "quantity": 1,
        "strategy_tag": 'FDC37',
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "trading_class": '',
        "mult": '50',
        "target_put_delta": 45,
        "target_call_delta": 25,
        "short_put_expiry_days": 3,
        "short_call_expiry_days": 3,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
    },
}

# Friday Double Calendar Parameters (secondary)
fri_37dc_params = {
    'SPX': {
        "quantity": 1,
        "strategy_tag": 'FDC37',
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'SPXW',
        "mult": '100',
        "target_put_delta": 30,
        "target_call_delta": 20,
        "short_put_expiry_days": 3,
        "short_call_expiry_days": 3,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        "submit_auto_close": False,
    },
    'QQQ': {
        "quantity": 1,
        "strategy_tag": 'FDC37',
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "trading_class": '',
        "mult": '100',
        "target_put_delta": 30,
        "target_call_delta": 20,
        "short_put_expiry_days": 3,
        "short_call_expiry_days": 3,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        "submit_auto_close": True,
    },
    'NQ': {
        "quantity": 1,
        "strategy_tag": 'FDC37',
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "trading_class": '',
        "mult": '20',
        "target_put_delta": 30,
        "target_call_delta": 20,
        "short_put_expiry_days": 3,
        "short_call_expiry_days": 3,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        "submit_auto_close": True,
    },
    'NDX': {
        "quantity": 1,
        "strategy_tag": 'FDC37',
        "exchange": 'NASDAQ',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "trading_class": 'NDXP',
        "mult": '100',
        "target_put_delta": 30,
        "target_call_delta": 20,
        "short_put_expiry_days": 3,
        "short_call_expiry_days": 3,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 7,
        "submit_auto_close": True,
    },
}

# Monday Double Calendar Parameters (unchanged)
mon_dc_params = {
    'NQ': [
        {
            "exchange": 'CME',
            "opt_exchange": 'CME',
            "sec_type": 'FUT',
            "trading_class": '',
            "mult": '20',
            "quantity": 1,
            "strategy_tag": 'MDC2427',
            "target_put_delta": 30,
            "target_call_delta": 18,
            "short_put_expiry_days": 2,
            "short_call_expiry_days": 2,
            "long_put_expiry_days": 4,
            "long_call_expiry_days": 7,
            "submit_auto_close": False,
        }
    ],
    'QQQ': [
        {
            "exchange": 'SMART',
            "opt_exchange": 'CBOE',
            "sec_type": 'STK',
            "trading_class": '',
            "mult": '100',
            "quantity": 1,
            "strategy_tag": 'MDC2427',
            "target_put_delta": 30,
            "target_call_delta": 18,
            "short_put_expiry_days": 2,
            "short_call_expiry_days": 2,
            "long_put_expiry_days": 4,
            "long_call_expiry_days": 7,
            "submit_auto_close": False,
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
            "target_put_delta": 30,
            "target_call_delta": 18,
            "short_put_expiry_days": 2,
            "short_call_expiry_days": 2,
            "long_put_expiry_days": 4,
            "long_call_expiry_days": 7,
            "submit_auto_close": False,
        }
    ],
}

# Wednesday Double Calendar Parameters (unchanged)
wed_dc_params = {
    'NQ': [
        {
            "exchange": 'NASDAQ',
            "opt_exchange": 'CME',
            "sec_type": 'FUT',
            "trading_class": '',
            "mult": '20',
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
    'QQQ': [
        {
            "exchange": 'NASDAQ',
            "opt_exchange": 'CBOE',
            "sec_type": 'STK',
            "trading_class": '',
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
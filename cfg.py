# Default configuration (live trading)
fri_57dc_symbols = ['SPX', 'NQ']
fri_37dc_symbols = ['SPX', 'NQ']
mon_dc_symbols = ['SPX', 'QQQ']
wed_dc_symbols = ['SPX', 'QQQ']
wed_dc_symbols = ['QQQ']

adaptive_priority = 'Normal'
adjust_sleep_interval = 4

# IBKR Connection Parameters
ib_host = '127.0.0.1'
ib_port = 7496  # Default live trading port
ib_clientid = 3  # Client ID for live trading

# Testing configuration
test_ib_host = 'dte'
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
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'QQQ': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'SMART',
        "opt_exchange": 'CBOE',
        "sec_type": 'STK',
        "trading_class": '',
        "mult": '100',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'NQ': {
        "quantity": 1,
        "strategy_tag": 'FDC57',
        "exchange": 'CME',
        "opt_exchange": 'CME',
        "sec_type": 'FUT',
        "trading_class": '',
        "mult": '20',
        "target_put_delta": 20,
        "target_call_delta": 20,
        "short_put_expiry_days": 5,
        "short_call_expiry_days": 5,
        "long_put_expiry_days": 7,
        "long_call_expiry_days": 10,
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'NDX': {
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
        "long_call_expiry_days": 10,
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'RUT': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
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
        "profit_target_pct": 20,
        "submit_auto_close": True,
        "close_time": '18:00:00',  # 2PM Atlantic
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
        "profit_target_pct": 20,
        "submit_auto_close": True,
        "close_time": '18:00:00',  # 2PM Atlantic
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
        "profit_target_pct": 20,
        "submit_auto_close": True,
        "close_time": '18:00:00',  # 2PM Atlantic
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
        "profit_target_pct": 20,
        "submit_auto_close": True,
        "close_time": '18:00:00',  # 2PM Atlantic
    },
}

# Monday Double Calendar Parameters (unchanged)
# Monday Double Calendar Parameters (corrected)
mon_dc_params = {
    'NQ': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'QQQ': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'SPX': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
}

wed_dc_params = {
    'NQ': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'QQQ': {
        "exchange": 'SMART',
        "opt_exchange": 'SMART',
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
    'SPX': {
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
        "profit_target_pct": -1,
        "submit_auto_close": True,
        "close_time": '20:00:00',  # 4PM Atlantic
    },
}
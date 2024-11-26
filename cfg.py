myStrategyTag = 'MEIC'

ib_host='127.0.0.1'
ib_port='7497'
ib_clientid='1'

stop_loss_mult = 1.5

dc_param = {
    'SPX':
        {
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "mult": '1',
        "long_strike_distance": 2.5,
        "short_strike_distance": 2.5,
        "short_expiry_days": 5,
        "long_expiry_days": 7,
        },
    'RUT':
        {
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'CBOE',
        "opt_exchange": 'CBOE',
        "sec_type": 'IND',
        "mult": '1',
        "short_put_strike_offset": 5,
        "short_call_strike_offset": 5,
        "long_put_target_price": 0.05,
        "long_call_target_price": 0.05,
        },
    'NDX':
        {
        "quantity": 1,
        "min_tick": 0.1,
        "live_order": False,
        "exchange": 'NASDAQ',
        "opt_exchange": 'ISE',
        "sec_type": 'IND',
        "mult": '1',
        "short_put_strike_offset": 10,
        "short_call_strike_offset": 10,
        "long_put_target_price": 0.2,
        "long_call_target_price": 0.2,
        }
    }
# can't trade if less than this many minutes to close
minutes_till_close_required = 120
minutes_after_open_required = 2


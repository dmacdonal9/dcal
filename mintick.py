min_tick_data = {
    "ES": {  # E-mini S&P 500 Futures Options (FOP)
        "thresholds": [
            {"max_price": 10.00, "tick_size": 0.05, "tick_value": 2.50},
            {"max_price": float('inf'), "tick_size": 0.25, "tick_value": 12.50}
        ]
    },
    "NQ": {  # E-mini Nasdaq 100 Futures Options (FOP)
        "thresholds": [
            {"max_price": 5.00, "tick_size": 0.05, "tick_value": 1.00},
            {"max_price": float('inf'), "tick_size": 0.25, "tick_value": 5.00}
        ]
    },
    "RTY": {  # E-mini Russell 2000 Futures Options (FOP)
        "thresholds": [
            {"max_price": 5.00, "tick_size": 0.05, "tick_value": 5.00},
            {"max_price": float('inf'), "tick_size": 0.10, "tick_value": 10.00}
        ]
    },
    "SPX": {  # S&P 500 Index Options (OPT)
        "thresholds": [
            {"max_price": 3.00, "tick_size": 0.05, "tick_value": 5.00},
            {"max_price": float('inf'), "tick_size": 0.10, "tick_value": 10.00}
        ]
    },
    "NDX": {  # Nasdaq 100 Index Options (OPT)
        "thresholds": [
            {"max_price": 3.00, "tick_size": 0.05, "tick_value": 5.00},
            {"max_price": float('inf'), "tick_size": 0.1, "tick_value": 10.00}
        ]
    },
    "RUT": {  # Russell 2000 Index Options (OPT)
        "thresholds": [
            {"max_price": 3.00, "tick_size": 0.05, "tick_value": 5.00},
            {"max_price": float('inf'), "tick_size": 0.10, "tick_value": 10.00}
        ]
    }
}
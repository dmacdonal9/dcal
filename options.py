from datetime import datetime
from ib_insync import Contract, Option, FuturesOption
from ib_instance import ib
import math
import logging

logging.getLogger('ib_insync').setLevel(logging.CRITICAL)

def find_option_closest_to_delta(tickers, right, target_delta):
    options = [option for option in tickers if option.contract.right == right and option.modelGreeks is not None]

    print("find_option_closest_to_delta(): ", right, target_delta)
    print("find_option_closest_to_delta(): Before filtering we have: ", len(options))

    if not options:
        print(f"find_option_closest_to_delta(): nothing found close to delta {target_delta}")
        return None

    # Filter for options with delta equal or greater than target_delta
    filtered_options = [option for option in options if (abs(option.modelGreeks.delta) * 100)  <= target_delta]
    print("find_option_closest_to_delta(): After delta filter we have count of: ", len(filtered_options))
    # Get the option with maximum strike among the filtered options
    closest_option = max(filtered_options, key=lambda x: x.contract.strike, default=None)
    print(closest_option)

    if closest_option:
        print(
            f"find_option_closest_to_delta(): closest option strike is {closest_option.contract.strike} with delta {closest_option.modelGreeks.delta}")
    else:
        print("No options with delta less than or equal to target_delta were found.")

    return closest_option

def get_closest_strike(contract, right, exchange, expiry, price):
    print(f"Entering function: get_closest_strike with parameters: {locals()}")
    try:
        option_secType = 'FOP' if contract.secType == 'FUT' else 'OPT'
        option_contract = Contract()
        option_contract.symbol = contract.symbol
        option_contract.secType = option_secType
        option_contract.exchange = exchange
        option_contract.currency = contract.currency
        option_contract.lastTradeDateOrContractMonth = expiry
        option_contract.right = right  # 'C' for Call, 'P' for Put

        # Fetch option chain details
        option_chain = ib.reqContractDetails(option_contract)
        if not option_chain:
            print(f"Warning: No options found for symbol {contract.symbol}, expiry {expiry}, right {right}, exchange {exchange}.")
            return float('nan')

        # Log all available strikes
        available_strikes = [detail.contract.strike for detail in option_chain if detail.contract.lastTradeDateOrContractMonth == expiry]
        print(f"Info: Available strikes for {contract.symbol} on {exchange}, expiry {expiry}: {available_strikes}")

        # Find the closest strike
        closest_strike = None
        min_difference = float('inf')

        for detail in option_chain:
            opt_contract = detail.contract
            if opt_contract.lastTradeDateOrContractMonth != expiry:
                continue

            if opt_contract.strike is None or math.isnan(opt_contract.strike):
                continue

            # Calculate the difference and find the closest strike
            difference = abs(opt_contract.strike - price)
            if difference < min_difference:
                min_difference = difference
                closest_strike = opt_contract.strike

        if closest_strike is not None:
            print(f"Info: Closest strike for {right} is {closest_strike}")
            return closest_strike
        else:
            print(f"Warning: No matching strike found for price {price}, right {right}.")
            return float('nan')
    except Exception as e:
        print(f"Error: Error fetching closest strike: {e}")
        return float('nan')

def get_today_expiry():
    print(f"Entering function: get_today_expiry")
    return datetime.today().strftime('%Y%m%d')


def get_atm_strike(qualified_contract, exchange, opt_exchange, expiry, current_price, secType):
    print(f"Entering function: get_atm_strike with parameters: {locals()}")
    try:
        option_contract = Contract()
        option_contract.symbol = qualified_contract.symbol
        option_contract.secType = secType
        option_contract.exchange = exchange
        option_contract.currency = qualified_contract.currency
        option_contract.lastTradeDateOrContractMonth = expiry

        option_details = ib.reqContractDetails(option_contract)
        if not option_details:
            print("Warning: No options found for the given expiry.")
            return float('nan')

        closest_strike = None
        min_difference = float('inf')

        for detail in option_details:
            strike = detail.contract.strike
            difference = abs(strike - current_price)
            if difference < min_difference:
                min_difference = difference
                closest_strike = strike

        if closest_strike is not None:
            print(f"Info: Closest ATM strike for price {current_price} is {closest_strike}")
            return closest_strike
        else:
            print("Warning: No ATM strike found.")
            return float('nan')
    except Exception as e:
        print(f"Error: Error fetching ATM strike: {e}")
        return float('nan')


def get_option_by_target_price(und_contract, right, opt_exchange, expiry, target_price, atm_strike):
    print(f"Entering function: get_option_by_target_price with parameters: {locals()}")
    try:
        chains = ib.reqSecDefOptParams(
            und_contract.symbol, '', und_contract.secType, und_contract.conId)
        print(f"Info: Option chains retrieved: {chains}")
    except Exception as e:
        print(f"Error: Error retrieving option chains: {e}")
        return None, None

    all_strikes = set()
    trading_classes = set()
    for chain in chains:
        if expiry in chain.expirations:
            if right == 'P':
                all_strikes.update([strike for strike in chain.strikes if strike <= atm_strike])
            elif right == 'C':
                all_strikes.update([strike for strike in chain.strikes if strike >= atm_strike])
            trading_classes.add(chain.tradingClass)

    if not all_strikes:
        print("Warning: No strikes found for the given expiry and ATM filtering.")
        return None, None

    strikes = sorted(all_strikes)
    contracts = []
    for strike in strikes:
        for trading_class in trading_classes:
            option = Option(
                symbol=und_contract.symbol,
                lastTradeDateOrContractMonth=expiry,
                strike=strike,
                right=right,
                exchange=opt_exchange,
                currency=und_contract.currency,
                tradingClass=trading_class)
            contracts.append(option)
    print(f"Info: Created {len(contracts)} option contracts with right '{right}' and filtered strikes.")

    qualified_contracts = ib.qualifyContracts(*contracts)

    if not qualified_contracts:
        print("Warning: No qualified contracts found.")
        return None, None

    tickers = ib.reqTickers(*qualified_contracts)
    ib.sleep(2)

    valid_options = []
    for ticker in tickers:
        if right == 'P' and ticker.ask != float('inf') and ticker.ask > 0:
            valid_options.append((ticker.contract, ticker.ask))
        elif right == 'C' and ticker.bid != float('inf') and ticker.bid > 0:
            valid_options.append((ticker.contract, ticker.bid))

    if not valid_options:
        print("Warning: No options with valid ask/bid prices found.")
        return None, None

    if right == 'P':
        min_diff = min(abs(ask - target_price) for _, ask in valid_options)
        closest_options = [(contract, ask) for contract, ask in valid_options if abs(ask - target_price) == min_diff]
    else:
        min_diff = min(abs(bid - target_price) for _, bid in valid_options)
        closest_options = [(contract, bid) for contract, bid in valid_options if abs(bid - target_price) == min_diff]

    print(f"Info: Options with minimum price difference: {closest_options}")

    if right == 'P':
        closest_options.sort(key=lambda x: x[0].strike, reverse=True)
    else:
        closest_options.sort(key=lambda x: x[0].strike, reverse=False)

    selected_option = closest_options[0][0]
    selected_price = closest_options[0][1]

    print(f"Info: Option closest to target price found: {selected_option} with bid/ask price {selected_price}")

    return selected_option, selected_price

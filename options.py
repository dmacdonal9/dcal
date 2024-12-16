from datetime import datetime
from ib_insync import Contract, Option, Ticker,FuturesOption
from ib_instance import ib
import math
import logging

logging.getLogger('ib_insync').setLevel(logging.ERROR)

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

        option_chain = ib.reqContractDetails(option_contract)
        if not option_chain:
            print("Warning: No options found for the specified parameters.")
            return float('nan')

        option_contracts = [detail.contract for detail in option_chain]
        tickers = ib.reqTickers(*option_contracts)

        closest_strike = None
        min_difference = float('inf')

        for contract, ticker in zip(option_contracts, tickers):
            bid_price = ticker.bid
            if bid_price is None or math.isnan(bid_price):
                continue

            strike = contract.strike
            difference = abs(strike - price)
            if difference < min_difference:
                min_difference = difference
                closest_strike = strike

        if closest_strike is not None:
            print(f"Info: Closest strike for price {price} and right {right} is {closest_strike}")
            return closest_strike
        else:
            print("Warning: No matching strike found with valid bid prices.")
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


def get_option_by_target_price(und_contract, right, opt_exchange, expiry, multiplier, target_price, atm_strike):
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
            if und_contract.secType == 'FUT':
                option = FuturesOption(
                    symbol=und_contract.symbol,
                    strike=strike,
                    lastTradeDateOrContractMonth=expiry,
                    right=right,
                    currency='USD',
                    multiplier=multiplier,
                    exchange=opt_exchange
                )
            else:
                option = Option(
                    symbol=und_contract.symbol,
                    lastTradeDateOrContractMonth=expiry,
                    strike=strike,
                    right=right,
                    exchange=opt_exchange,
                    currency=und_contract.currency,
                    tradingClass=trading_class
                )
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


def find_option_closest_to_delta(tickers, right, target_delta):
    #print(f"Entering function: fetch_option_chain with parameters: {locals()}")

    options = [option for option in tickers if option.contract.right == right and option.modelGreeks is not None]
    print("find_option_closest_to_delta(): ", right, target_delta)

    if not options:
        print(f"find_option_closest_to_delta(): nothing found close to delta {target_delta}")
        return None

    # Select the option closest to the target delta (absolute difference, adjusted for puts)
    closest_option = min(options, key=lambda x: abs(abs(x.modelGreeks.delta * 100) - target_delta), default=None)

    if closest_option:
        print(
            f"find_option_closest_to_delta(): closest option strike is {closest_option.contract.strike} with delta {closest_option.modelGreeks.delta}")
    else:
        print("No options found close to the target delta.")

    return closest_option


def fetch_option_chain(my_contract, my_expiry: str, last_price: float) -> list[Ticker]:
    print(f"Entering function: fetch_option_chain with parameters: {locals()}")

    chains = ib.reqSecDefOptParams(my_contract.symbol, my_contract.exchange if my_contract.secType=='FUT' else '', my_contract.secType, my_contract.conId)

    # Filter chain for the specific expiry
    expiry_chain = next((chain for chain in chains if my_expiry in chain.expirations), None)

    if not expiry_chain:
        raise ValueError(f"Expiry {my_expiry} not found in chain.")

    print(f"fetch_option_chain(): found expiry for {my_expiry}")

    # Filter strikes based on last_price
    relevant_put_strikes = [strike for strike in expiry_chain.strikes if strike < last_price]
    relevant_call_strikes = [strike for strike in expiry_chain.strikes if strike > last_price]

    option_contracts = []

    # Process relevant put strikes
    for strike in relevant_put_strikes:
        if my_contract.secType=='FUT':
            put_option_contract = FuturesOption(
                symbol=my_contract.symbol,
                strike=strike,
                lastTradeDateOrContractMonth=my_expiry,
                right='P',
                currency='USD',
                multiplier=my_contract.multiplier,
                exchange=my_contract.exchange
            )
        else:
            put_option_contract = Option(
                symbol=my_contract.symbol,
                strike=strike,
                lastTradeDateOrContractMonth=my_expiry,
                right='P',
                currency='USD',
                exchange=my_contract.exchange
            )
        option_contracts.append(put_option_contract)

    # Process relevant call strikes
    for strike in relevant_call_strikes:
        if my_contract.secType=='FUT':
            call_option_contract = FuturesOption(
                symbol=my_contract.symbol,
                strike=strike,
                lastTradeDateOrContractMonth=my_expiry,
                right='C',
                currency='USD',
                multiplier=my_contract.multiplier,
                exchange=my_contract.exchange
            )
        else:
            call_option_contract = Option(
                symbol=my_contract.symbol,
                strike=strike,
                lastTradeDateOrContractMonth=my_expiry,
                right='C',
                currency='USD',
                exchange=my_contract.exchange
            )
        option_contracts.append(call_option_contract)

    # Qualify contracts with error handling
    try:
        qualified_contracts = ib.qualifyContracts(*option_contracts)
    except Exception as e:
        if 'error code 200' in str(e).lower():
            print(f"Error 200 encountered while qualifying contracts: {str(e)}. Discarding invalid contracts.")
            qualified_contracts = []  # Fallback to an empty list if necessary
        else:
            raise  # Reraise other exceptions

    if not qualified_contracts:
        print("No valid contracts qualified.")
        return []

    # Fetch tickers with retries
    for attempt in range(3):  # Allow 3 attempts
        try:
            tickers = ib.reqTickers(*qualified_contracts)
            if all(ticker.modelGreeks is None for ticker in tickers):
                raise Exception("All modelGreeks are None")
            break  # Exit loop if no exception occurs
        except Exception as e:
            if attempt < 2:  # Retry for the first two attempts
                print(f"fetch_option_chain(): problem getting tickers, retrying...")
                ib.sleep(2)
            else:  # On final failure
                print(f"Error: Unable to obtain modelGreeks for all tickers after three attempts: {str(e)}")
                tickers = []  # Return an empty list if retries fail
                break

    return tickers

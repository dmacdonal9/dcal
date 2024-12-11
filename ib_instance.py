from ib_insync import IB
import time
import cfg

# Initialize IB instance
ib = IB()

# Variables for retry mechanism
max_retries = 5  # Maximum number of retries if the connection fails
retry_interval = 2  # Time (in seconds) to wait between retries


def connect_to_ib(is_test=False):
    """Connect to IBKR using the appropriate configuration."""
    host = cfg.test_ib_host if is_test else cfg.ib_host
    port = cfg.test_ib_port if is_test else cfg.ib_port
    clientid = cfg.test_ib_clientid if is_test else cfg.ib_clientid

    # Try to connect
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to connect to Interactive Brokers on port {port}...")
            ib.connect(host, port, clientid, readonly=False)
            print(f"Successfully connected to {'Test' if is_test else 'Live'} Interactive Brokers!")
            return ib
        except Exception as e:
            print(f"Failed to connect to Interactive Brokers on attempt {attempt + 1}. Error: {str(e)}")
            if attempt < max_retries - 1:  # No need to sleep on the last attempt
                time.sleep(retry_interval)

    raise RuntimeError(f"Unable to connect to {'Test' if is_test else 'Live'} Interactive Brokers after {max_retries} attempts.")
from ib_insync import IB
import time
import cfg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('IBConnection')

# Initialize IB instance
ib = IB()

# Variables for retry mechanism
MAX_RETRIES = 5  # Maximum number of retries if the connection fails
RETRY_INTERVAL = 2  # Time (in seconds) to wait between retries


def connect_to_ib(is_test=False):
    """
    Connect to Interactive Brokers using the appropriate configuration.

    Args:
        is_test (bool): Whether to connect to the test environment (paper trading).

    Returns:
        IB: An instance of the IB connection.

    Raises:
        RuntimeError: If the connection cannot be established after the maximum retries.
    """
    # Select connection parameters
    host = cfg.test_ib_host if is_test else cfg.ib_host
    port = cfg.test_ib_port if is_test else cfg.ib_port
    clientid = cfg.test_ib_clientid if is_test else cfg.ib_clientid

    # Attempt to connect with retries
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Attempt {attempt + 1} to connect to {'Test' if is_test else 'Live'} Interactive Brokers...")
            ib.connect(host, port, clientid, readonly=False)
            logger.info(f"Successfully connected to {'Test' if is_test else 'Live'} Interactive Brokers!")
            return ib
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:  # No need to sleep on the last attempt
                time.sleep(RETRY_INTERVAL)

    # Raise an error if unable to connect after retries
    raise RuntimeError(f"Unable to connect to {'Test' if is_test else 'Live'} Interactive Brokers after {MAX_RETRIES} attempts.")
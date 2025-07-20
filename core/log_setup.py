import logging
import os
from datetime import datetime
from config import AppConfig

def setup_logging():
    """
    Configures the root logger to output to both console and a timestamped file.
    """
    if not AppConfig:
        print("Cannot setup logging, config not loaded.")
        return

    # Create a unique log file name with a timestamp
    log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_filepath = os.path.join(AppConfig.LOGS_PATH, log_filename)

    # Define the logging format
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s')

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if this function is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- File Handler ---
    # Writes logs to the file
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # --- Console Handler ---
    # Writes logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    logging.info("Logging configured successfully. Output will be saved to %s", log_filepath)


import logging
import os
from logging.handlers import RotatingFileHandler

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True) # Create log directory if it doesn't exist

def setup_logger(name: str, log_file= 'logs.log', level=logging.INFO):
    """ 
        What it does : A function to setup a logger with a specific name and log file
        What ir returns : Returns a logger object that is stored in the logs directory
        Parameters:
            name (str): Name of the file it is logging for and being excecuted in
            log_file (str): Name of the log file
            level (int): Logging level (default is logging.INFO)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent propagation to the root logger
    
    if not logger.hasHandlers():
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s — %(name)s — %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Stream handler for console output
        # Activate this if you want console output
        # ch = logging.StreamHandler()
        # ch.setLevel(level)
        # ch.setFormatter(formatter)
        # logger.addHandler(ch)
        
        # File handler with rotation
        fh = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=1_000_000, backupCount=5)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger




logging.info("Logger setup complete. Logs will be stored in: %s", log_dir)


        
        
    
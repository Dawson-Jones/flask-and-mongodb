import logging.handlers
from concurrent_log_handler import ConcurrentRotatingFileHandler


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
standard_format = '%(asctime)s - %(threadName)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
handler_format = logging.Formatter(standard_format, datefmt="%Y-%m-%d %H:%M:%S")
# logs file
logfile = ConcurrentRotatingFileHandler('log', maxBytes=1024 * 1024 * 5, backupCount=1)
logfile.setLevel(logging.INFO)
logfile.setFormatter(handler_format)
logger.addHandler(logfile)
# console output handler
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(handler_format)
logger.addHandler(console)

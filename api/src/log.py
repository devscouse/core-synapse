import logging

def logging_config():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(logging.StreamHandler())


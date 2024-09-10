import json
import logging
import datetime

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.datetime.now().isoformat(),  # Current time in ISO format
            'message': record.getMessage(),
            'target': record.target,
            'action': record.action,
            'outcome': record.outcome
        }
        return json.dumps(log_record)
    

def setup_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs to a specified file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create a custom JSON formatter
    formatter = JsonLogFormatter('%(asctime)s')

    # Add the formatter to the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

# Define a function to add custom fields to the log record
def log_with_custom_fields(logger, msg, target, action, outcome):
    extra = {
        'target': target,
        'action': action,
        'outcome': outcome
    }
    logger.info(msg, extra=extra)
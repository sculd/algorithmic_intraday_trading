from google.cloud import logging
import logging as python_logging

LOG_NAME = 'us_intraday_trading'

_client = None
log_to_std = False

def set_log_name(log_name):
    global LOG_NAME
    LOG_NAME = log_name

def get_log_name():
    return LOG_NAME

def _get_client():
    global _client
    if _client is None:
        _client = logging.Client()
    return _client

def get_logger(log_name=LOG_NAME):
    return _get_client().logger(log_name)

def _print_with_severity_prefix(severity, text):
    print('{severity}: {text}'.format(severity=severity, text=text))

def _log_print_with_severity(severity, text):
    _print_with_severity_prefix(severity, text)
    if log_to_std:
        if severity == 'DEBUG':
            python_logging.debug(text)
        else:
            python_logging.info(text)
    else:
        log_name = get_log_name()
        if not log_name:
            return
        logger = get_logger(log_name=log_name)
        logger.log_text(text, severity=severity)

def debug(*messages):
    text = ', '.join(list(map(lambda m: str(m), messages)))
    _log_print_with_severity('DEBUG', text)

def info(*messages):
    text = ', '.join(list(map(lambda m: str(m), messages)))
    _log_print_with_severity('INFO', text)

def error(*messages):
    text = ', '.join(list(map(lambda m: str(m), messages)))
    _log_print_with_severity('ERROR', text)

def warning(*messages):
    text = ', '.join(list(map(lambda m: str(m), messages)))
    _log_print_with_severity('WARNING', text)

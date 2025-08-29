
import logging
import os
import sys

import structlog


def get_logger(logger_name=None):

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    log_env = os.environ.get('LogLevel', 'INFO')
    if log_env not in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
        msg = f'Value {log_env} is not a valid log level'
        raise ValueError(msg)

    if logger_name:
        log = structlog.get_logger(logger_name)
    else:
        default_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'no_name_available')
        log = structlog.get_logger(default_name)

    # list out the loggers that will be set to Error level at all times.
    loggers_to_supress = {
        'boto3': 'ERROR',
        'botocore': 'ERROR',
        's3transfer': 'ERROR',
        'requests': 'ERROR',
        'urllib3': 'ERROR',
    }

    supress_loggers(loggers_to_supress)

    log.setLevel(log_env)
    return log


def supress_loggers(logger_dict):

    for logger, level in logger_dict.items():
        setup_logger = logging.getLogger(logger)
        setup_logger.setLevel(level.upper())
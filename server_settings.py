import logging.config
import os
from datetime import datetime
from libra import check_dir


check_dir('server_logs')
logname = os.path.join('archive', 'server_logs', 'server_log_' + datetime.today().strftime('%Y_%m_%d') + '.txt')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s %(name)s] %(message)s'
        },
        'uvicorn_formatter': {
            'format': '[%(levelname)s:%(asctime)s %(module)s] %(message)s'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default_formatter',
        },
        'file_handler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': logname,
            'formatter': 'default_formatter',
        },
        'stream_handler_uvicorn': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'uvicorn_formatter',
        },
        'file_handler_uvicorn': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': logname,
            'formatter': 'uvicorn_formatter',
        },
    },

    'loggers': {
        "uvicorn.access": {
            "name": "uvicorn",
            "handlers": ["stream_handler_uvicorn", "file_handler_uvicorn"],
            "level": "DEBUG",
            "propagate": True,
        },
        "uvicorn.error": {
            "name": "uvicorn",
            "handlers": ["stream_handler_uvicorn", "file_handler_uvicorn"],
            "level": "DEBUG",
            "propagate": True,
        },
        "api": {
            "handlers": ["stream_handler", "file_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
        "monitoring": {
            "handlers": ["stream_handler", "file_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
        "rinex_merger": {
            "handlers": ["stream_handler", "file_handler"],
            "level": "DEBUG",
            "propagate": True,
        }
    }
}

# if __name__ == "__main__":

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

    # logger.info("this is a test")
    # logger.error("this is a warning")
    # logger.critical("this is a critical error")
    # logger.debug("debuging")
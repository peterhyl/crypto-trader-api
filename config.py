import os

HEADERS = {'Content-Type': 'application/json'}
LOG_DIR = "/var/log/backend"
ENVIRONMENT = os.environ.get('FLASK_ENV', 'dev')


if ENVIRONMENT not in ['dev', 'test', 'prod']:
    raise ValueError(f"System variable: FLASK_ENV has bad value: {ENVIRONMENT}. "
                     "Possible values: dev, test, prod")

debug_log_config = {
    'version': 1,
    'formatters': {
        'default': {'format': '%(levelname)-5s %(asctime)s %(name)s %(thread)-5d %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'}
    },
    'handlers': {
        'file_handler': {
            'class': "logging.handlers.RotatingFileHandler",
            'level': "DEBUG",
            'formatter': 'default',
            'filename': os.path.join(LOG_DIR, "debug.log"),
            'backupCount': 7,
        },
        'stdout': {  # easier logging into Docker
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['file_handler', 'stdout']
        }
    },
    'disable_existing_loggers': False
}

info_log_config = {
    'version': 1,
    'formatters': {
        'default': {'format': '%(levelname)-5s %(asctime)s %(name)s %(thread)-5d %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'}
    },
    'handlers': {
        'file_handler': {
            'class': "logging.handlers.RotatingFileHandler",
            'level': "INFO",
            'formatter': 'default',
            'filename': os.path.join(LOG_DIR, "info.log"),
            'backupCount': 7,
        },
        'stdout': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['file_handler', 'stdout']
        }
    },
    'disable_existing_loggers': False
}


class Config(object):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_DOMAIN = False
    SECRET_KEY = 0xd153af67e2b2bfa4b98d3045
    RESTPLUS_MASK_SWAGGER = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    SERVER_NAME = "0.0.0.0:5000"
    LOG_CONFIG = info_log_config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME = "0.0.0.0:5050"
    LOG_CONFIG = debug_log_config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME = "0.0.0.0:5001"
    LOG_CONFIG = debug_log_config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', "sqlite:///")


config_by_env = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}[ENVIRONMENT]

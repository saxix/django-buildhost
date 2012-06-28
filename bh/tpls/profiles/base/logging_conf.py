
import os

file_handler = lambda name, level: {'level': level, 'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'verbose',
                                    'filename': os.path.join(os.environ['PASPORT_LOGDIR'], '%s.log' % name),
                                    }
"""
pendig_records
contracts
tracer.pasport.contract
"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'full': {
            'format': '%(levelname)-8s: %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'verbose': {
            'format': '%(levelname)-8s: %(asctime)s %(name)20s %(message)s'
        },
        'simple': {
            'format': '%(levelname)-8s %(asctime)s %(name)20s %(funcName)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler'
        },
        'error': file_handler('errors', 'DEBUG'),
        'security': file_handler('security', 'DEBUG'),
        'interface': file_handler('interface', 'DEBUG'),
        'root': file_handler('messages', 'DEBUG'),
        'payroll': file_handler('payroll', 'DEBUG'),
        'pendig_records': file_handler('pendig_records', 'DEBUG'),
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        '': {
            'handlers': ['root', ],
            'propagate': True,
            'level': 'DEBUG'
        },
        'tracer.': {
            'handlers': ['root'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'kiowa.models': {'handlers': ['root'], 'propagate': False, 'level': 'CRITICAL'},
        'commands.*': {'handlers': ['root'], 'propagate': False, 'level': 'CRITICAL'},
        'sessions.models': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'error': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True
        },
        'security_risk': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True
        },
        'security': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False
        },
        'root': {
            'handlers': ['root', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'interface': {
            'handlers': ['interface'],
            'level': 'ERROR',
            'propagate': True
        },
        'payroll': {
            'handlers': ['payroll'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

LOGGING_DEBUG = {'version': 1,
                 'disable_existing_loggers': True,
                 }
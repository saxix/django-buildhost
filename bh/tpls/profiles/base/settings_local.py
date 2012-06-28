#{% block content %}
from pasportng.ng.settings import *
#{% block header %}#{% endblock header %}

#{% block debug %}
DEBUG = TEMPLATE_DEBUG = True
#{% endblock debug %}

MAINTENANCE_FILE="{{base}}/var/run/MAINTENANCE"

#{% block email %}
# Email config
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = '10.11.32.71'
EMAIL_PORT          = '25'
EMAIL_NOTIFY_CONTRACT_EMPLOYEE = False # if true updtaes to contract will be nofied to the contract's owner too
EMAIL_SUBJECT_PREFIX = '[Pasport] Base'
EMAIL_FAKE_RECIPIENTS= DEBUG_EMAIL_TO = [ "Praphatsorn.Lertkotchakorn@wfp.org", "isariyaporn.banlusilp@wfp.org",]
#{% endblock email %}

STATIC_ROOT="{{base}}/var/www/static"
MEDIA_ROOT="{{base}}/var/www/media"

#{% block database %}
DATABASES = {
    'default': {
        'NAME': '{{base}}/var/PASPORT.db',
        'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'USER': '',
        'PASSWORD': '',
    },
    'interface': {
        'NAME': '{{base}}/var/INTERFACE.db',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
    }
}
#{% endblock database %}

PASPORT_LOGDIR = "{{base}}/logs/pasport"
try:
    from django.utils.dictconfig import dictConfig
    os.environ['PASPORT_LOGDIR'] = PASPORT_LOGDIR
    from logging_conf import LOGGING
    dictConfig(LOGGING)
except ValueError:
    pass

#{% endblock content %}

#{% block footer %}
#{% endblock footer %}
